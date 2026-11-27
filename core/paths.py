import sys
from pathlib import Path


def data_dir() -> Path:
    base = Path.home() / "AppData" / "Roaming" if sys.platform == "win32" else Path.home() / ".local" / "share"
    d = base / "RiponCashMemoStudio"; (d / "backups").mkdir(parents=True, exist_ok=True); return d
