from .i18n import T
from datetime import date
from PySide6.QtWidgets import QGridLayout, QLabel, QVBoxLayout, QWidget
from .w import CardWidget
from core.formatting import format_amount
from reports import reports
from .common import h1, button


class Dashboard(QWidget):
    def __init__(self, app):
        super().__init__(); self.setObjectName("page"); self.app = app
        v = QVBoxLayout(self); v.addWidget(h1(T("ড্যাশবোর্ড")))
        self.grid = QGridLayout(); v.addLayout(self.grid)
        self.cards = {}
        for i, (k, label) in enumerate([("total_sales", T("মোট বিক্রি")), ("today_sales", T("আজকের বিক্রি")), ("invoices", T("মোট মেমো/ইনভয়েস")),
                                         ("paid", T("পরিশোধিত টাকা")), ("outstanding", T("মোট বাকি")), ("customers", T("মোট গ্রাহক"))]):
            f = CardWidget(); fl = QVBoxLayout(f); fl.setContentsMargins(18, 14, 18, 14)
            val = QLabel("-"); val.setStyleSheet("font-size:20pt;font-weight:bold;color:#0B6BCB;background:transparent"); lab = QLabel(label); lab.setStyleSheet("color:#7A8797;background:transparent")
            fl.addWidget(val); fl.addWidget(lab); self.grid.addWidget(f, i // 3, i % 3); self.cards[k] = val
        row = QGridLayout(); v.addLayout(row)
        for i, (t, page) in enumerate([(T("নতুন ক্যাশ মেমো"), "memo"), (T("নতুন ইনভয়েস"), "memo"), (T("নতুন রশিদ"), "memo"), (T("টেমপ্লেট স্টুডিও"), "studio"),
                                        (T("গ্রাহক"), "customers"), (T("পণ্য"), "products"), (T("বিক্রির ইতিহাস"), "history"), (T("রিপোর্ট"), "reports"),
                                        (T("সেটিংস"), "settings")]):
            row.addWidget(button(t, lambda p=page, t=t: app.window.open(p, t)), i // 3, i % 3)
        v.addStretch()

    def refresh(self):
        s = reports.dashboard_stats(self.app.db, date.today().isoformat())
        for k, lab in self.cards.items():
            lab.setText(str(s[k]) if k in ("invoices", "customers") else T("৳ ") + format_amount(s[k]))
