from .i18n import T
from datetime import datetime
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QKeySequence, QShortcut
from PySide6.QtWidgets import QMessageBox
from qfluentwidgets import FluentIcon as FIF, FluentWindow, NavigationItemPosition, Theme, isDarkTheme, setTheme, setThemeColor
from .dashboard import Dashboard
from .lists import CustomersPage, HistoryPage, ProductsPage
from .memo_page import MemoPage
from .reports_page import ReportsPage
from .settings_page import SettingsPage
from .studio import StudioPage

NAV = [("dashboard", T("ড্যাশবোর্ড"), "HOME", Dashboard), ("memo", T("নতুন ক্যাশ মেমো"), "DOCUMENT", MemoPage), ("studio", T("টেমপ্লেট স্টুডিও"), "BRUSH", StudioPage),
       ("customers", T("গ্রাহক"), "PEOPLE", CustomersPage), ("products", T("পণ্য"), "SHOPPING_CART", ProductsPage), ("history", T("বিক্রির ইতিহাস"), "HISTORY", HistoryPage),
       ("reports", T("রিপোর্ট"), "PIE_SINGLE", ReportsPage), ("settings", T("সেটিংস ও ব্যাকআপ"), "SETTING", SettingsPage)]


class MainWindow(FluentWindow):
    def __init__(self, app):
        super().__init__(); self.app = app; app.window = self
        setThemeColor("#0B6BCB"); setTheme(Theme.LIGHT)
        self.setWindowTitle(T("রিপন কম্পিউটার অ্যান্ড ইলেকট্রনিক্স — ক্যাশ মেমো স্টুডিও")); self.setWindowIcon(QIcon(app.app_ico_path())); self.resize(1300, 840)
        self.navigationInterface.setExpandWidth(250)
        self.pages = {}
        for i, (key, label, icon, cls) in enumerate(NAV):
            p = cls(app); p.setObjectName("page_" + key); p.layout().setContentsMargins(28, 18, 28, 18)
            self.pages[key] = p; self.addSubInterface(p, getattr(FIF, icon, FIF.HOME), label)
            QShortcut(QKeySequence(f"Ctrl+{i+1}"), self, activated=lambda k=key: self.open(k))
        self.navigationInterface.addItem("theme", getattr(FIF, "CONSTRACT", FIF.SETTING), T("ডার্ক / লাইট থিম"), onClick=self.toggle_theme, selectable=False, position=NavigationItemPosition.BOTTOM)
        self.navigationInterface.addItem("about", FIF.INFO, T("সম্পর্কে"), onClick=self.about, selectable=False, position=NavigationItemPosition.BOTTOM)
        self.stackedWidget.currentChanged.connect(lambda _=0: self.refresh_current())
        self.open("dashboard")

    def open(self, key, *_):
        self.switchTo(self.pages.get(key, self.pages["memo"]))

    def refresh_current(self):
        cur = self.stackedWidget.currentWidget()
        if hasattr(cur, "refresh"): cur.refresh()

    def refresh_all(self):
        self.refresh_current()

    def toggle_theme(self):
        setTheme(Theme.LIGHT if isDarkTheme() else Theme.DARK)

    def about(self):
        from PySide6.QtGui import QPixmap
        box = QMessageBox(self); box.setWindowTitle(T("সম্পর্কে")); box.setIconPixmap(QPixmap(self.app.app_icon_path()).scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        box.setTextFormat(Qt.RichText); box.setText(T("<b>রিপন কম্পিউটার অ্যান্ড ইলেকট্রনিক্স</b><br>ক্যাশ মেমো স্টুডিও — প্রফেশনাল বিজনেস ডকুমেন্ট ডিজাইনার<br>সংস্করণ ১.০<br><br>অফলাইনে চলে। আপনার তথ্য শুধু এই কম্পিউটারেই থাকে।")); box.exec()

    def closeEvent(self, e):
        if self.app.settings.get("auto_backup", True):
            try: self.app.db.backup(self.app.data_dir / "backups" / f"auto_{datetime.now():%Y%m%d_%H%M%S}.db"); self.app.prune_backups()
            except Exception: pass
        super().closeEvent(e)
