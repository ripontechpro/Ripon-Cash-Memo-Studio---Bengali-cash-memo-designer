import csv
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill


def _table(rows):
    if not rows: return [], []
    headers = list(rows[0].keys())
    return headers, [[str(r[h]) for h in headers] for r in rows]


def to_csv(rows, path):
    h, data = _table(rows)
    with open(path, "w", newline="", encoding="utf-8-sig") as f:  # BOM so Excel shows Bengali
        w = csv.writer(f); w.writerow(h); w.writerows(data)


def to_xlsx(rows, path, title="Report"):
    h, data = _table(rows)
    wb = Workbook(); ws = wb.active; ws.title = title[:31]
    ws.append(h)
    for c in ws[1]:
        c.font = Font(bold=True, color="FFFFFF"); c.fill = PatternFill("solid", fgColor="0B3C8C")
    for r in data: ws.append(r)
    for col in ws.columns:
        ws.column_dimensions[col[0].column_letter].width = min(40, max(len(str(c.value or "")) for c in col) + 3)
    wb.save(path)
