"""Entry point: python app.py"""
import os
import sys
from pathlib import Path
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QSplashScreen
from db.database import Database
from render import qt_backend
from services.repositories import Customers, Products, Settings, Templates
from templates_lib import bn_presets
from ui.theme import QSS
from ui import w as widgets

ROOT = Path(__file__).resolve().parent if not getattr(sys, "frozen", False) else Path(sys._MEIPASS)


class AppContext:
    DEFAULTS = {"business_name": "Ripon Computer", "business_subtitle": "Your Trusted Tech Partner", "address": "ভাদ্দা বাজার, নাগরপুর, টাঙ্গাইল", "phone": "01903888515",
                "email": "", "website": "", "social": "", "registration": "", "thank_you": "ধন্যবাদ! আবার আসবেন",
                "terms": "পণ্যের গ্যারান্টি শুধুমাত্র নির্দিষ্ট শর্তে প্রযোজ্য।\nবিল সংরক্ষণ করুন।"}

    def __init__(self):
        from core.paths import data_dir
        self.data_dir = data_dir()
        self.db = Database(self.data_dir / "cashmemo.db"); self.bind(); self.window = None
        self.seed_templates()

    def bind(self):
        self.settings, self.templates, self.customers, self.products = Settings(self.db), Templates(self.db), Customers(self.db), Products(self.db)

    rebind = bind

    def business(self):
        b = dict(self.DEFAULTS); b.update({k: self.settings.get(k, v) for k, v in self.DEFAULTS.items()}); return b

    def logo_path(self):
        p = self.settings.get("logo_path", "")
        return p if p and Path(p).exists() else str(ROOT / "assets" / "logo_rc.png")

    def app_icon_path(self): return str(ROOT / "assets" / "app_logo.png")

    def app_ico_path(self): return str(ROOT / "assets" / "app.ico")

    def default_template(self): return bn_presets.build(bn_presets.SPECS[0])

    def seed_templates(self):
        """First run: install the 18 ready-made Bengali templates (users can edit/delete them freely)."""
        if self.settings.get("bn_templates_seeded_v1"): return
        for t in bn_presets.all_templates("bn"):
            self.templates.save(t["name"], t, doc_type=t["doc_type"])
        self.settings.set("bn_templates_seeded_v1", True)

    def prune_backups(self, keep=14):
        files = sorted((self.data_dir / "backups").glob("auto_*.db"))
        for f in files[:-keep]: f.unlink(missing_ok=True)


def main():
    from core import prefs
    pf = prefs.load()
    os.environ.setdefault("QT_SCALE_FACTOR", str(max(100, min(200, int(pf["ui_scale"]))) / 100))  # bigger text/UI everywhere (applies at start)
    if sys.platform == "win32":  # own taskbar identity so the Windows taskbar shows our icon
        try:
            import ctypes; ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Ripon.CashMemoStudio.1")
        except Exception: pass
    qa = QApplication(sys.argv)
    from PySide6.QtGui import QIcon
    qa.setWindowIcon(QIcon(str(ROOT / "assets" / "app.ico")))
    if not widgets.FLUENT: qa.setStyleSheet(QSS)
    from PySide6.QtGui import QFont
    f = QFont(); f.setFamilies(([pf["ui_font"]] if pf["ui_font"] else []) + ["Noto Sans Bengali", "Nirmala UI", "Segoe UI", "Kalpurush", "SolaimanLipi"]); f.setPixelSize(15); qa.setFont(f)
    if widgets.FLUENT:
        from ui import fontfix; fontfix.install(qa)
    if pf["ui_font"] and not widgets.FLUENT: qa.setStyleSheet(QSS + "* { font-family: '%s'; }" % pf["ui_font"])
    fonts = ROOT / "assets" / "fonts"
    if fonts.exists(): qt_backend.load_fonts(fonts)
    pm = QPixmap(str(ROOT / "assets" / "app_logo.png")).scaled(420, 420, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    splash = QSplashScreen(pm); splash.show(); qa.processEvents()
    ctx = AppContext()
    from ui.main_window import MainWindow
    w = MainWindow(ctx); ctx.window = w; w.refresh_all()
    QTimer.singleShot(1200, lambda: (splash.finish(w), w.show()))
    sys.exit(qa.exec())


if __name__ == "__main__":
    main()
