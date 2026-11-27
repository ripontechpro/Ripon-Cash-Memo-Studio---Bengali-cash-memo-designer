from .i18n import T, LANG
from templates_lib.bn_presets import display_name
from PySide6.QtCore import Qt, QStringListModel
from PySide6.QtWidgets import QCompleter, QFormLayout, QGridLayout, QHBoxLayout, QLabel, QTableWidgetItem, QVBoxLayout, QWidget, QHeaderView
from .w import QComboBox, QDoubleSpinBox, QLineEdit, PlainLineEdit, Group as QGroupBox, new_table
from core.calculation import calculate, LineItem, Adjustments, CalculationError
from core.constants import PAYMENT_METHODS, PAYMENT_BN, UNITS
from core.formatting import format_amount
from core.money import D
from services.memo_service import issue_memo
from .common import h1, button, error
from .preview import PreviewDialog, build_pages

COLS = [T("পণ্য"), T("বিবরণ"), "Qty", T("একক"), T("একক মূল্য"), T("ছাড় (যেমন 10% বা 50)"), T("মোট")]


def spin(maximum=10**9, dec=2):
    s = QDoubleSpinBox(); s.setRange(0, maximum); s.setDecimals(dec); return s


class MemoPage(QWidget):
    def __init__(self, app):
        super().__init__(); self.setObjectName("page"); self.app = app; self._busy = False
        self.doc_type = "cash_memo"
        v = QVBoxLayout(self); self.title = h1(T("নতুন ক্যাশ মেমো")); v.addWidget(self.title)
        top = QHBoxLayout(); v.addLayout(top)
        cg = QGroupBox(T("গ্রাহক (ঐচ্ছিক)")); cf = QFormLayout(cg.body)
        self.cust_pick = QComboBox(); self.cust_pick.currentIndexChanged.connect(self.pick_customer)
        self.cname, self.cphone, self.caddr = QLineEdit(), QLineEdit(), QLineEdit()
        for l, w in ((T("নিবন্ধিত গ্রাহক"), self.cust_pick), (T("নাম"), self.cname), (T("ফোন"), self.cphone), (T("ঠিকানা"), self.caddr)): cf.addRow(l, w)
        top.addWidget(cg, 2)
        tg = QGroupBox(T("টেমপ্লেট ও পেমেন্ট")); tf = QFormLayout(tg.body)
        self.tpl = QComboBox(); self.pay = QComboBox()
        for m_ in PAYMENT_METHODS: self.pay.addItem(T(PAYMENT_BN[m_]), userData=m_)
        tf.addRow(T("টেমপ্লেট"), self.tpl); tf.addRow(T("পেমেন্টের ধরন"), self.pay); top.addWidget(tg, 1)

        sr = QHBoxLayout(); self.search = PlainLineEdit(); self.search.setMinimumHeight(34); self.search.setPlaceholderText(T("পণ্যের নাম / এসকেইউ / বারকোড লিখে Enter চাপুন…"))
        self.comp = QCompleter([]); self.comp.setCaseSensitivity(Qt.CaseInsensitive); self.comp.setFilterMode(Qt.MatchContains); self.search.setCompleter(self.comp)
        self.search.textEdited.connect(self.update_completer); self.search.returnPressed.connect(self.add_from_search)
        sr.addWidget(self.search, 1); sr.addWidget(button(T("+ সারি যোগ"), self.add_row, True)); sr.addWidget(button(T("সারি মুছুন"), self.remove_row, True)); v.addLayout(sr)

        self.t = new_table(0, len(COLS)); self.t.setHorizontalHeaderLabels(COLS)
        self.t.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch); self.t.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.t.itemChanged.connect(self.recalc); v.addWidget(self.t, 1)

        bottom = QHBoxLayout(); v.addLayout(bottom)
        ag = QGroupBox(T("ছাড়, ভ্যাট ও চার্জ")); g = QGridLayout(ag.body)
        self.dtype = QComboBox(); self.dtype.addItems(["percent", "fixed"]); self.dval = spin()
        self.vat, self.tax = spin(100), spin(100); self.vmode = QComboBox(); self.vmode.addItems(["after_discount", "before_discount"])
        self.deliv, self.serv, self.other, self.paid, self.prev = spin(), spin(), spin(), spin(), spin()
        self.round = QComboBox(); self.round.addItems(["none", "nearest", "up", "down"])
        fields = [(T("সর্বমোট ছাড়"), self.dval), (T("ধরন"), self.dtype), (T("ভ্যাট %"), self.vat), (T("ট্যাক্স %"), self.tax), (T("ভ্যাট হিসাব"), self.vmode),
                  (T("ডেলিভারি"), self.deliv), (T("সার্ভিস চার্জ"), self.serv), (T("অন্যান্য"), self.other), (T("পূর্বের বাকি"), self.prev), (T("পরিশোধিত"), self.paid), (T("রাউন্ডিং"), self.round)]
        for i, (l, w) in enumerate(fields):
            g.addWidget(QLabel(l), i // 4 * 2, i % 4); g.addWidget(w, i // 4 * 2 + 1, i % 4)
            (w.valueChanged if hasattr(w, "valueChanged") else w.currentIndexChanged).connect(self.recalc)
        bottom.addWidget(ag, 3)
        self.summary = QLabel(); self.summary.setTextFormat(Qt.RichText); bottom.addWidget(self.summary, 1)
        act = QHBoxLayout(); v.addLayout(act); act.addStretch()
        act.addWidget(button(T("পরিষ্কার"), self.clear, True)); act.addWidget(button(T("সংরক্ষণ ও প্রিভিউ"), self.save))
        self.add_row(); self.recalc()

    # --- data helpers
    def refresh(self):
        self.cust_pick.blockSignals(True); self.cust_pick.clear(); self.cust_pick.addItem(T("— সাধারণ ক্রেতা / নিবন্ধিত নয় —"), userData=None)
        for c in self.app.customers.search(""): self.cust_pick.addItem(c["name"], userData=dict(c))
        self.cust_pick.blockSignals(False)
        self.tpl.clear(); self.tpl.addItem(T("রিপন ক্লাসিক (ডিফল্ট)"), userData=None)
        for r in self.app.templates.list(): self.tpl.addItem(display_name(r["name"], LANG), userData=r["id"])
        for i_ in range(self.tpl.count()):
            if self.tpl.itemText(i_).startswith(("রিপন ক্লাসিক", "Ripon Classic")) and self.tpl.itemData(i_): self.tpl.setCurrentIndex(i_); break

    def pick_customer(self):
        d = self.cust_pick.currentData()
        if d: self.cname.setText(d["name"]); self.cphone.setText(d["phone"] or ""); self.caddr.setText(d["address"] or "")

    def update_completer(self, text):
        names = [r["name"] for r in self.app.products.search(text)]
        self.comp.setModel(QStringListModel(names))

    def add_from_search(self):
        rows = self.app.products.search(self.search.text(), 1)
        if not rows: return
        p = rows[0]; self.add_row(); r = self.t.rowCount() - 1; self._busy = True
        for c, val in ((0, p["name"]), (2, "1"), (3, p["unit"]), (4, p["selling_price"])): self.t.setItem(r, c, QTableWidgetItem(str(val)))
        self.t.item(r, 0).setData(Qt.UserRole, p["id"]); self._busy = False
        self.search.clear(); self.recalc()

    def add_row(self):
        self._busy = True; r = self.t.rowCount(); self.t.insertRow(r)
        for c in range(len(COLS)): self.t.setItem(r, c, QTableWidgetItem(""))
        self.t.item(r, 2).setText("1"); self.t.item(r, 3).setText("Pcs"); self.t.item(r, 6).setFlags(Qt.ItemIsEnabled)
        self._busy = False

    def remove_row(self):
        r = self.t.currentRow()
        if r >= 0: self.t.removeRow(r); self.recalc()

    def rows(self):
        out = []
        for r in range(self.t.rowCount()):
            g = lambda c: (self.t.item(r, c).text() if self.t.item(r, c) else "").strip()
            if not g(0): continue
            disc = g(5); dt = "percent" if disc.endswith("%") else "fixed"
            out.append({"name": g(0), "description": g(1), "qty": g(2) or "0", "unit": g(3), "price": g(4) or "0",
                        "disc_type": dt, "disc_value": disc.rstrip("%") or "0", "product_id": self.t.item(r, 0).data(Qt.UserRole)})
        return out

    def adjustments(self):
        return dict(discount_type=self.dtype.currentText(), discount_value=str(self.dval.value()), vat_percent=str(self.vat.value()),
                    tax_percent=str(self.tax.value()), vat_mode=self.vmode.currentText(), delivery=str(self.deliv.value()),
                    service=str(self.serv.value()), other_charges=str(self.other.value()), paid=str(self.paid.value()),
                    previous_due=str(self.prev.value()), rounding=self.round.currentText())

    def recalc(self, *_):
        if self._busy: return
        try:
            rows = self.rows()
            items = [LineItem(r["qty"], r["price"], r["disc_type"], r["disc_value"]) for r in rows]
            t = calculate(items, Adjustments(**self.adjustments()))
        except (CalculationError, ValueError) as e:
            self.summary.setText(f"<span style='color:#C0392B'><b>{T('ইনপুট ঠিক করুন:')}</b> {e}</span>"); return
        self._busy = True; k = 0
        for r in range(self.t.rowCount()):
            if self.t.item(r, 0) and self.t.item(r, 0).text().strip() and k < len(t.line_totals):
                self.t.item(r, 6).setText(format_amount(t.line_totals[k])); k += 1
            elif self.t.item(r, 6): self.t.item(r, 6).setText("")
        self._busy = False
        f = format_amount
        self.summary.setText(T("মোট: <b>{}</b><br>ছাড়: {}<br>ভ্যাট+ট্যাক্স: {}<br>চার্জ: {}<br>রাউন্ডিং: {}<br>").format(
            f(t.subtotal), f(t.overall_discount), f(t.vat + t.tax), f(t.delivery + t.service + t.other_charges), f(t.rounding_adjustment))
            + "<span style='font-size:15pt;color:#0B6BCB'><b>" + T("সর্বমোট: ৳ {}").format(f(t.grand_total)) + "</b></span><br><b>" + T("বাকি: ৳ {}").format(f(t.current_due)) + "</b>")

    def clear(self):
        self.t.setRowCount(0); self.add_row()
        for w in (self.cname, self.cphone, self.caddr): w.clear()
        for w in (self.dval, self.vat, self.tax, self.deliv, self.serv, self.other, self.paid, self.prev): w.setValue(0)
        self.recalc()

    def save(self):
        try:
            cust = None
            if self.cname.text().strip() or self.cust_pick.currentData():
                d = self.cust_pick.currentData() or {}
                cust = {"id": d.get("id") if d and d.get("name") == self.cname.text().strip() else None, "name": self.cname.text().strip(),
                        "phone": self.cphone.text(), "address": self.caddr.text()}
            doc_id, number, totals, payload = issue_memo(self.app.db, self.rows(), self.adjustments(), cust, self.pay.currentData(),
                                                          self.tpl.currentData(), self.doc_type)
        except (CalculationError, ValueError) as e:
            return error(self, e)
        row = self.app.db.conn.execute("SELECT * FROM documents WHERE id=?", (doc_id,)).fetchone()
        PreviewDialog(self.app, lambda l, f_: build_pages(self.app, row, l, f_), f"{number}", self).exec()
        self.clear(); self.app.window.refresh_all()
