"""T("বাংলা") -> Bengali as written, or English when the app language is English (set in Settings, applied at start)."""
from core import prefs

LANG = prefs.get("language", "bn")


def _en():
    from .strings_en import EN
    return EN


def T(s):
    return _en().get(s, s) if LANG == "en" else s
