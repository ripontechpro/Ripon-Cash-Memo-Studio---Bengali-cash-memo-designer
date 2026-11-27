"""Create/revise cash memos: validate -> calculate -> store in one transaction."""
from decimal import Decimal
from core.calculation import LineItem, Adjustments, calculate, CalculationError
from core.money import D


def _items(rows):
    items = []
    for r in rows:
        if not str(r.get("name", "")).strip():
            continue
        items.append(LineItem(r.get("qty", "0"), r.get("price", "0"), r.get("disc_type", "fixed"), r.get("disc_value", "0")))
    if not items:
        raise CalculationError("add at least one product row")
    return items


def build(rows, adjustments=None):
    valid = [r for r in rows if str(r.get("name", "")).strip()]
    totals = calculate(_items(rows), Adjustments(**(adjustments or {})))
    lines = [{"sn": i + 1, "name": r["name"], "description": r.get("description", ""), "qty": str(D(r.get("qty"))),
              "unit": r.get("unit", "Pcs"), "price": str(D(r.get("price"))),
              "discount": str(totals.line_discounts[i]), "total": str(totals.line_totals[i])}
             for i, r in enumerate(valid)]
    return totals, {"items": lines, "totals": totals.as_strings(), "adjustments": {k: str(v) for k, v in (adjustments or {}).items()}}


def issue_memo(db, rows, adjustments=None, customer=None, payment_method="Cash", template_id=None, doc_type="cash_memo"):
    totals, payload = build(rows, adjustments)
    tracked = []
    for r in rows:
        pid = r.get("product_id")
        if pid:
            tracked.append((pid, D(r.get("qty"))))

    def decrement(conn):
        for pid, qty in tracked:
            row = conn.execute("SELECT stock,track_stock FROM products WHERE id=?", (pid,)).fetchone()
            if row and row["track_stock"]:
                new = D(row["stock"]) - qty
                if new < 0:
                    raise CalculationError("insufficient stock")
                conn.execute("UPDATE products SET stock=? WHERE id=?", (str(new), pid))

    doc_id, number = db.issue_document(doc_type, totals, payload, customer, payment_method, template_id, extra=decrement)
    payload["number"] = number
    return doc_id, number, totals, payload
