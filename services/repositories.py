"""CRUD services: customers, products, templates, settings."""
import csv
import json
from datetime import datetime
from decimal import Decimal
from core.money import D


class Settings:
    def __init__(self, db): self.db = db

    def get(self, key, default=None):
        r = self.db.conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
        return json.loads(r[0]) if r else default

    def set(self, key, value):
        with self.db.tx():
            self.db.conn.execute("INSERT OR REPLACE INTO settings VALUES(?,?)", (key, json.dumps(value, ensure_ascii=False)))


class Customers:
    def __init__(self, db): self.db = db

    def add(self, name, phone="", address=""):
        if not name.strip(): raise ValueError("customer name is required")
        with self.db.tx():
            return self.db.conn.execute("INSERT INTO customers(name,phone,address) VALUES(?,?,?)",
                                        (name.strip(), phone, address)).lastrowid

    def update(self, cid, name, phone="", address=""):
        if not name.strip(): raise ValueError("customer name is required")
        with self.db.tx():
            self.db.conn.execute("UPDATE customers SET name=?,phone=?,address=? WHERE id=?", (name.strip(), phone, address, cid))

    def delete(self, cid):
        with self.db.tx():  # documents keep their own customer snapshot
            self.db.conn.execute("UPDATE documents SET customer_id=NULL WHERE customer_id=?", (cid,))
            self.db.conn.execute("DELETE FROM customers WHERE id=?", (cid,))

    def search(self, text=""):
        like = f"%{text}%"
        return self.db.conn.execute("SELECT * FROM customers WHERE name LIKE ? OR phone LIKE ? ORDER BY name", (like, like)).fetchall()

    def summary(self, cid):
        total = paid = due = Decimal("0")
        rows = self.db.conn.execute("SELECT * FROM documents WHERE customer_id=? AND status='issued' ORDER BY id DESC", (cid,)).fetchall()
        for r in rows:
            total += D(r["grand_total"]); paid += D(r["paid"]); due += D(r["due"])
        return {"total_purchases": total, "paid": paid, "outstanding": due, "history": rows}


class Products:
    def __init__(self, db): self.db = db

    def add(self, name, selling_price="0", purchase_price="0", unit="Pcs", sku=None, barcode=None,
            category="", brand="", stock="0", low_stock_alert=None, track_stock=False):
        if not name.strip(): raise ValueError("product name is required")
        for v in (selling_price, purchase_price, stock):
            if D(v) < 0: raise ValueError("price/stock cannot be negative")
        with self.db.tx():
            return self.db.conn.execute(
                """INSERT INTO products(name,sku,barcode,category,brand,purchase_price,selling_price,unit,stock,low_stock_alert,track_stock)
                VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
                (name.strip(), sku or None, barcode, category, brand, str(D(purchase_price)), str(D(selling_price)),
                 unit, str(D(stock)), None if low_stock_alert is None else str(D(low_stock_alert)), int(track_stock))).lastrowid

    def update_price(self, pid, selling_price):
        if D(selling_price) < 0: raise ValueError("price cannot be negative")
        with self.db.tx():
            self.db.conn.execute("UPDATE products SET selling_price=? WHERE id=?", (str(D(selling_price)), pid))

    def delete(self, pid):
        with self.db.tx(): self.db.conn.execute("DELETE FROM products WHERE id=?", (pid,))

    def search(self, text="", limit=20):
        like = f"%{text}%"
        return self.db.conn.execute(
            "SELECT * FROM products WHERE name LIKE ? OR sku LIKE ? OR barcode LIKE ? ORDER BY name LIMIT ?",
            (like, like, like, limit)).fetchall()

    def low_stock(self):
        return [r for r in self.db.conn.execute("SELECT * FROM products WHERE track_stock=1 AND low_stock_alert IS NOT NULL")
                if D(r["stock"]) <= D(r["low_stock_alert"])]

    COLS = ["name", "sku", "barcode", "category", "brand", "purchase_price", "selling_price", "unit", "stock"]

    def export_csv(self, path):
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f); w.writerow(self.COLS)
            for r in self.db.conn.execute("SELECT * FROM products ORDER BY name"):
                w.writerow([r[c] for c in self.COLS])

    def import_csv(self, path):
        n = 0
        with open(path, newline="", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                if not (row.get("name") or "").strip(): continue
                self.add(row["name"], row.get("selling_price") or "0", row.get("purchase_price") or "0",
                         row.get("unit") or "Pcs", row.get("sku") or None, row.get("barcode"),
                         row.get("category") or "", row.get("brand") or "", row.get("stock") or "0")
                n += 1
        return n


class Templates:
    def __init__(self, db): self.db = db

    def save(self, name, definition, template_id=None, doc_type="cash_memo"):
        now = datetime.now().isoformat(timespec="seconds")
        data = json.dumps(definition, ensure_ascii=False)
        with self.db.tx():
            if template_id:
                self.db.conn.execute("UPDATE templates SET name=?,definition=?,updated_at=? WHERE id=?", (name, data, now, template_id))
                return template_id
            return self.db.conn.execute("INSERT INTO templates(name,doc_type,definition,updated_at) VALUES(?,?,?,?)",
                                        (name, doc_type, data, now)).lastrowid

    def get(self, tid):
        r = self.db.conn.execute("SELECT * FROM templates WHERE id=?", (tid,)).fetchone()
        return (r["name"], json.loads(r["definition"])) if r else None

    def list(self):
        return self.db.conn.execute("SELECT id,name,doc_type,updated_at FROM templates ORDER BY name").fetchall()

    def duplicate(self, tid):
        name, d = self.get(tid)
        return self.save(f"{name} (Copy)", d)

    def delete(self, tid):
        with self.db.tx(): self.db.conn.execute("DELETE FROM templates WHERE id=?", (tid,))
