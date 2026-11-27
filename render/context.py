"""Turn business settings + a stored document into the flat text context the layout engine needs."""
import json
from core.formatting import format_amount, BN_DIGITS

TOTAL_KEYS = ["subtotal", "overall_discount", "vat", "tax", "delivery", "service", "other_charges",
              "rounding_adjustment", "grand_total", "previous_due", "paid", "current_due"]


def make_context(business, doc_row=None, payload=None, bangla=False):
    """business: dict (business_name, business_subtitle, address, phone, email, terms, thank_you ...)
    doc_row: sqlite row/dict of a document (optional, for preview use sample data)."""
    payload = payload if payload is not None else json.loads(doc_row["payload"])
    fa = lambda v: format_amount(v, bangla=bangla)
    ctx = dict(business)
    if doc_row is not None:
        issued = doc_row["issued_at"]
        ctx.update(memo_number=doc_row["number"], date=issued[:10], time=issued[11:16],
                   customer_name=doc_row["customer_name"] or "", customer_phone=doc_row["customer_phone"] or "",
                   customer_address=doc_row["customer_address"] or "")
        try: ctx["payment_method"] = doc_row["payment_method"]
        except (KeyError, IndexError): pass
    t = payload["totals"]
    for k in TOTAL_KEYS:
        ctx[k] = fa(t.get(k, "0"))
    ctx["due"] = ctx["current_due"]
    items = []
    for it in payload["items"]:
        row = dict(it)
        for k in ("price", "discount", "total"):
            row[k] = fa(it[k])
        row["sn"] = str(it["sn"])
        if bangla:
            row["sn"] = row["sn"].translate(BN_DIGITS)
            row["qty"] = it["qty"].translate(BN_DIGITS)
        items.append(row)
    ctx["items"] = items
    ctx["item_names"] = ", ".join(i["name"] for i in items)
    if bangla:
        for k in ("memo_number", "date", "time", "customer_phone"):
            if k in ctx: ctx[k] = str(ctx[k]).translate(BN_DIGITS)
    return ctx
