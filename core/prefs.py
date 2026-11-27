"""UI preferences kept in a small JSON file (readable before Qt starts, so language/scale apply at startup)."""
import json
from .paths import data_dir

DEFAULTS = {"language": "bn", "ui_font": "", "ui_scale": 115, "doc_language": "bn", "doc_font": ""}


def _file(): return data_dir() / "ui_prefs.json"


def load() -> dict:
    d = dict(DEFAULTS)
    try: d.update(json.loads(_file().read_text(encoding="utf-8")))
    except Exception: pass
    return d


def save(**kw) -> dict:
    d = load(); d.update(kw)
    _file().write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8"); return d


def get(key, default=None): return load().get(key, DEFAULTS.get(key, default))
