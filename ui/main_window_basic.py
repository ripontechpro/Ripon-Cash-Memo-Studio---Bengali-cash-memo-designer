from .i18n import T
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QShortcut, QKeySequence
from PySide6.QtWidgets import QButtonGroup, QFrame, QHBoxLayout, QLabel, QMainWindow, QPushButton, QStackedWidget, QVBoxLayout, QWidget
from .dashboard import Dashboard
from .lists import CustomersPage, ProductsPage, HistoryPage
from .memo_page import MemoPage
from .reports_page import ReportsPage
from .settings_page import SettingsPage
from .studio import StudioPage

NAV = [("dashboard", T("🏠  ড্যাশবোর্ড")), ("memo", T("🧾  নতুন ক্যাশ মেমো")), ("studio", T("🎨  টেমপ্লেট স্টুডিও")), ("customers", T("👥  গ্রাহক")),
       ("products", T("📦  পণ্য")), ("history", T("🗂  বিক্রির ইতিহাস")), ("reports", T("📊  রিপোর্ট")), ("settings", T("⚙  সেটিংস ও ব্যাকআপ"))]


class MainWindow(QMainWindow):
    def __init__(self, app):
        super().__init__(); self.app = app; app.window = self
        self.setWindowIcon(__import__("PySide6.QtGui", fromlist=["QIcon"]).QIcon(app.app_ico_path()))
        self.setWindowTitle(T("রিপন কম্পিউটার অ্যান্ড ইলেকট্রনিক্স — ক্যাশ মেমো স্টুডিও")); self.resize(1280, 800)
        root = QWidget(); self.setCentralWidget(root); h = QHBoxLayout(root); h.setContentsMargins(0, 0, 0, 0); h.setSpacing(0)
        side = QFrame(); side.setObjectName("sidebar"); side.setFixedWidth(230); sl = QVBoxLayout(side); sl.setContentsMargins(0, 10, 0, 10)
        self.logo = QLabel(); self.logo.setAlignment(Qt.AlignCenter); sl.addWidget(self.logo)
        name = QLabel("RIPON COMPUTER\nAND ELECTRONICS"); name.setAlignment(Qt.AlignCenter); name.setStyleSheet("color:white;font-weight:bold;padding:4px"); sl.addWidget(name)
        tag = QLabel(T("ক্যাশ মেমো স্টুডিও")); tag.setAlignment(Qt.AlignCenter); tag.setStyleSheet("color:#19B5D8;padding-bottom:10px"); sl.addWidget(tag)
        self.stack = QStackedWidget(); self.pages = {}; self.btns = {}; grp = QButtonGroup(self)
        cls = {"dashboard": Dashboard, "memo": MemoPage, "studio": StudioPage, "customers": CustomersPage, "products": ProductsPage,
               "history": HistoryPage, "reports": ReportsPage, "settings": SettingsPage}
        for key, label in NAV:
            b = QPushButton(label); b.setObjectName("nav"); b.setCheckable(True); b.setToolTip(label.strip()); grp.addButton(b)
            b.clicked.connect(lambda _=False, k=key: self.open(k)); sl.addWidget(b); self.btns[key] = b
            p = cls[key](app); self.pages[key] = p; self.stack.addWidget(p)
        sl.addStretch(); about = QPushButton(T("ℹ  সম্পর্কে")); about.setObjectName("nav"); about.clicked.connect(self.about); sl.addWidget(about)
        h.addWidget(side); h.addWidget(self.stack, 1)
        for i, (k, _) in enumerate(NAV[:8]): QShortcut(QKeySequence(f"Ctrl+{i+1}"), self, activated=lambda k=k: self.open(k))
        self.open("dashboard")

    def open(self, key, *_):
        if key not in self.pages: key = "memo"
        self.btns.get(key, self.btns["dashboard"]).setChecked(True)
        p = self.pages[key]; self.stack.setCurrentWidget(p)
        if hasattr(p, "refresh"): p.refresh()

    def refresh_all(self):
        pm = QPixmap(self.app.app_icon_path())
        self.logo.setPixmap(pm.scaledToWidth(110, Qt.SmoothTransformation))
        cur = self.stack.currentWidget()
        if hasattr(cur, "refresh"): cur.refresh()

    def about(self):
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.about(self, T("সম্পর্কে"), "<b>RIPON COMPUTER AND ELECTRONICS</b><br>Cash Memo Studio — Professional Business Document Designer<br>Version 1.0<br><br>Offline-first. Your data stays on this computer.")

    def closeEvent(self, e):
        if self.app.settings.get("auto_backup", True):
            from datetime import datetime
            try: self.app.db.backup(self.app.data_dir / "backups" / f"auto_{datetime.now():%Y%m%d_%H%M%S}.db"); self.app.prune_backups()
            except Exception: pass
        super().closeEvent(e)
