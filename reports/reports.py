"""Sales reports (Decimal aggregation in Python, since money is stored as text)."""
import csv
import json
from collections import defaultdict
from decimal import Decimal
from core.money import D

Z = Decimal("0")
_FMT = {"day": 10, "month": 7, "year": 4}


def _docs(db, date_from=None, date_to=None):
    return db.search_documents(date_from=date_from, date_to=date_to, status="issued")


def sales_by_period(db, period="day", date_from=None, date_to=None):
    if period == "week":
        import datetime as dt
        key = lambda s: "%d-W%02d" % dt.date.fromisoformat(s[:10]).isocalendar()[:2]
    else:
        n = _FMT[period]; key = lambda s: s[:n]
    agg = defaultdict(lambda: [0, Z, Z, Z])
    for r in _docs(db, date_from, date_to):
        a = agg[key(r["issued_at"])]
        a[0] += 1; a[1] += D(r["grand_total"]); a[2] += D(r["paid"]); a[3] += D(r["due"])
    return [{"period": k, "count": v[0], "total": v[1], "paid": v[2], "due": v[3]} for k, v in sorted(agg.items())]


def by_customer(db, **kw):
    agg = defaultdict(lambda: [0, Z])
    for r in _docs(db, **kw):
        a = agg[r["customer_name"] or "Walk-in"]; a[0] += 1; a[1] += D(r["grand_total"])
    return [{"customer": k, "count": v[0], "total": v[1]} for k, v in sorted(agg.items(), key=lambda x: -x[1][1])]


def by_payment_method(db, **kw):
    agg = defaultdict(lambda: [0, Z])
    for r in _docs(db, **kw):
        a = agg[r["payment_method"]]; a[0] += 1; a[1] += D(r["paid"])
    return [{"method": k, "count": v[0], "paid": v[1]} for k, v in sorted(agg.items())]


def by_product(db, **kw):
    agg = defaultdict(lambda: [Z, Z])
    for r in _docs(db, **kw):
        for it in json.loads(r["payload"]).get("items", []):
            a = agg[it["name"]]; a[0] += D(it["qty"]); a[1] += D(it["total"])
    return [{"product": k, "qty": v[0], "total": v[1]} for k, v in sorted(agg.items(), key=lambda x: -x[1][1])]


def tax_and_discount(db, **kw):
    vat = disc = Z
    for r in _docs(db, **kw):
        t = json.loads(r["payload"]).get("totals", {})
        vat += D(t.get("vat")) + D(t.get("tax")); disc += D(t.get("overall_discount")) + D(t.get("item_discount_total"))
    return {"vat_and_tax": vat, "discount": disc}


def due_report(db):
    return [{"number": r["number"], "customer": r["customer_name"] or "Walk-in", "due": D(r["due"])}
            for r in _docs(db) if D(r["due"]) > 0]


def dashboard_stats(db, today):
    rows = _docs(db)
    return {"total_sales": sum((D(r["grand_total"]) for r in rows), Z),
            "today_sales": sum((D(r["grand_total"]) for r in rows if r["issued_at"].startswith(today)), Z),
            "invoices": len(rows), "paid": sum((D(r["paid"]) for r in rows), Z),
            "outstanding": sum((D(r["due"]) for r in rows), Z),
            "customers": db.conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0]}
