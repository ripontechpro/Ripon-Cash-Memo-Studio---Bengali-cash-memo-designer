"""Decimal-safe money helpers. Never use float for money."""
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

CENT = Decimal("0.01")


def D(value) -> Decimal:
    """Convert str/int/Decimal to Decimal. Floats are rejected on purpose."""
    if isinstance(value, float):
        raise TypeError("float not allowed for money; pass str or Decimal")
    if isinstance(value, Decimal):
        return value
    if value is None or (isinstance(value, str) and not value.strip()):
        return Decimal("0")
    try:
        return Decimal(str(value).strip().replace(",", ""))
    except InvalidOperation as exc:
        raise ValueError(f"invalid number: {value!r}") from exc


def q2(value: Decimal) -> Decimal:
    return value.quantize(CENT, rounding=ROUND_HALF_UP)
