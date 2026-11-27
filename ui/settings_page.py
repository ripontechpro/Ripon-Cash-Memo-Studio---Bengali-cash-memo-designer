import subprocess, sys
from core import prefs
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication, QLabel
from .fonts import bengali_fonts
from .i18n import T, LANG
import shutil
from datetime import datetime
from pathlib import Path
from PySide6.QtWidgets import QFileDialog, QFormLayout, QHBoxLayout, QVBoxLayout, QWidget
from .w import QCheckBox, QComboBox, QLineEdit, QTextEdit, Group as QGroupBox
from core.constants import BUSINESS_TYPES
from .common import h1, button, ask, error, success

FIELDS = [("business_name", T("দোকানের নাম")), ("business_subtitle", T("ট্যাগলাইন")), ("address", T("ঠিকানা")), ("phone", T("ফোন")), ("email", T("ইমেইল")),
          ("website", T("ওয়েবসাইট")), ("social", T("সোশ্যাল মিডিয়া")), ("registration", T("রেজিস্ট্রেশন / বিআইএন / টিআইএন")), ("thank_you", T("ধন্যবাদ বার্তা"))]


class SettingsPage(QWidget):
    def __init__(self, app):
        super().__init__(); self.setObjectName("page"); self.app = app; v = QVBoxLayout(self); v.addWidget(h1(T("দোকানের তথ্য, ব্যাকআপ ও রিস্টোর")))
        g = QGroupBox(T("দোকানের তথ্য")); f = QFormLayout(g.body); self.w = {}
        for k, l in FIELDS: self.w[k] = QLineEdit(); f.addRow(l, self.w[k])
        self.terms = QTextEdit(); self.terms.setFixedHeight(70); f.addRow(T("শর্ত / ফেরত / ওয়ারেন্টি"), self.terms)
        self.btype = QComboBox(); self.btype.addItems(BUSINESS_TYPES); f.addRow(T("ব্যবসার ধরন"), self.btype)
        self.bn = QCheckBox(T("প্রিন্টে বাংলা সংখ্যা ব্যবহার করুন")); f.addRow(self.bn)
        r = QHBoxLayout(); r.addWidget(button(T("লোগো বাছাই…"), self.logo, True)); r.addWidget(button(T("লোগো রিসেট"), self.reset_logo, True)); r.addWidget(button(T("সেটিংস সংরক্ষণ"), self.save)); f.addRow(r)
        v.addWidget(g)
        lg = QGroupBox(T("ভাষা ও ফন্ট")); lf = QFormLayout(lg.body)
        self.app_lang, self.doc_lang = QComboBox(), QComboBox()
        for c in (self.app_lang, self.doc_lang): c.addItem("বাংলা", userData="bn"); c.addItem("English", userData="en")
        self.app_font, self.doc_font = QComboBox(), QComboBox()
        for c in (self.app_font, self.doc_font):
            c.addItem(T("(ডিফল্ট ফন্ট)"), userData="")
            for fam in bengali_fonts(): c.addItem(fam, userData=fam)
        self.app_scale = QComboBox()
        for lab, val in ((T("ছোট (১০০%)"), 100), (T("মাঝারি (১১৫%)"), 115), (T("বড় (১৩০%)"), 130), (T("অতি বড় (১৫০%)"), 150)): self.app_scale.addItem(lab, userData=val)
        self.sample = QLabel(T("আমার সোনার বাংলা, আমি তোমায় ভালোবাসি। ক্যাশ মেমো ১২৩৪৫৬৭৮৯০")); self.sample.setStyleSheet("font-size:16pt")
        self.note = QLabel(""); self.note.setWordWrap(True)
        for lab, wdg in ((T("অ্যাপের ভাষা"), self.app_lang), (T("অ্যাপের ফন্ট"), self.app_font), (T("অ্যাপের লেখার আকার"), self.app_scale),
                         (T("ডকুমেন্টের ভাষা"), self.doc_lang), (T("ডকুমেন্টের ফন্ট"), self.doc_font), (T("ফন্টের নমুনা"), self.sample)): lf.addRow(lab, wdg)
        self.app_font.currentIndexChanged.connect(self.show_sample); self.doc_font.currentIndexChanged.connect(self.show_sample)
        rr = QHBoxLayout(); rr.addWidget(button(T("সেটিংস সংরক্ষণ"), self.save_lang)); self.restart_btn = button(T("এখনই রিস্টার্ট করুন"), self.restart, True); self.restart_btn.setVisible(False)
        rr.addWidget(self.restart_btn); lf.addRow(rr); lf.addRow(self.note)
        v.addWidget(lg)
        b = QGroupBox(T("ব্যাকআপ")); bl = QHBoxLayout(b.body); bl.addWidget(button(T("এখনই ব্যাকআপ…"), self.backup)); bl.addWidget(button(T("ব্যাকআপ রিস্টোর…"), self.restore, True))
        self.auto = QCheckBox(T("বন্ধ করার সময় স্বয়ংক্রিয় ব্যাকআপ")); bl.addWidget(self.auto); v.addWidget(b); v.addStretch()

    def _pick(self, combo, value):
        combo.blockSignals(True)
        for i in range(combo.count()):
            if combo.itemData(i) == value: combo.setCurrentIndex(i); break
        combo.blockSignals(False)

    def show_sample(self, *_):
        fam = self.app_font.currentData() or self.doc_font.currentData() or "Noto Sans Bengali"
        f = QFont(); f.setFamilies([fam, "Noto Sans Bengali", "Nirmala UI"]); f.setPointSize(16); self.sample.setFont(f)

    def save_lang(self):
        old = prefs.load()
        new = prefs.save(language=self.app_lang.currentData(), ui_font=self.app_font.currentData(), ui_scale=self.app_scale.currentData(),
                         doc_language=self.doc_lang.currentData(), doc_font=self.doc_font.currentData())
        success(self, T("ভাষা ও ফন্ট সংরক্ষিত হয়েছে"))
        if any(old[k] != new[k] for k in ("language", "ui_font", "ui_scale")):
            self.note.setText(T("অ্যাপের ভাষা ও লেখার আকার বদলাতে অ্যাপ আবার চালু করতে হবে।")); self.restart_btn.setVisible(True)

    def restart(self):
        subprocess.Popen([sys.executable] + sys.argv); QApplication.quit()

    def refresh(self):
        p = prefs.load()
        self._pick(self.app_lang, p["language"]); self._pick(self.app_font, p["ui_font"]); self._pick(self.app_scale, p["ui_scale"])
        self._pick(self.doc_lang, p["doc_language"]); self._pick(self.doc_font, p["doc_font"]); self.show_sample()
        s = self.app.settings
        for k, w in self.w.items(): w.setText(s.get(k, self.app.DEFAULTS.get(k, "")))
        self.terms.setPlainText(s.get("terms", self.app.DEFAULTS["terms"])); self.btype.setCurrentText(s.get("business_type", BUSINESS_TYPES[0]))
        self.bn.setChecked(s.get("bangla_numerals", False)); self.auto.setChecked(s.get("auto_backup", True))

    def save(self):
        s = self.app.settings
        for k, w in self.w.items(): s.set(k, w.text().strip())
        s.set("terms", self.terms.toPlainText()); s.set("business_type", self.btype.currentText()); s.set("bangla_numerals", self.bn.isChecked()); s.set("auto_backup", self.auto.isChecked())
        self.app.window.refresh_all(); success(self, T("সেটিংস সংরক্ষিত হয়েছে"))

    def logo(self):
        p, _ = QFileDialog.getOpenFileName(self, T("লোগো"), "", "Images (*.png *.jpg *.jpeg)")
        if p:
            dest = self.app.data_dir / "custom_logo.png"; shutil.copy2(p, dest); self.app.settings.set("logo_path", str(dest)); self.app.window.refresh_all()

    def reset_logo(self): self.app.settings.set("logo_path", ""); self.app.window.refresh_all()

    def backup(self):
        p, _ = QFileDialog.getSaveFileName(self, T("ব্যাকআপ"), f"cashmemo_backup_{datetime.now():%Y%m%d_%H%M}.db", "Database (*.db)")
        if p:
            try: self.app.db.backup(p)
            except Exception as e: error(self, e)

    def restore(self):
        p, _ = QFileDialog.getOpenFileName(self, T("রিস্টোর"), "", "Database (*.db)")
        if p and ask(self, T("রিস্টোর"), T("এতে বর্তমান তথ্য প্রতিস্থাপিত হবে (একটি নিরাপত্তা কপি .pre_restore নামে থাকবে)। চালিয়ে যাবেন?")):
            try: self.app.db.restore(p)
            except Exception as e: return error(self, e)
            self.app.rebind(); self.app.window.refresh_all()
