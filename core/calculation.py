"""Calculation engine for cash memos / invoices. All Decimal, validated."""
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP, ROUND_DOWN, ROUND_UP
from typing import List
from .money import D, q2

HUNDRED = Decimal("100")


class CalculationError(ValueError):
    pass


@dataclass
class LineItem:
    quantity: Decimal
    unit_price: Decimal
    discount_type: str = "fixed"      # "fixed" | "percent"
    discount_value: Decimal = Decimal("0")

    def __post_init__(self):
        self.quantity = D(self.quantity)
        self.unit_price = D(self.unit_price)
        self.discount_value = D(self.discount_value)
        if self.quantity < 0:
            raise CalculationError("quantity cannot be negative")
        if self.unit_price < 0:
            raise CalculationError("unit price cannot be negative")
        if self.discount_value < 0:
            raise CalculationError("discount cannot be negative")
        if self.discount_type not in ("fixed", "percent"):
            raise CalculationError("discount_type must be 'fixed' or 'percent'")
        if self.discount_type == "percent" and self.discount_value > HUNDRED:
            raise CalculationError("percent discount cannot exceed 100")


@dataclass
class Adjustments:
    discount_type: str = "percent"     # overall discount: "percent" | "fixed"
    discount_value: Decimal = Decimal("0")
    vat_percent: Decimal = Decimal("0")
    tax_percent: Decimal = Decimal("0")
    vat_mode: str = "after_discount"   # or "before_discount"
    delivery: Decimal = Decimal("0")
    service: Decimal = Decimal("0")
    other_charges: Decimal = Decimal("0")
    paid: Decimal = Decimal("0")
    previous_due: Decimal = Decimal("0")
    rounding: str = "none"             # none | nearest | up | down (to whole taka)

    def __post_init__(self):
        for name in ("discount_value", "vat_percent", "tax_percent", "delivery",
                     "service", "other_charges", "paid", "previous_due"):
            setattr(self, name, D(getattr(self, name)))
            if getattr(self, name) < 0:
                raise CalculationError(f"{name} cannot be negative")
        if self.discount_type not in ("fixed", "percent"):
            raise CalculationError("discount_type must be 'fixed' or 'percent'")
        if self.vat_mode not in ("after_discount", "before_discount"):
            raise CalculationError("invalid vat_mode")
        if self.rounding not in ("none", "nearest", "up", "down"):
            raise CalculationError("invalid rounding")
        if self.discount_type == "percent" and self.discount_value > HUNDRED:
            raise CalculationError("percent discount cannot exceed 100")


@dataclass
class Totals:
    line_totals: List[Decimal] = field(default_factory=list)
    line_discounts: List[Decimal] = field(default_factory=list)
    gross: Decimal = Decimal("0")
    item_discount_total: Decimal = Decimal("0")
    subtotal: Decimal = Decimal("0")
    overall_discount: Decimal = Decimal("0")
    vat: Decimal = Decimal("0")
    tax: Decimal = Decimal("0")
    delivery: Decimal = Decimal("0")
    service: Decimal = Decimal("0")
    other_charges: Decimal = Decimal("0")
    rounding_adjustment: Decimal = Decimal("0")
    grand_total: Decimal = Decimal("0")
    previous_due: Decimal = Decimal("0")
    paid: Decimal = Decimal("0")
    current_due: Decimal = Decimal("0")
    change_due: Decimal = Decimal("0")

    def as_strings(self) -> dict:
        out = {}
        for k, v in self.__dict__.items():
            out[k] = [str(x) for x in v] if isinstance(v, list) else str(v)
        return out


_ROUND = {"nearest": ROUND_HALF_UP, "up": ROUND_UP, "down": ROUND_DOWN}


def calculate(items: List[LineItem], adj: Adjustments = None) -> Totals:
    adj = adj or Adjustments()
    t = Totals()
    for it in items:
        gross = q2(it.quantity * it.unit_price)
        if it.discount_type == "percent":
            disc = q2(gross * it.discount_value / HUNDRED)
        else:
            disc = min(q2(it.discount_value), gross)
        t.line_discounts.append(disc)
        t.line_totals.append(gross - disc)
        t.gross += gross
        t.item_discount_total += disc
    t.subtotal = sum(t.line_totals, Decimal("0"))

    if adj.discount_type == "percent":
        t.overall_discount = q2(t.subtotal * adj.discount_value / HUNDRED)
    else:
        t.overall_discount = min(q2(adj.discount_value), t.subtotal)

    base = t.subtotal - t.overall_discount if adj.vat_mode == "after_discount" else t.subtotal
    t.vat = q2(base * adj.vat_percent / HUNDRED)
    t.tax = q2(base * adj.tax_percent / HUNDRED)
    t.delivery, t.service, t.other_charges = q2(adj.delivery), q2(adj.service), q2(adj.other_charges)

    before = (t.subtotal - t.overall_discount + t.vat + t.tax
              + t.delivery + t.service + t.other_charges)
    if adj.rounding == "none":
        t.grand_total = before
    else:
        t.grand_total = before.quantize(Decimal("1"), rounding=_ROUND[adj.rounding])
    t.rounding_adjustment = t.grand_total - before

    t.previous_due, t.paid = q2(adj.previous_due), q2(adj.paid)
    owed = t.grand_total + t.previous_due
    t.current_due = max(owed - t.paid, Decimal("0"))
    t.change_due = max(t.paid - owed, Decimal("0"))
    return t
