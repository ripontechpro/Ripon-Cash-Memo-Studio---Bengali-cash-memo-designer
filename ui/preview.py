from .i18n import T
"""Print preview / PDF / image export using the Qt backend (same layout as the saved document)."""
import json
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPainter
from PySide6.QtPrintSupport import QPrintDialog, QPrinter
from PySide6.QtWidgets import QDialog, QFileDialog, QHBoxLayout, QLabel, QScrollArea, QSpinBox, QVBoxLayout, QWidget
from .w import QComboBox
from PySide6.QtGui import QPixmap
from render import qt_backend as qb
from render.context import make_context
from render.layout import layout
from templates_lib.bn_presets import prepare_template
from templates_lib.model import SAMPLE_DOC, default_template, sample_payload
from core import prefs
from .i18n import T
from .fonts import bengali_fonts
from .common import button, error

ROOT = Path(__file__).resolve().parent.parent


def build_pages(app, doc_row, lang=None, font=None):
    """Pages for a saved document; lang ('bn'/'en') and font override the template at render time."""
    lang = lang or prefs.get("doc_language", "bn"); font = font if font is not None else prefs.get("doc_font", "")
    tid = doc_row["template_id"]
    tpl = app.templates.get(tid)[1] if tid and app.templates.get(tid) else app.default_template()
    tpl = prepare_template(tpl, lang, font or None)
    ctx = make_context(app.business(), doc_row, bangla=(lang == "bn" and app.settings.get("bangla_numerals", False)))
    return layout(tpl, ctx, qb.measure_mm, {"logo": app.logo_path()})


def sample_pages(app, tpl, lang=None, font=None):
    lang = lang or prefs.get("doc_language", "bn"); font = font if font is not None else prefs.get("doc_font", "")
    ctx = make_context(app.business(), SAMPLE_DOC, sample_payload(), bangla=(lang == "bn" and app.settings.get("bangla_numerals", False)))
    return layout(prepare_template(tpl, lang, font or None), ctx, qb.measure_mm, {"logo": app.logo_path()})


class PreviewDialog(QDialog):
    """pages_fn(lang, font) -> pages. The dialog lets the user switch document language and font and re-renders."""
    def __init__(self, app, pages_fn, title="Preview", parent=None):
        super().__init__(parent); self.app, self.pages_fn = app, pages_fn
        self.setWindowTitle(title); self.resize(780, 940)
        v = QVBoxLayout(self); bar = QHBoxLayout()
        self.copies = QSpinBox(); self.copies.setRange(1, 99)
        self.lang = QComboBox(); self.lang.addItem("বাংলা", userData="bn"); self.lang.addItem("English", userData="en")
        self.lang.setCurrentIndex(0 if prefs.get("doc_language", "bn") == "bn" else 1)
        self.font = QComboBox(); self.font.addItem(T("(ডিফল্ট ফন্ট)"), userData="")
        for fam in bengali_fonts(): self.font.addItem(fam, userData=fam)
        cur = prefs.get("doc_font", "")
        for i in range(self.font.count()):
            if self.font.itemData(i) == cur: self.font.setCurrentIndex(i)
        bar.addWidget(QLabel(T("ভাষা"))); bar.addWidget(self.lang); bar.addWidget(QLabel(T("ফন্ট"))); bar.addWidget(self.font)
        bar.addWidget(QLabel(T("কপি:"))); bar.addWidget(self.copies); bar.addStretch()
        bar.addWidget(button(T("প্রিন্ট"), self.print_)); bar.addWidget(button(T("PDF সংরক্ষণ"), self.pdf, True)); bar.addWidget(button(T("ছবি সংরক্ষণ"), self.png, True))
        v.addLayout(bar)
        self.host = QWidget(); self.hl = QVBoxLayout(self.host)
        sc = QScrollArea(); sc.setWidget(self.host); sc.setWidgetResizable(True); v.addWidget(sc)
        self.lang.currentIndexChanged.connect(self.render); self.font.currentIndexChanged.connect(self.render)
        self.render()

    def render(self, *_):
        self.pages = self.pages_fn(self.lang.currentData(), self.font.currentData())
        while self.hl.count():
            it = self.hl.takeAt(0)
            if it.widget(): it.widget().deleteLater()
        for pg in self.pages:
            lab = QLabel(); lab.setAlignment(Qt.AlignCenter)
            img = QImage(int(pg["w"] * 4), int(pg["h"] * 4), QImage.Format_RGB32); img.fill(Qt.white)
            p = QPainter(img); p.setRenderHint(QPainter.Antialiasing); p.setRenderHint(QPainter.TextAntialiasing)
            qb.paint_page(p, pg, 4.0); p.end()
            lab.setPixmap(QPixmap.fromImage(img)); self.hl.addWidget(lab)

    def print_(self):
        pr = QPrinter(QPrinter.HighResolution)
        if QPrintDialog(pr, self).exec():
            qb.print_pages(self.pages, pr, self.copies.value())

    def pdf(self):
        path, _ = QFileDialog.getSaveFileName(self, T("PDF সংরক্ষণ"), "memo.pdf", "PDF (*.pdf)")
        if path:
            try: qb.render_pdf(self.pages, path)
            except Exception as e: error(self, e)

    def png(self):
        path, _ = QFileDialog.getSaveFileName(self, T("ছবি সংরক্ষণ"), "memo.png", "PNG (*.png)")
        if path:
            for i, pg in enumerate(self.pages):
                qb.render_png(pg, path if i == 0 else path.replace(".png", f"_{i+1}.png"))
