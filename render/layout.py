"""Layout engine: template + context -> pages of drawing primitives (mm). Backend-agnostic, so the
preview, PDF, image and printer outputs all come from the same layout (what you see is what prints)."""
import re
from templates_lib.model import page_size, validate

PT_MM = 25.4 / 72
_PH = re.compile(r"\{(\w+)\}")


def fill(text, ctx):
    return _PH.sub(lambda m: str(ctx.get(m.group(1), "")), text)


def wrap(text, width_mm, measure):
    lines = []
    for para in str(text).split("\n"):
        cur = ""
        for word in para.split(" "):
            trial = word if not cur else cur + " " + word
            if measure(trial) <= width_mm or not cur:
                cur = trial
                while measure(cur) > width_mm and len(cur) > 1:  # break very long words
                    k = len(cur)
                    while k > 1 and measure(cur[:k]) > width_mm: k -= 1
                    lines.append(cur[:k]); cur = cur[k:]
            else:
                lines.append(cur); cur = word
        lines.append(cur)
    return lines


def _text_prims(e, ctx, measure_fn, x=None, y=None, w=None, h=None):
    text = fill(e["text"], ctx)
    font, bold = e.get("font", "Helvetica"), e.get("bold", False)
    size = float(e.get("size", 10))
    x = e["x"] if x is None else x; y = e["y"] if y is None else y
    w = e.get("w", 50) if w is None else w; h = e.get("h", 6) if h is None else h
    while True:  # shrink-to-fit so text is never clipped
        m = lambda s: measure_fn(s, font, size, bold)
        lines = wrap(text, w, m)
        lh = size * PT_MM * 1.25
        if len(lines) * lh <= h + 0.01 or size <= 6:
            break
        size -= 0.5
    return [{"t": "text", "x": x, "y": y + i * lh, "w": w, "text": ln, "font": font, "size": size, "bold": bold,
             "color": e.get("color", "#000000"), "align": e.get("align", "left")} for i, ln in enumerate(lines)], len(lines) * lh


def _fit_image(e, images):
    from PIL import Image
    path = images.get(e["src"], e["src"])
    try:
        with Image.open(path) as im:
            iw, ih = im.size
    except Exception:
        return None
    bw, bh = e["w"], e["h"]
    if e.get("keep_aspect", True):
        s = min(bw / iw, bh / ih); w, h = iw * s, ih * s
    else:
        w, h = bw, bh
    al = e.get("align", "left")
    x = e["x"] + (0 if al == "left" else (bw - w) / 2 if al == "center" else bw - w)
    return {"t": "image", "x": x, "y": e["y"] + (bh - h) / 2, "w": w, "h": h, "path": path}


def _simple(e, ctx, measure_fn, images):
    t = e["type"]
    if t == "text":
        return _text_prims(e, ctx, measure_fn)[0]
    if t == "rect":
        return [{"t": "rect", "x": e["x"], "y": e["y"], "w": e["w"], "h": e["h"], "fill": e.get("fill"),
                 "stroke": e.get("stroke"), "lw": e.get("lw", 0.2), "r": e.get("radius", 0)}]
    if t == "polygon":
        return [{"t": "poly", "points": e["points"], "fill": e.get("fill"), "stroke": e.get("stroke"), "lw": e.get("lw", 0.2)}]
    if t == "checkbox":  # small square + label; filled when ctx payment_method matches
        sz = e.get("size_mm", 3.4)
        on = e.get("method") and ctx.get("payment_method") == e["method"]
        out = [{"t": "rect", "x": e["x"], "y": e["y"], "w": sz, "h": sz, "fill": None, "stroke": e.get("color", "#000000"), "lw": 0.25, "r": 0.4}]
        if on:
            out.append({"t": "rect", "x": e["x"] + sz * 0.22, "y": e["y"] + sz * 0.22, "w": sz * 0.56, "h": sz * 0.56, "fill": e.get("color", "#000000"), "stroke": None, "lw": 0, "r": 0.2})
        ps, _ = _text_prims({"text": e["label"], "font": e.get("font", "Helvetica"), "size": e.get("size", 9), "color": "#000000"}, {}, measure_fn,
                            e["x"] + sz + 1.2, e["y"] - 0.4, e.get("w", 25), sz + 1)
        return out + ps
    if t == "line":
        return [{"t": "line", "x": e["x"], "y": e["y"], "x2": e["x2"], "y2": e["y2"], "color": e.get("color", "#000000"), "lw": e.get("lw", 0.2), "dash": e.get("dash", False)}]
    if t == "image":
        p = _fit_image(e, images); return [p] if p else []
    if t == "qr":
        d = fill(e["data"], ctx)
        return [{"t": "qr", "x": e["x"], "y": e["y"], "size": e["size"], "data": d}] if d else []
    if t == "barcode":
        d = fill(e["data"], ctx)
        return [{"t": "barcode", "x": e["x"], "y": e["y"], "w": e["w"], "h": e["h"], "data": d}] if d else []
    return []


def _totals(page, e, ctx, measure_fn, x0, y):
    rh, w, font = e.get("row_h", 6), e["w"], e.get("font", "Helvetica")
    lw_ = w * e.get("label_frac", 0.5)
    for r in e["rows"]:
        hl = r["key"] in e.get("bold_keys", [])
        if e.get("boxed"):
            pad = e.get("gap", 1.2)
            lab_bg = e.get("hl_bg") if hl else e.get("label_bg")
            page.append({"t": "rect", "x": x0, "y": y, "w": lw_, "h": rh, "fill": lab_bg, "stroke": None, "lw": 0, "r": e.get("radius", 1.5)})
            page.append({"t": "rect", "x": x0 + lw_, "y": y, "w": w - lw_, "h": rh, "fill": "#FFFFFF", "stroke": e.get("box_color", "#999999"), "lw": 0.3, "r": e.get("radius", 1.5)})
            ps, _ = _text_prims({"text": r["label"], "font": font, "size": e.get("size", 10), "bold": True, "color": e.get("label_color", "#FFFFFF")}, {}, measure_fn, x0 + 2, y + (rh - e.get("size", 10) * PT_MM) / 2 - 0.3, lw_ - 3, rh)
            page.extend(ps)
            ps, _ = _text_prims({"text": ctx.get(r["key"], ""), "font": font, "size": e.get("size", 10), "bold": hl, "align": "right", "color": "#000000"}, {}, measure_fn, x0 + lw_, y + (rh - e.get("size", 10) * PT_MM) / 2 - 0.3, w - lw_ - 2, rh)
            page.extend(ps)
            y += rh + pad
        else:
            for text, x, wd, al in ((r["label"], x0, w * 0.5, "left"), (ctx.get(r["key"], ""), x0 + w * 0.5, w * 0.5, "right")):
                ps, _ = _text_prims({"text": text, "font": font, "size": e.get("size", 10), "bold": hl, "align": al, "color": "#000000"}, {}, measure_fn, x, y, wd - 1, rh)
                page.extend(ps)
            page.append({"t": "line", "x": x0, "y": y + rh, "x2": x0 + w, "y2": y + rh, "color": "#999999", "lw": 0.1})
            y += rh
    return y


def layout(template, ctx, measure_fn, images=None):
    validate(template)
    images = images or {}
    pg = template["page"]
    W, H = page_size(pg)
    margin = float(pg.get("margin_mm", 10))
    reserve = float(pg.get("footer_reserve_mm", 40))
    pages = [[]]

    table = next((e for e in template["elements"] if e["type"] == "table"), None)
    y_end = margin
    if table:
        font, size = table.get("font", "Helvetica"), float(table.get("font_size", 9))
        cols = table["columns"]
        scale = table["w"] / sum(c["width_mm"] for c in cols)
        widths = [c["width_mm"] * scale for c in cols]
        pad = 1.2
        xs = [table["x"] + sum(widths[:i]) for i in range(len(cols))]
        bc, bw = table.get("border_color", "#000000"), table.get("border_w", 0.2)
        bottom = H - margin - reserve  # keep footer area free on every page

        def header(page, y):
            hh = table.get("header_h", 8)
            for c, x, w in zip(cols, xs, widths):
                page.append({"t": "rect", "x": x, "y": y, "w": w, "h": hh, "fill": table.get("header_bg"), "stroke": bc, "lw": bw})
                ps, _ = _text_prims({"text": c["label"], "font": font, "size": size, "bold": True, "color": table.get("header_color", "#000000"),
                                     "align": "center"}, {}, measure_fn, x + pad, y + (hh - size * PT_MM) / 2, w - 2 * pad, hh)
                page.extend(ps)
            return y + hh

        rows = list(ctx.get("items", []))
        n_blank = max(0, int(table.get("min_rows", 0)) - len(rows))
        base = len(rows)
        rows += [dict({"sn": str(base + i + 1)} if table.get("number_blank_rows") else {}, _blank=True) for i in range(n_blank)]
        y = header(pages[-1], table["y"]); idx = 0
        for r in rows:
            cells = []
            for c, w in zip(cols, widths):
                txt = str(r.get(c["key"], ""))
                if c["key"] == "name" and r.get("description"):
                    txt += "\n" + r["description"]
                cells.append(wrap(txt, w - 2 * pad, lambda s: measure_fn(s, font, size, False)) if txt else [""])
            lh = size * PT_MM * 1.25
            rh = max(table.get("row_h", 7), max(len(c) for c in cells) * lh + 2 * pad)
            if r.get("_blank") and y + rh > bottom:
                break  # padding rows never force a new page
            if y + rh > bottom:
                pages.append([]); y = header(pages[-1], table.get("continue_y", margin))
            pg_ = pages[-1]
            fill_c = table.get("alt_row_bg") if idx % 2 == 1 else None
            for c, x, w, lines in zip(cols, xs, widths, cells):
                pg_.append({"t": "rect", "x": x, "y": y, "w": w, "h": rh, "fill": fill_c, "stroke": bc, "lw": bw})
                for i, ln in enumerate(lines):
                    if ln:
                        pg_.append({"t": "text", "x": x + pad, "y": y + pad + i * lh, "w": w - 2 * pad, "text": ln, "font": font,
                                    "size": size, "bold": False, "color": "#000000", "align": c.get("align", "left")})
            y += rh; idx += 1
        y_end = y

    # totals: flow after the table, or fixed on the last page when the element has its own "y"
    fixed_totals = []
    for e in [e for e in template["elements"] if e["type"] == "totals"]:
        rh = e.get("row_h", 6)
        if "y" in e:
            fixed_totals.append(e); continue
        need = rh * len(e["rows"]) + 3
        if y_end + 3 + need > H - margin - reserve:
            pages.append([]); y_end = margin
        y_end = _totals(pages[-1], e, ctx, measure_fn, e["x"], y_end + 3)
    for e in fixed_totals:
        _totals(pages[-1], e, ctx, measure_fn, e["x"], e["y"])

    first, last, n = 0, len(pages) - 1, len(pages)
    for e in template["elements"]:
        if e["type"] in ("table", "totals"):
            continue
        which = e.get("pages", "first")
        targets = {"first": [first], "last": [last], "all": list(range(n))}[which]
        for pi in targets:
            pages[pi].extend(_simple(e, ctx, measure_fn, images))

    bg, border = pg.get("bg_color", "#FFFFFF"), pg.get("border")
    out = []
    for prims in pages:
        head = [{"t": "rect", "x": 0, "y": 0, "w": W, "h": H, "fill": bg, "stroke": None, "lw": 0}]
        if border and border.get("width", 0) > 0:
            head.append({"t": "rect", "x": margin / 2, "y": margin / 2, "w": W - margin, "h": H - margin, "fill": None,
                         "stroke": border.get("color", "#000000"), "lw": border["width"]})
        out.append({"w": W, "h": H, "prims": head + prims})
    return out
