"""Installed fonts that can show Bengali (plus the usual Bengali fonts so the list is never empty)."""
COMMON = ["Noto Sans Bengali", "Nirmala UI", "Kalpurush", "SolaimanLipi", "Siyam Rupali", "Vrinda", "Hind Siliguri", "Mukti", "Lohit Bengali", "Shonar Bangla"]


def bengali_fonts():
    try:
        from PySide6.QtGui import QFontDatabase
        ws = getattr(QFontDatabase, "WritingSystem", QFontDatabase).Bengali
        fams = list(QFontDatabase.families(ws))
    except Exception:
        fams = []
    return sorted(set(fams) | {f for f in COMMON if not fams or f in fams}) if fams else COMMON
