from .i18n import T
from datetime import date
from PySide6.QtCore import QDate
from PySide6.QtGui import QPageSize, QPdfWriter, QTextDocument
from PySide6.QtWidgets import QDateEdit, QFileDialog, QHBoxLayout, QVBoxLayout, QWidget
from .w import QComboBox
from core.constants import REPORT_HEAD_BN
from core.formatting import format_amount
from exporters import export
from reports import reports as R
from .common import h1, button, table, fill_table, error


class ReportsPage(QWidget):
    NAMES = [T("দৈনিক বিক্রি"), T("সাপ্তাহিক বিক্রি"), T("মাসিক বিক্রি"), T("বার্ষিক বিক্রি"), T("গ্রাহক অনুযায়ী বিক্রি"), T("পণ্য অনুযায়ী বিক্রি"),
             T("ছাড় ও ভ্যাট"), T("বাকির রিপোর্ট"), T("পেমেন্ট পদ্ধতি")]

    def __init__(self, app):
        super().__init__(); self.setObjectName("page"); self.app = app; v = QVBoxLayout(self); v.addWidget(h1(T("রিপোর্ট ও বিশ্লেষণ")))
        bar = QHBoxLayout(); self.kind = QComboBox(); self.kind.addItems(self.NAMES)
        self.d1, self.d2 = QDateEdit(QDate(date.today().year, 1, 1)), QDateEdit(QDate.currentDate())
        for d in (self.d1, self.d2): d.setCalendarPopup(True)
        for w in (self.kind, self.d1, self.d2): bar.addWidget(w)
        for t, s, sec in ((T("দেখুন"), self.show, False), ("CSV", lambda: self.save("csv"), True), (T("এক্সেল"), lambda: self.save("xlsx"), True), ("PDF", lambda: self.save("pdf"), True)): bar.addWidget(button(t, s, sec))
        v.addLayout(bar); self.t = table(["-"]); v.addWidget(self.t); self.rows = []

    def data(self):
        kw = dict(date_from=self.d1.date().toString("yyyy-MM-dd"), date_to=self.d2.date().toString("yyyy-MM-dd")); db = self.app.db; k = self.kind.currentIndex()
        if k < 4: return R.sales_by_period(db, ["day", "week", "month", "year"][k], **kw)
        if k == 4: return R.by_customer(db, **kw)
        if k == 5: return R.by_product(db, **kw)
        if k == 6: t = R.tax_and_discount(db, **kw); return [{"item": T("আদায়কৃত ভ্যাট + ট্যাক্স"), "amount": t["vat_and_tax"]}, {"item": T("প্রদত্ত ছাড়"), "amount": t["discount"]}]
        if k == 7: return R.due_report(db)
        return R.by_payment_method(db, **kw)

    def show(self):
        self.rows = [{k: (format_amount(v) if hasattr(v, "quantize") else v) for k, v in r.items()} for r in self.data()]
        heads = [T(REPORT_HEAD_BN.get(k, k)) for k in self.rows[0].keys()] if self.rows else [T("কোনো তথ্য নেই")]
        self.t.setColumnCount(len(heads)); self.t.setHorizontalHeaderLabels(heads); fill_table(self.t, [list(r.values()) for r in self.rows])

    def save(self, kind):
        if not self.rows: self.show()
        if not self.rows: return error(self, T("এই রিপোর্টে কোনো তথ্য নেই"))
        path, _ = QFileDialog.getSaveFileName(self, T("এক্সপোর্ট"), f"report.{kind}", f"*.{kind}")
        if not path: return
        title = self.kind.currentText()
        if kind == "csv": export.to_csv([{T(REPORT_HEAD_BN.get(k, k)): v for k, v in r.items()} for r in self.rows], path)
        elif kind == "xlsx": export.to_xlsx([{T(REPORT_HEAD_BN.get(k, k)): v for k, v in r.items()} for r in self.rows], path, title)
        else:
            heads = [T(REPORT_HEAD_BN.get(k, k)) for k in self.rows[0].keys()]
            html = f"<h2>{title}</h2><table border='1' cellspacing='0' cellpadding='4' width='100%'><tr>" + "".join(f"<th bgcolor='#0B2A5B'><font color='white'>{h}</font></th>" for h in heads) + "</tr>"
            html += "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r.values()) + "</tr>" for r in self.rows) + "</table>"
            w = QPdfWriter(path); w.setPageSize(QPageSize(QPageSize.A4)); d = QTextDocument(); d.setHtml(html); d.print_(w)
