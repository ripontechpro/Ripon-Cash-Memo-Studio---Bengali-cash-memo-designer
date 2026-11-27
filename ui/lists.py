from .i18n import T
import json
from datetime import date
from PySide6.QtWidgets import QDateEdit, QDialog, QDialogButtonBox, QFileDialog, QFormLayout, QHBoxLayout, QInputDialog, QVBoxLayout, QWidget, QLabel
from .w import QLineEdit, QComboBox
from core.constants import PAYMENT_BN, STATUS_BN
from PySide6.QtCore import QDate
from core.formatting import format_amount
from core.money import D
from services.memo_service import issue_memo
from .common import h1, button, table, fill_table, ask, error
from .preview import PreviewDialog, build_pages


class FormDialog(QDialog):
    def __init__(self, title, fields, values=None, parent=None):
        super().__init__(parent); self.setWindowTitle(title); f = QFormLayout(self); self.w = {}
        for key, label in fields:
            e = QLineEdit((values or {}).get(key, "") or ""); self.w[key] = e; f.addRow(label, e)
        bb = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel); bb.accepted.connect(self.accept); bb.rejected.connect(self.reject); f.addRow(bb)

    def values(self): return {k: w.text().strip() for k, w in self.w.items()}


class CustomersPage(QWidget):
    def __init__(self, app):
        super().__init__(); self.setObjectName("page"); self.app = app; v = QVBoxLayout(self); v.addWidget(h1(T("গ্রাহক")))
        bar = QHBoxLayout(); self.q = QLineEdit(); self.q.setPlaceholderText(T("নাম বা ফোন দিয়ে খুঁজুন…")); self.q.textChanged.connect(self.refresh); bar.addWidget(self.q, 1)
        for t, s, sec in ((T("যোগ করুন"), self.add, False), (T("সম্পাদনা"), self.edit, True), (T("মুছুন"), self.delete, True), (T("ইতিহাস"), self.history, True)): bar.addWidget(button(t, s, sec))
        v.addLayout(bar); self.t = table(["ID", T("নাম"), T("ফোন"), T("ঠিকানা"), T("মোট কেনা"), T("পরিশোধিত"), T("বাকি")]); v.addWidget(self.t)

    def refresh(self):
        rows = []
        for c in self.app.customers.search(self.q.text()):
            s = self.app.customers.summary(c["id"])
            rows.append([c["id"], c["name"], c["phone"] or "", c["address"] or "", format_amount(s["total_purchases"]), format_amount(s["paid"]), format_amount(s["outstanding"])])
        fill_table(self.t, rows)

    def sel(self):
        r = self.t.currentRow(); return int(self.t.item(r, 0).text()) if r >= 0 else None

    FIELDS = [("name", T("নাম")), ("phone", T("ফোন")), ("address", T("ঠিকানা"))]

    def add(self):
        d = FormDialog(T("গ্রাহক যোগ করুন"), self.FIELDS, parent=self)
        if d.exec():
            try: self.app.customers.add(**d.values())
            except ValueError as e: return error(self, e)
            self.refresh()

    def edit(self):
        cid = self.sel()
        if not cid: return
        c = dict(next(x for x in self.app.customers.search("") if x["id"] == cid))
        d = FormDialog(T("গ্রাহক সম্পাদনা"), self.FIELDS, c, self)
        if d.exec():
            try: self.app.customers.update(cid, **d.values())
            except ValueError as e: return error(self, e)
            self.refresh()

    def delete(self):
        cid = self.sel()
        if cid and ask(self, T("মুছুন"), T("এই গ্রাহক মুছবেন? সংরক্ষিত মেমোতে গ্রাহকের নাম থেকে যাবে।")): self.app.customers.delete(cid); self.refresh()

    def history(self):
        cid = self.sel()
        if not cid: return
        s = self.app.customers.summary(cid); dlg = QDialog(self); dlg.setWindowTitle(T("গ্রাহকের ইতিহাস")); dlg.resize(640, 400); l = QVBoxLayout(dlg)
        t = table([T("মেমো"), T("তারিখ"), T("মোট"), T("পরিশোধিত"), T("বাকি")]); fill_table(t, [[r["number"], r["issued_at"][:10], r["grand_total"], r["paid"], r["due"]] for r in s["history"]]); l.addWidget(t); dlg.exec()


class ProductsPage(QWidget):
    FIELDS = [("name", T("নাম")), ("sku", T("এসকেইউ")), ("barcode", T("বারকোড")), ("category", T("ক্যাটাগরি")), ("brand", T("ব্র্যান্ড")), ("purchase_price", T("ক্রয়মূল্য")),
              ("selling_price", T("বিক্রয়মূল্য")), ("unit", T("একক")), ("stock", T("স্টক")), ("low_stock_alert", T("স্টক কমলে সতর্কতা (সংখ্যা)"))]

    def __init__(self, app):
        super().__init__(); self.setObjectName("page"); self.app = app; v = QVBoxLayout(self); v.addWidget(h1(T("পণ্য")))
        bar = QHBoxLayout(); self.q = QLineEdit(); self.q.setPlaceholderText(T("নাম / এসকেইউ / বারকোড দিয়ে খুঁজুন…")); self.q.textChanged.connect(self.refresh); bar.addWidget(self.q, 1)
        for t, s, sec in ((T("যোগ করুন"), self.add, False), (T("মুছুন"), self.delete, True), (T("CSV ইমপোর্ট"), self.imp, True), (T("CSV এক্সপোর্ট"), self.exp, True)): bar.addWidget(button(t, s, sec))
        v.addLayout(bar); self.info = QLabel(); v.addWidget(self.info)
        self.t = table(["ID", T("নাম"), T("এসকেইউ"), T("ক্যাটাগরি"), T("ব্র্যান্ড"), T("ক্রয়"), T("বিক্রয়"), T("একক"), T("স্টক")]); v.addWidget(self.t)

    def refresh(self):
        fill_table(self.t, [[p["id"], p["name"], p["sku"] or "", p["category"], p["brand"], p["purchase_price"], p["selling_price"], p["unit"], p["stock"]] for p in self.app.products.search(self.q.text(), 500)])
        low = self.app.products.low_stock(); self.info.setText(T("⚠ স্টক কম: {}").format(', '.join(p['name'] for p in low)) if low else "")

    def add(self):
        d = FormDialog(T("পণ্য যোগ করুন"), self.FIELDS, {"unit": "Pcs", "stock": "0", "selling_price": "0", "purchase_price": "0"}, self)
        if d.exec():
            v = d.values(); la = v.pop("low_stock_alert")
            try: self.app.products.add(**{k: x or None if k in ("sku", "barcode") else x for k, x in v.items()}, low_stock_alert=la or None, track_stock=bool(la))
            except Exception as e: return error(self, e)
            self.refresh()

    def delete(self):
        r = self.t.currentRow()
        if r >= 0 and ask(self, T("মুছুন"), T("এই পণ্য মুছবেন?")): self.app.products.delete(int(self.t.item(r, 0).text())); self.refresh()

    def imp(self):
        p, _ = QFileDialog.getOpenFileName(self, T("পণ্য ইমপোর্ট"), "", "CSV (*.csv)")
        if p:
            try: n = self.app.products.import_csv(p)
            except Exception as e: return error(self, e)
            self.refresh(); self.info.setText(T("{n}টি পণ্য ইমপোর্ট হয়েছে").format(n=n))

    def exp(self):
        p, _ = QFileDialog.getSaveFileName(self, T("পণ্য এক্সপোর্ট"), "products.csv", "CSV (*.csv)")
        if p: self.app.products.export_csv(p)


class HistoryPage(QWidget):
    def __init__(self, app):
        super().__init__(); self.setObjectName("page"); self.app = app; v = QVBoxLayout(self); v.addWidget(h1(T("বিক্রির ইতিহাস")))
        bar = QHBoxLayout(); self.num, self.cus = QLineEdit(), QLineEdit(); self.num.setPlaceholderText(T("মেমো নং")); self.cus.setPlaceholderText(T("গ্রাহক"))
        self.d1, self.d2 = QDateEdit(QDate(2020, 1, 1)), QDateEdit(QDate.currentDate())
        for d in (self.d1, self.d2): d.setCalendarPopup(True)
        self.st = QComboBox(); self.pay = QComboBox()
        for t_, d_ in ((T("সব অবস্থা"), "all"), (T("বৈধ"), "issued"), (T("বাতিল"), "void")): self.st.addItem(t_, userData=d_)
        for t_, d_ in ((T("সব পেমেন্ট"), "any"), (T("পরিশোধিত"), "paid"), (T("বাকি আছে"), "due")): self.pay.addItem(t_, userData=d_)
        for w in (self.num, self.cus, self.d1, self.d2, self.st, self.pay): bar.addWidget(w)
        bar.addWidget(button(T("খুঁজুন"), self.refresh)); v.addLayout(bar)
        bar2 = QHBoxLayout()
        for t, s, sec in ((T("আবার প্রিন্ট / প্রিভিউ"), self.preview, False), (T("কপি করুন"), self.dup, True), (T("বাতিল করুন"), self.void, True), (T("পরিবর্তনের ইতিহাস"), self.audit, True)): bar2.addWidget(button(t, s, sec, t == T("বাতিল করুন")))
        bar2.addWidget(button(T("স্থায়ীভাবে মুছুন"), self.remove, danger=True)); bar2.addWidget(button(T("সব ইতিহাস মুছুন"), self.remove_all, danger=True))
        bar2.addStretch(); v.addLayout(bar2)
        self.t = table(["ID", T("নম্বর"), T("তারিখ"), T("গ্রাহক"), T("মোট"), T("পরিশোধিত"), T("বাকি"), T("পদ্ধতি"), T("অবস্থা"), T("সংস্করণ")]); v.addWidget(self.t)

    def refresh(self, *_):
        st = None if self.st.currentData() == "all" else self.st.currentData()
        rows = self.app.db.search_documents(self.num.text() or None, self.cus.text() or None, self.d1.date().toString("yyyy-MM-dd"), self.d2.date().toString("yyyy-MM-dd"), st)
        pm = self.pay.currentData()
        if pm == "paid": rows = [r for r in rows if D(r["due"]) == 0]
        if pm == "due": rows = [r for r in rows if D(r["due"]) > 0]
        fill_table(self.t, [[r["id"], r["number"], r["issued_at"].replace("T", " "), r["customer_name"] or T("সাধারণ ক্রেতা"), r["grand_total"], r["paid"], r["due"], T(PAYMENT_BN.get(r["payment_method"], r["payment_method"])), T(STATUS_BN.get(r["status"], r["status"])), r["revision"]] for r in rows])

    def sel(self):
        r = self.t.currentRow(); return int(self.t.item(r, 0).text()) if r >= 0 else None

    def row(self, i): return self.app.db.conn.execute("SELECT * FROM documents WHERE id=?", (i,)).fetchone()

    def preview(self):
        i = self.sel()
        if i: PreviewDialog(self.app, lambda l, f_: build_pages(self.app, self.row(i), l, f_), self.row(i)["number"], self).exec()

    def dup(self):
        i = self.sel()
        if not i: return
        r = self.row(i); p = json.loads(r["payload"])
        rows = [{"name": it["name"], "description": it["description"], "qty": it["qty"], "unit": it["unit"], "price": it["price"]} for it in p["items"]]
        try:
            issue_memo(self.app.db, rows, p.get("adjustments"), {"name": r["customer_name"], "phone": r["customer_phone"], "address": r["customer_address"]}, r["payment_method"], r["template_id"], r["doc_type"])
        except Exception as e: return error(self, e)
        self.refresh()

    def void(self):
        i = self.sel()
        if not i: return
        reason, ok = QInputDialog.getText(self, T("মেমো বাতিল"), T("বাতিলের কারণ (আবশ্যক):"))
        if ok and reason.strip(): self.app.db.void_document(i, reason.strip()); self.refresh()

    def _backup_first(self, tag):
        from datetime import datetime
        try: self.app.db.backup(self.app.data_dir / "backups" / f"{tag}_{datetime.now():%Y%m%d_%H%M%S}.db"); return True
        except Exception as e: error(self, T("ব্যাকআপ হয়নি, তাই মোছা হয়নি: {}").format(e)); return False

    def remove(self):
        i = self.sel()
        if not i: return
        if not ask(self, T("স্থায়ীভাবে মুছুন"), T("এই মেমো চিরতরে মুছে যাবে (আগে ব্যাকআপ নেওয়া হবে)। মুছবেন?")): return
        if self._backup_first("before_delete"):
            self.app.db.delete_document(i); self.refresh(); self.app.window.refresh_all()

    def remove_all(self):
        text, ok = QInputDialog.getText(self, T("সব ইতিহাস মুছুন"), T("সব মেমো ও বিক্রির তথ্য মুছে যাবে!\nনিশ্চিত হলে এখানে লিখুন: মুছুন"))
        if not ok or text.strip() != T("মুছুন"): return
        if self._backup_first("before_clear_all"):
            self.app.db.clear_all_documents(reset_numbers=ask(self, T("মেমো নম্বর"), T("মেমো নম্বর আবার ১ থেকে শুরু করবেন?")))
            self.refresh(); self.app.window.refresh_all()

    def audit(self):
        i = self.sel()
        if not i: return
        dlg = QDialog(self); dlg.setWindowTitle(T("পরিবর্তনের ইতিহাস")); dlg.resize(560, 320); l = QVBoxLayout(dlg); t = table([T("কখন"), T("কাজ"), T("কারণ")])
        fill_table(t, [[a["at"].replace("T", " "), a["action"], a["reason"] or ""] for a in self.app.db.conn.execute("SELECT * FROM audit_log WHERE document_id=? ORDER BY id", (i,))]); l.addWidget(t); dlg.exec()
