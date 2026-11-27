# Test Report
Environment: Linux sandbox, Python 3.12, no PySide6, no Bengali font, no Windows.
Automated: 39 unit tests PASS (incl. language/font: every UI string has English, templates translate to English/override font, prefs) (incl. 18 Bengali presets: valid, one page, in bounds, numbered blank rows, payment tick, pagination, DB round trip) — calculation (spec example 9,550.00, VAT before/after discount, rounding, validation, float rejection), BD formatting,
database (numbering, void/revise audit, backup/restore, rollback), layout (pagination, header repeat, bounds), PDF export, templates save/duplicate/validate,
reports, CSV/XLSX, stock decrement + atomic rollback, customer balances.
Visually checked: sample A4 memo PDF (sample_cash_memo.pdf).
NOT yet tested (needs a Windows machine with PySide6): all ui/ screens, render/qt_backend (Bengali shaping, printing, PNG), PyInstaller build, Inno Setup installer.
Bengali glyph rendering could not be viewed here (no Bengali font in the sandbox); layout was checked with English-labelled copies (template_gallery_layout_preview.png). Fluent UI (qfluentwidgets) code is untested: written from its documented API, with a plain-Qt fallback.
Known limits: Template Studio is a property-grid editor with preview; the drag-and-drop canvas, undo/redo, alignment guides are not built yet.
