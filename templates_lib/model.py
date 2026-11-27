"""Template definition (plain JSON dict) + validation + built-in presets. All coordinates in mm."""
import copy
from core.constants import PAPER_MM

NAVY, BLUE, CYAN, LIGHT = "#0B2A5B", "#0B6BCB", "#19B5D8", "#EAF2FB"


def page_size(page):
    if page.get("size") == "Custom":
        w, h = float(page["width_mm"]), float(page["height_mm"])
    else:
        w, h = PAPER_MM[page.get("size", "A4")]
    if page.get("orientation") == "landscape":
        w, h = h, w
    return w, h


def validate(t):
    if "page" not in t or "elements" not in t:
        raise ValueError("template needs 'page' and 'elements'")
    w, h = page_size(t["page"])
    if w <= 0 or h <= 0:
        raise ValueError("invalid page size")
    for e in t["elements"]:
        if e.get("type") not in ("text", "image", "line", "rect", "polygon", "checkbox", "table", "totals", "qr", "barcode"):
            raise ValueError(f"unknown element type: {e.get('type')}")
    return t


DEFAULT_COLUMNS = [
    {"key": "sn", "label": "SL", "width_mm": 10, "align": "center"},
    {"key": "name", "label": "Product Description", "width_mm": 82, "align": "left"},
    {"key": "qty", "label": "Qty", "width_mm": 16, "align": "center"},
    {"key": "unit", "label": "Unit", "width_mm": 16, "align": "center"},
    {"key": "price", "label": "Unit Price", "width_mm": 24, "align": "right"},
    {"key": "discount", "label": "Discount", "width_mm": 20, "align": "right"},
    {"key": "total", "label": "Total Price", "width_mm": 26, "align": "right"},
]


def default_template(title="CASH MEMO", font="Noto Sans Bengali"):
    return {
        "name": "Ripon Blue Classic", "version": 1,
        "page": {"size": "A4", "orientation": "portrait", "margin_mm": 10, "bg_color": "#FFFFFF",
                 "border": {"width": 0.4, "color": BLUE}, "footer_reserve_mm": 48},
        "elements": [
            {"type": "rect", "x": 10, "y": 10, "w": 190, "h": 30, "fill": NAVY, "pages": "first"},
            {"type": "image", "src": "logo", "x": 13, "y": 12, "w": 26, "h": 26, "align": "left", "pages": "first"},
            {"type": "text", "text": "{business_name}", "x": 42, "y": 13, "w": 155, "h": 11, "size": 20, "bold": True,
             "color": "#FFFFFF", "font": font, "pages": "first"},
            {"type": "text", "text": "{business_subtitle}", "x": 42, "y": 24, "w": 155, "h": 5, "size": 9,
             "color": "#BFE6F5", "font": font, "pages": "first"},
            {"type": "text", "text": "{address}   |   {phone}", "x": 42, "y": 30, "w": 155, "h": 8, "size": 8.5,
             "color": "#FFFFFF", "font": font, "pages": "first"},
            {"type": "text", "text": title, "x": 70, "y": 44, "w": 70, "h": 8, "size": 14, "bold": True,
             "color": BLUE, "font": font, "align": "center", "pages": "first"},
            {"type": "text", "text": "Memo No: {memo_number}", "x": 12, "y": 53, "w": 90, "h": 5, "size": 10, "font": font, "pages": "first"},
            {"type": "text", "text": "Date: {date}   Time: {time}", "x": 120, "y": 53, "w": 78, "h": 5, "size": 10,
             "font": font, "align": "right", "pages": "first"},
            {"type": "text", "text": "Customer: {customer_name}", "x": 12, "y": 60, "w": 100, "h": 5, "size": 10, "font": font, "pages": "first"},
            {"type": "text", "text": "Phone: {customer_phone}", "x": 120, "y": 60, "w": 78, "h": 5, "size": 10,
             "font": font, "align": "right", "pages": "first"},
            {"type": "text", "text": "Address: {customer_address}", "x": 12, "y": 66, "w": 186, "h": 5, "size": 10, "font": font, "pages": "first"},
            {"type": "table", "x": 10, "y": 75, "w": 190, "columns": copy.deepcopy(DEFAULT_COLUMNS), "font": font,
             "font_size": 9.5, "header_bg": NAVY, "header_color": "#FFFFFF", "alt_row_bg": LIGHT,
             "row_h": 7, "header_h": 8, "border_color": BLUE, "border_w": 0.2, "min_rows": 10, "continue_y": 14},
            {"type": "totals", "x": 130, "w": 70, "font": font, "size": 10, "row_h": 6.5, "bold_keys": ["grand_total", "due"],
             "rows": [{"label": "Subtotal", "key": "subtotal"}, {"label": "Discount", "key": "overall_discount"},
                      {"label": "VAT", "key": "vat"}, {"label": "Delivery", "key": "delivery"},
                      {"label": "Grand Total", "key": "grand_total"}, {"label": "Paid", "key": "paid"},
                      {"label": "Due", "key": "due"}]},
            {"type": "text", "text": "{terms}", "x": 12, "y": 252, "w": 120, "h": 16, "size": 8, "font": font, "color": "#444444", "pages": "last"},
            {"type": "line", "x": 14, "y": 280, "x2": 60, "y2": 280, "color": NAVY, "lw": 0.3, "pages": "last"},
            {"type": "text", "text": "Customer Signature", "x": 14, "y": 281, "w": 46, "h": 4, "size": 8, "font": font, "align": "center", "pages": "last"},
            {"type": "line", "x": 150, "y": 280, "x2": 196, "y2": 280, "color": NAVY, "lw": 0.3, "pages": "last"},
            {"type": "text", "text": "Authorized Signature", "x": 150, "y": 281, "w": 46, "h": 4, "size": 8, "font": font, "align": "center", "pages": "last"},
            {"type": "text", "text": "{thank_you}", "x": 60, "y": 287, "w": 90, "h": 5, "size": 9, "bold": True, "color": BLUE,
             "font": font, "align": "center", "pages": "last"},
            {"type": "qr", "data": "{memo_number}", "x": 172, "y": 250, "size": 24, "pages": "last", "optional": True},
        ],
    }


# Business presets only change labels/units/columns; the user can still edit everything.
PRESETS = {
    "Computer & Electronics": {"thank_you": "Thank you for shopping with us!", "terms": "Warranty as per product policy. No return after use."},
    "Grocery": {"thank_you": "Thank you, visit again!", "terms": "Goods once sold will not be taken back."},
    "Pharmacy": {"thank_you": "Get well soon.", "terms": "Medicines will not be returned or exchanged."},
    "Repair & Service": {"thank_you": "Thank you for trusting us.", "terms": "Service warranty applies only to the repaired part."},
}


def sample_payload():
    items = [{"sn": 1, "name": "Sample Product", "description": "", "qty": "1", "unit": "Pcs", "price": "1000", "discount": "0", "total": "1000"},
             {"sn": 2, "name": "Another Item", "description": "with description", "qty": "2", "unit": "Pcs", "price": "500", "discount": "50", "total": "950"}]
    totals = {"subtotal": "1950", "overall_discount": "0", "vat": "97.50", "tax": "0", "delivery": "0", "service": "0", "other_charges": "0",
              "rounding_adjustment": "0", "grand_total": "2047.50", "previous_due": "0", "paid": "1000", "current_due": "1047.50"}
    return {"items": items, "totals": totals}


SAMPLE_DOC = {"number": "CM-000001", "issued_at": "2026-01-01T10:30:00", "customer_name": "Sample Customer",
              "customer_phone": "01700000000", "customer_address": "Dhaka", "payment_method": "bKash"}
