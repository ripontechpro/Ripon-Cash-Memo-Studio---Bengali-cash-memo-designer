# RIPON COMPUTER AND ELECTRONICS — Cash Memo Studio
Professional Business Document Designer. Offline-first desktop app (Python, PySide6, SQLite) for Bangladeshi businesses.

## Architecture
| Folder | Role |
|---|---|
| core/ | Decimal-safe money, calculation engine, BD number formatting, constants |
| db/ | SQLite, migrations, atomic numbering, void/revise audit trail, backup/restore |
| services/ | Customers, products (CSV import/export, low stock), templates, settings, memo creation |
| templates_lib/ | JSON template model, default blue/navy design, validation, business presets |
| render/ | layout engine (shared by preview/PDF/print), Qt backend (production, Bengali shaping), ReportLab backend (tests/headless), QR + Code128 |
| reports/, exporters/ | Sales/customer/product/due/VAT/payment reports; CSV and Excel export |
| ui/ | PySide6 screens: dashboard, memo editor, template studio, customers, products, history, reports, settings |
| app.py | Entry point (splash, theme, auto-backup on exit) |

Run: `pip install -r requirements.txt` then `python app.py`. Tests: `python -m unittest discover -s tests -t .`
Bengali fonts: copy Noto Sans Bengali `*-Regular.ttf` and `*-Bold.ttf` into `assets/fonts/` (see BUILD_WINDOWS.md).
See PROGRESS.md for status and next steps.

## UI & licensing note
The UI uses **PySide6-Fluent-Widgets** (modern Windows-11 Fluent look, dark/light theme) when installed; otherwise it falls back to plain Qt with a clean stylesheet
(`ui/w.py` is the only place that chooses). qfluentwidgets is GPLv3 for non-commercial use — **to sell this software you need its commercial licence**
(or ship on the fallback / replace it). PySide6 itself is LGPL.

## Bengali templates
`templates_lib/bn_presets.py` generates 18 ready-made Bengali templates (computer/electronics, repair, mobile, grocery, pharmacy, hardware, electrical, cloth,
stationery, wholesale, retail, photocopy/photo studio, A6 mini slips, gift shop, sweets/bakery, VAT invoice, money receipt). They are installed on first run and
take shop name/address/phone from Settings (defaults: Ripon Computer, ভাদ্দা বাজার, নাগরপুর, টাঙ্গাইল, 01903888515).
