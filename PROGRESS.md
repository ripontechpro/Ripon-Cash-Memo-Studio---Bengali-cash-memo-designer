# PROGRESS CHECKPOINT (update after every phase)
Project: RIPON COMPUTER AND ELECTRONICS — Cash Memo Studio (Python/PySide6/SQLite, Windows 10/11)
Run tests: python -m unittest discover -s tests -t .   (currently 24 tests)

## DONE
- Phase 1: core/money, calculation, formatting, constants; db/database (migrations v1+v2, numbering, void/revise audit, backup/restore)
- Phase 2: services/repositories (Settings, Customers, Products incl. CSV import/export + low stock, Templates CRUD/duplicate),
  services/memo_service (validate->calc->issue, stock decrement atomically), reports/reports (period/customer/product/payment/due/VAT+discount/dashboard stats),
  exporters/export (CSV with BOM, XLSX)
- Phase 3: templates_lib/model (JSON template, default blue/navy A4 template, presets, validation),
  render/layout (backend-agnostic: pagination, header repeat, wrapping, shrink-to-fit, QR/barcode prims),
  render/pdf_backend (ReportLab; English/headless/tests), render/qt_backend (Qt painter; PDF/PNG/print; UNTESTED here - no PySide6 in sandbox)
  render/codes (QR + Code128 via reportlab encoders), render/fonts, render/context

## KEY DECISIONS
- ReportLab cannot shape Bengali -> production rendering = Qt (HarfBuzz). Preview/PDF/print share the same layout => output matches preview.
- Money stored as TEXT decimals. Fonts: put Noto Sans Bengali *-Regular.ttf/*-Bold.ttf in assets/fonts (not bundled, no internet).

- Phase 4: ui/ complete set (theme, dashboard, memo editor w/ live totals + product autocomplete, customers, products, history w/ void/duplicate/audit/reprint,
  reports w/ CSV/XLSX/PDF, settings w/ logo/backup/restore, main window + shortcuts), app.py (splash, auto-backup on exit). py_compile OK, NOT run (no PySide6 here)
- Phase 5 (partial): Template Studio = property-grid editor + column editor + preview (ui/studio.py)
- Phase 6: requirements.txt, cash_memo_studio.spec, installer.iss, assets/app.ico
- Phase 7: README, USER_GUIDE, BUILD_WINDOWS, TEST_REPORT

- Phase 8 (Bengali + modern UI + templates): all UI strings in Bengali; ui/w.py widget layer (PySide6-Fluent-Widgets, fallback plain Qt); ui/main_window_fluent.py (FluentWindow nav, dark/light);
  render: rounded rects, polygons, dashed lines, checkboxes, boxed totals, numbered blank rows (padding rows never force a page); templates_lib/bn_presets.py = 18 Bengali templates
  seeded on first run; Ripon shop defaults in app.py (ভাদ্দা বাজার, নাগরপুর, টাঙ্গাইল, 01903888515); assets/logo_rc.png (RC logo cropped from user's reference). 31 tests pass.

- Phase 9 (language & font): core/prefs.py (ui_prefs.json: language, ui_font, ui_scale default 115, doc_language, doc_font), ui/i18n.py T() + ui/strings_en.py (Bengali = source text, English map),
  all UI Bengali literals wrapped in T(); Settings "ভাষা ও ফন্ট" card (+ restart); app.py sets QT_SCALE_FACTOR + app font before QApplication;
  templates_lib/bn_presets.prepare_template(tpl, lang, font) translates standard template texts to English + overrides fonts at render time;
  PreviewDialog has language/font combos and re-renders; permanent delete / clear-all history in Sales History. 39 tests pass.

## TODO (next)
- FIRST: run on Windows (pip install -r requirements.txt; python app.py); report runtime errors; check Bengali look/size of app + 18 templates, try ui_scale 130/150
- Licensing decision for qfluentwidgets if selling (commercial licence vs plain-Qt fallback)
- Drag-and-drop template canvas (QGraphicsScene) + undo/redo; revise-saved-document UI; bundle Bengali fonts (Noto Sans Bengali OFL)
