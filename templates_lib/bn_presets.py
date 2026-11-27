"""18 ready-made Bengali shop templates (generated from a small spec, fully editable in Template Studio).
All shop details come from Settings placeholders ({business_name}, {business_subtitle}, {address}, {phone}),
so every template automatically shows the user's own shop information."""
import copy

FONT = "Noto Sans Bengali"
PALETTES = {  # dark, accent, light
    "blue": ("#0B2A5B", "#0B6BCB", "#EAF2FB"), "green": ("#0F4D2E", "#1E9E5A", "#E8F6EE"), "maroon": ("#5C1020", "#C0392B", "#FCEDEE"),
    "teal": ("#0B4F5C", "#13A3B8", "#E6F6F8"), "orange": ("#7A3B00", "#F28C28", "#FFF3E3"), "purple": ("#3B1F6E", "#7B4FD6", "#F0EAFB"),
    "gold": ("#1A1A1A", "#C9A227", "#FBF6E3"), "red": ("#8B0000", "#E53935", "#FDECEA"), "slate": ("#263238", "#546E7A", "#ECEFF1"),
}
SIZES = {  # W, H, font factor, margin, base row height
    "A4": (210, 297, 1.0, 8, 7.6), "A5": (148, 210, 0.82, 6, 6.6), "A5L": (210, 148, 0.8, 6, 6.2), "A6": (105, 148, 0.64, 4, 5.6)}
L = {"bn": dict(sn="ক্রমিক নং", name="পণ্যের বিবরণ", qty="পরিমাণ", unit="একক", price="একক মূল্য (৳)", disc="ছাড় (৳)", total="মোট মূল্য (৳)",
                no="নং :", date="তারিখ :", cname="গ্রাহকের নাম :", phone="ফোন :", addr="ঠিকানা :", pay="পেমেন্টের ধরন :",
                cash="নগদ", card="কার্ড", bkash="বিকাশ", other="অন্যান্য", note="নোটঃ", sig="স্বাক্ষর",
                subtotal="মোট মূল্য (৳)", discount="ডিসকাউন্ট (৳)", vat="ভ্যাট (৳)", grand="সর্বমোট (৳)", paid="পরিশোধিত (৳)", due="বাকি (৳)"),
     "en": dict(sn="SL", name="Description", qty="Qty", unit="Unit", price="Unit Price", disc="Discount", total="Total", no="No:", date="Date:",
                cname="Customer:", phone="Phone:", addr="Address:", pay="Payment:", cash="Cash", card="Card", bkash="bKash", other="Other", note="Note:",
                sig="Signature", subtotal="Subtotal", discount="Discount", vat="VAT", grand="Grand Total", paid="Paid", due="Due")}

NOTES = {
    "general": ["পণ্যের গ্যারান্টি শুধুমাত্র নির্দিষ্ট শর্তে প্রযোজ্য।", "বিক্রীত পণ্য ফেরত বা বদল করতে বিল সাথে আনুন।", "বিল সংরক্ষণ করুন, ভবিষ্যৎ সেবার জন্য প্রয়োজন হতে পারে।"],
    "electronics": ["পণ্যের গ্যারান্টি শুধুমাত্র নির্দিষ্ট শর্তে প্রযোজ্য।", "পণ্য ফেরতের ক্ষেত্রে ৩ দিনের মধ্যে জানাতে হবে।", "ব্যবহৃত (সেকেন্ড হ্যান্ড) পণ্য ফেরতযোগ্য নয়।", "বিল সংরক্ষণ করুন, ভবিষ্যৎ সেবার জন্য প্রয়োজন হতে পারে।"],
    "repair": ["মেরামতের পর ৭ দিনের সার্ভিস ওয়ারেন্টি (শুধু মেরামতকৃত অংশে)।", "পানি/আঘাতজনিত ক্ষতিতে ওয়ারেন্টি প্রযোজ্য নয়।", "৩০ দিনের মধ্যে ডিভাইস না নিলে দোকান দায়ী থাকবে না।"],
    "grocery": ["বিক্রীত মালামাল ফেরত নেওয়া হয় না।", "পচনশীল পণ্য ক্রয়ের সময়ই দেখে নিন।", "বিল ছাড়া অভিযোগ গ্রহণযোগ্য নয়।"],
    "pharmacy": ["বিক্রীত ওষুধ ফেরত বা বদল করা হয় না।", "ওষুধ সেবনের আগে চিকিৎসকের পরামর্শ নিন।", "মেয়াদোত্তীর্ণ তারিখ দেখে ওষুধ নিন।"],
    "hardware": ["মালামাল বুঝে নিয়ে যাবেন, পরে অভিযোগ গ্রহণযোগ্য নয়।", "কাটা/কাস্টম সাইজের মাল ফেরতযোগ্য নয়।", "প্রস্তুতকারকের ওয়ারেন্টি প্রযোজ্য।"],
    "cloth": ["কাটা কাপড় ফেরত বা বদল হবে না।", "রং ও মাপ কেনার সময়ই দেখে নিন।", "পণ্য বদলের জন্য ৩ দিনের মধ্যে বিলসহ আসুন।"],
    "stationery": ["বিক্রীত মালামাল ফেরত নেওয়া হয় না।", "পণ্য ত্রুটিপূর্ণ হলে ২৪ ঘণ্টার মধ্যে জানান।", "বিল সংরক্ষণ করুন।"],
    "wholesale": ["পাইকারি মূল্যে বিক্রীত মাল ফেরতযোগ্য নয়।", "বাকির ক্ষেত্রে নির্ধারিত তারিখে পরিশোধ করতে হবে।", "মাল বুঝে নিয়ে বিল স্বাক্ষর করুন।"],
    "photo": ["ডিজাইন/ছবির সফট কপি ৭ দিন সংরক্ষিত থাকবে।", "অগ্রিম টাকা ফেরতযোগ্য নয়।", "প্রিন্ট বুঝে নিয়ে যাবেন।"],
    "sweet": ["টাটকা খাবার, দ্রুত খেয়ে ফেলুন।", "বিক্রীত খাবার ফেরত নেওয়া হয় না।", "অর্ডার দেওয়া খাবারের অগ্রিম ফেরত হবে না।"],
    "gift": ["বিক্রীত পণ্য ৩ দিনের মধ্যে বিলসহ বদল করা যাবে।", "ব্যবহৃত বা ক্ষতিগ্রস্ত পণ্য বদলযোগ্য নয়।", "বিল সংরক্ষণ করুন।"],
}

# (name, kind, size, header, palette, notes key, cols, thanks, trust)
SPECS = [
    ("রিপন ক্লাসিক (কম্পিউটার ও ইলেকট্রনিক্স)", "memo", "A4", "corner", "blue", "electronics", "basic", ("Thank You", "For Shopping With Us"), "আপনার আস্থা আমাদের শক্তি"),
    ("কম্পিউটার সার্ভিস ও রিপেয়ার", "memo", "A5", "band", "teal", "repair", "unit", ("ধন্যবাদ!", "আবার সেবা নিতে আসবেন"), "দ্রুত ও নির্ভরযোগ্য সার্ভিস"),
    ("মোবাইল ও অ্যাক্সেসরিজ", "memo", "A5", "corner", "orange", "electronics", "basic", ("Thank You", "For Shopping With Us"), "আপনার আস্থা আমাদের শক্তি"),
    ("মুদি দোকান (গ্রোসারি)", "memo", "A5", "band", "green", "grocery", "unit", ("ধন্যবাদ!", "আবার আসবেন"), "সততাই আমাদের মূলধন"),
    ("ফার্মেসি / ওষুধের দোকান", "memo", "A5", "center", "red", "pharmacy", "unit", ("ধন্যবাদ!", "সুস্থ থাকুন"), "আপনার সুস্বাস্থ্যই আমাদের লক্ষ্য"),
    ("হার্ডওয়্যার ও স্যানিটারি", "memo", "A4", "band", "slate", "hardware", "unit", ("ধন্যবাদ!", "আবার আসবেন"), "মানসম্মত মালের নিশ্চয়তা"),
    ("ইলেকট্রিক্যাল শপ", "memo", "A5", "corner", "gold", "electronics", "basic", ("ধন্যবাদ!", "আবার আসবেন"), "নিরাপদ ও মানসম্মত পণ্য"),
    ("কাপড়ের দোকান", "memo", "A5", "center", "purple", "cloth", "basic", ("ধন্যবাদ!", "আবার আসবেন"), "পছন্দের কাপড়, সঠিক দামে"),
    ("স্টেশনারি ও বই", "memo", "A5", "corner", "teal", "stationery", "unit", ("ধন্যবাদ!", "আবার আসবেন"), "আপনার আস্থা আমাদের শক্তি"),
    ("পাইকারি (হোলসেল)", "memo", "A4", "band", "maroon", "wholesale", "discount", ("ধন্যবাদ!", "ব্যবসায় আপনার পাশে আছি"), "সর্বনিম্ন দামে সেরা মাল"),
    ("খুচরা (রিটেইল) সাধারণ", "memo", "A5", "center", "blue", "general", "basic", ("ধন্যবাদ!", "আবার আসবেন"), "আপনার আস্থা আমাদের শক্তি"),
    ("ফটোকপি ও ফটোস্টুডিও (ল্যান্ডস্কেপ)", "memo", "A5L", "band", "teal", "photo", "basic", ("ধন্যবাদ!", "আবার আসবেন"), "দ্রুত ও মানসম্মত সার্ভিস"),
    ("সাধারণ ব্যবসা (ছোট স্লিপ A6)", "memo", "A6", "compact", "blue", "general", "basic", ("ধন্যবাদ!", ""), "আপনার আস্থা আমাদের শক্তি"),
    ("মিনি স্লিপ গ্রোসারি (A6)", "memo", "A6", "compact", "green", "grocery", "basic", ("ধন্যবাদ!", ""), "সততাই আমাদের মূলধন"),
    ("উপহার ও গিফট শপ (প্রিমিয়াম)", "memo", "A4", "center", "gold", "gift", "unit", ("ধন্যবাদ!", "আবার আসবেন"), "সেরা উপহার, সেরা সেবা"),
    ("মিষ্টি ও বেকারি", "memo", "A5", "center", "maroon", "sweet", "unit", ("ধন্যবাদ!", "আবার আসবেন"), "মিষ্টিমুখে ভালোবাসা"),
    ("ইনভয়েস / বিল (ভ্যাটসহ)", "invoice", "A4", "corner", "blue", "wholesale", "discount", ("ধন্যবাদ!", "আপনার ব্যবসার জন্য কৃতজ্ঞ"), "আপনার আস্থা আমাদের শক্তি"),
    ("টাকা প্রাপ্তির রশিদ (রিসিট)", "receipt", "A5L", "band", "navy" if False else "blue", "general", "basic", ("ধন্যবাদ!", ""), "আপনার আস্থা আমাদের শক্তি"),
]


def _t(text, x, y, w, h, size, color="#000000", bold=False, align="left", pages="first", **kw):
    d = {"type": "text", "text": text, "x": round(x, 2), "y": round(y, 2), "w": round(w, 2), "h": round(h, 2), "size": round(size, 2),
         "color": color, "bold": bold, "align": align, "font": FONT, "pages": pages}
    d.update(kw); return d


def _rect(x, y, w, h, fill=None, stroke=None, r=0, lw=0.3, pages="first"):
    return {"type": "rect", "x": round(x, 2), "y": round(y, 2), "w": round(w, 2), "h": round(h, 2), "fill": fill, "stroke": stroke, "lw": lw, "radius": r, "pages": pages}


def _line(x, y, x2, color, lw=0.25, dash=False, pages="first"):
    return {"type": "line", "x": round(x, 2), "y": round(y, 2), "x2": round(x2, 2), "y2": round(y, 2), "color": color, "lw": lw, "dash": dash, "pages": pages}


def _poly(pts, fill, pages="first"):
    return {"type": "polygon", "points": [[round(a, 2), round(b, 2)] for a, b in pts], "fill": fill, "pages": pages}


def build(spec, lang="bn"):
    name, kind, size, hdr, pal, nkey, cols, thanks, trust = spec
    D, A, LT = PALETTES[pal]; W, H, f, m, rh = SIZES[size]; T = L[lang]; E = []
    cw = W - 2 * m

    # ---------- header
    if hdr == "corner":
        E += [_poly([(0, 0), (34 * f, 0), (0, 22 * f)], A), _poly([(0, 0), (20 * f, 0), (0, 12 * f)], D),
              _poly([(W, 0), (W - 46 * f, 0), (W, 27 * f)], D), _poly([(W, 0), (W - 27 * f, 0), (W, 15 * f)], A)]
        lw_ = 36 * f
        E += [{"type": "image", "src": "logo", "x": m + 2, "y": 8 * f, "w": lw_, "h": 24 * f, "align": "center", "pages": "first"},
              _line(m + 2 + lw_ + 3, 9 * f, m + 2 + lw_ + 3, D, 0.5)]
        E[-1]["y2"] = 31 * f
        nx = m + lw_ + 10
        E += [_t("{business_name}", nx, 8 * f, W - nx - 52 * f, 17 * f, 30 * f, D, True),
              _rect(W - m - 44 * f, 12 * f, 44 * f, 13 * f, D, None, 4 * f), _t("{business_subtitle}", W - m - 42 * f, 14.2 * f, 40 * f, 9 * f, 8.5 * f, "#FFFFFF", True, "center")]
        E += [_t("{address}     |     {phone}", m, 35 * f, cw, 8 * f, 13 * f, D, True, "center"), _line(m, 44.5 * f, W - m, A, 0.5)]
        y = 47 * f
    elif hdr == "band":
        hh = 30 * f
        E += [_rect(0, 0, W, hh, D), _rect(m, 4 * f, 30 * f, hh - 8 * f, "#FFFFFF", None, 3), {"type": "image", "src": "logo", "x": m + 1.5, "y": 5 * f, "w": 27 * f, "h": hh - 10 * f, "align": "center", "pages": "first"}]
        nx = m + 34 * f
        E += [_t("{business_name}", nx, 4 * f, W - nx - m, 13 * f, 24 * f, "#FFFFFF", True), _t("{business_subtitle}", nx, 15.5 * f, W - nx - m, 5.5 * f, 9 * f, A if pal in ("gold",) else "#BFE6F5", True),
              _t("{address}   |   {phone}", nx, 21.5 * f, W - nx - m, 6 * f, 10 * f, "#FFFFFF", True), _rect(0, hh, W, 1.6 * f, A)]
        y = hh + 5 * f
    elif hdr == "center":
        E += [{"type": "image", "src": "logo", "x": W / 2 - 17 * f, "y": 5 * f, "w": 34 * f, "h": 16 * f, "align": "center", "pages": "first"},
              _t("{business_name}", m, 21 * f, cw, 11 * f, 23 * f, D, True, "center"), _t("{business_subtitle}", m, 32 * f, cw, 5.5 * f, 9.5 * f, A, True, "center"),
              _line(m, 38.5 * f, W - m, D, 0.6), _line(m, 39.7 * f, W - m, A, 0.25),
              _t("{address}   |   {phone}", m, 41 * f, cw, 6.5 * f, 11 * f, D, True, "center")]
        y = 49 * f
    else:  # compact
        E += [_rect(0, 0, W, 2.2, D), {"type": "image", "src": "logo", "x": m, "y": 4.5, "w": 15, "h": 10, "align": "center", "pages": "first"},
              _t("{business_name}", m + 17, 4, cw - 17, 6.5, 14, D, True), _t("{address}", m + 17, 10.2, cw - 17, 4, 6.8, "#333333", False),
              _t("{phone}", m + 17, 14, cw - 17, 4, 8, D, True), _line(m, 19.5, W - m, A, 0.4)]
        y = 21.5
    top = y - 2

    # ---------- title row
    title = {"memo": "ক্যাশ মেমো", "invoice": "ইনভয়েস / বিল", "receipt": "টাকা প্রাপ্তির রশিদ"}[kind] if lang == "bn" else {"memo": "CASH MEMO", "invoice": "INVOICE", "receipt": "MONEY RECEIPT"}[kind]
    tw = 52 * f if kind != "receipt" else 66 * f
    E += [_rect(m, y, tw, 9.5 * f, D, None, 4.7 * f), _t(title, m + 2, y + 1.6 * f, tw - 4, 7 * f, 16 * f, "#FFFFFF", True, "center")]
    fx = m + tw + 6 * f; half = (W - m - fx)
    E += [_t(T["no"], fx, y + 3 * f, 10 * f, 5 * f, 10.5 * f, D, True), _t("{memo_number}", fx + 10 * f, y + 3 * f, half * 0.42 - 10 * f, 5 * f, 10.5 * f),
          _line(fx + 9 * f, y + 8.4 * f, fx + half * 0.45, D, 0.25),
          _t(T["date"], fx + half * 0.5, y + 3 * f, 15 * f, 5 * f, 10.5 * f, D, True), _t("{date}", fx + half * 0.5 + 15 * f, y + 3 * f, half * 0.5 - 15 * f, 5 * f, 10.5 * f),
          _line(fx + half * 0.5 + 14 * f, y + 8.4 * f, W - m, D, 0.25)]
    y += 12.5 * f

    # ---------- customer box
    ch = 29 * f if kind != "receipt" else 36 * f
    E.append(_rect(m, y, cw, ch, LT, None, 3))
    lx, hw = m + 3, cw * 0.58
    if kind == "receipt":
        rows = [(T["cname"], "{customer_name}"), (T["phone"], "{customer_phone}"), (T["addr"], "{customer_address}")]
        for i, (lab, val) in enumerate(rows):
            yy = y + 2.5 * f + i * 8 * f
            E += [_t(lab, lx, yy, 30 * f, 5 * f, 10 * f, D, True), _t(val, lx + 31 * f, yy, cw - 35 * f - 31 * f, 5 * f, 10 * f), _line(lx + 30 * f, yy + 5.6 * f, W - m - 3, "#777777", 0.2)]
        yy = y + 2.5 * f + 3 * 8 * f
    else:
        E += [_t(T["cname"], lx, y + 3 * f, 27 * f, 5 * f, 9.5 * f, D, True), _t("{customer_name}", lx + 27 * f, y + 3 * f, hw - 30 * f, 5 * f, 9.5 * f), _line(lx + 26 * f, y + 8.4 * f, m + hw, "#777777", 0.2),
              _t(T["phone"], m + hw + 5, y + 3 * f, 12 * f, 5 * f, 9.5 * f, D, True), _t("{customer_phone}", m + hw + 5 + 12 * f, y + 3 * f, cw - hw - 22 * f, 5 * f, 9.5 * f), _line(m + hw + 4 + 11 * f, y + 8.4 * f, W - m - 3, "#777777", 0.2),
              _t(T["addr"], lx, y + 11.2 * f, 22 * f, 5 * f, 9.5 * f, D, True), _t("{customer_address}", lx + 22 * f, y + 11.2 * f, cw - 28 * f, 5 * f, 9.5 * f), _line(lx + 21 * f, y + 16.6 * f, W - m - 3, "#777777", 0.2)]
        yy = y + 20.2 * f
    px = lx
    E.append(_t(T["pay"], px, yy, 28 * f, 5 * f, 8.5 * f, D, True))
    cx = px + 30 * f
    for lab, meth in ((T["cash"], "Cash"), (T["card"], "Debit/Credit Card"), (T["bkash"], "bKash"), (T["other"], "Other")):
        wlab = max(10 * f, 2.2 * f * len(lab) + 2)
        E.append({"type": "checkbox", "x": round(cx, 2), "y": round(yy + 0.4, 2), "label": lab, "method": meth, "size": 8.3 * f, "size_mm": 3.3 * f, "color": D, "font": FONT, "w": wlab, "pages": "first"})
        cx += 3.3 * f + 1.2 + wlab + 2 * f
    y += ch + 4 * f
    ty = y

    # ---------- footer geometry
    bottom_h = 21 * f
    notes_h = (50 if kind == "invoice" else 34) * f
    foot_h = notes_h + 3 * f + bottom_h + 2 * f
    fy = H - m - foot_h

    if kind != "receipt":
        spec_cols = [("sn", "sn", 13, "center"), ("name", "name", 86, "left")]
        if cols in ("unit", "discount"): spec_cols += [("qty", "qty", 18, "center"), ("unit", "unit", 15, "center")]
        else: spec_cols += [("qty", "qty", 20, "center")]
        spec_cols += [("price", "price", 28, "right")]
        if cols == "discount": spec_cols += [("discount", "disc", 22, "right")]
        spec_cols += [("total", "total", 30, "right")]
        columns = [{"key": k, "label": T[lab], "width_mm": w_, "align": al} for k, lab, w_, al in spec_cols]
        hh_ = 9 * f; avail = (fy - 1) - (ty + hh_)
        E.append({"type": "table", "x": m, "y": round(ty, 2), "w": cw, "columns": columns, "font": FONT, "font_size": round(10 * f, 2), "header_bg": D, "header_color": "#FFFFFF",
                  "alt_row_bg": LT, "row_h": rh, "header_h": round(hh_, 2), "border_color": A, "border_w": 0.2, "min_rows": int(avail / rh - 1e-6), "number_blank_rows": True,
                  "continue_y": m + 2, "pages": "all"})
    # frame around body
    E.insert(0, _rect(m - 2.5, top, cw + 5, H - m + 2.5 - top, None, A, 4, 0.5, "all"))

    # ---------- notes + totals
    ny = fy + 1
    nw = cw * 0.57
    if kind == "receipt":
        nw = cw * 0.5
    E.append(_rect(m, ny, nw, notes_h, LT, None, 3, 0.3, "last"))
    E.append(_t(T["note"], m + 3, ny + 1.5 * f, nw - 6, 6 * f, 11 * f, D, True, pages="last"))
    E.append(_t("\n".join("• " + n for n in NOTES[nkey]), m + 3, ny + 8 * f, nw - 6, notes_h - 9 * f, 8.2 * f, "#222222", pages="last"))
    if kind == "invoice":
        rows = [("subtotal", T["subtotal"]), ("overall_discount", T["discount"]), ("vat", T["vat"]), ("grand_total", T["grand"]), ("paid", T["paid"]), ("current_due", T["due"])]
        hl = ["grand_total"]
    elif kind == "receipt":
        rows = [("grand_total", T["subtotal"]), ("paid", T["paid"]), ("current_due", T["due"])]; hl = ["paid"]
    else:
        rows = [("subtotal", T["subtotal"]), ("overall_discount", T["discount"]), ("grand_total", T["grand"])]; hl = ["grand_total"]
    gap = 1.4 * f; trh = min(9 * f, (notes_h - gap * (len(rows) - 1)) / len(rows))
    tx = m + nw + 3
    E.append({"type": "totals", "x": round(tx, 2), "y": round(ny, 2), "w": round(W - m - tx, 2), "font": FONT, "size": round(10.5 * f, 2), "row_h": round(trh, 2), "boxed": True, "gap": round(gap, 2),
              "label_bg": D, "hl_bg": A, "label_color": "#FFFFFF", "box_color": A, "label_frac": 0.52, "radius": 1.8,
              "bold_keys": hl, "rows": [{"label": lab, "key": k} for k, lab in rows]})

    # ---------- bottom row
    by = ny + notes_h + 3 * f
    if kind == "receipt":
        E += [_t(thanks[0], m, by + 1, 55 * f, 9 * f, 17 * f, A, True, pages="last")]
    else:
        E += [_t(thanks[0], m + 2, by, 60 * f, 11 * f, 22 * f, A, True, pages="last")]
        if thanks[1]: E.append(_t(thanks[1], m + 2, by + 11.5 * f, 70 * f, 6 * f, 9.5 * f, D, True, pages="last"))
    tw_ = 52 * f; tx2 = W / 2 - tw_ / 2 + (6 * f if size != "A6" else 0)
    E += [_rect(tx2, by + 1.5 * f, tw_, 13 * f, D, None, 3, 0.3, "last"), _t(trust, tx2 + 2, by + 2.8 * f, tw_ - 4, 10 * f, 9.5 * f, "#FFFFFF", True, "center", "last")]
    sx = W - m - 44 * f
    E += [_line(sx, by + 9 * f, W - m - 2, "#555555", 0.3, True, "last"), _t(T["sig"], sx, by + 10.5 * f, 42 * f, 6 * f, 10 * f, D, True, "center", "last")]
    if kind == "invoice":
        E.append({"type": "qr", "data": "{memo_number}", "x": round(W * 0.34, 2), "y": round(by + 0.5, 2), "size": round(15 * f, 2), "pages": "last", "optional": True})
    if size in ("A4",) and hdr == "corner":
        E += [_poly([(W, H), (W - 42 * f, H), (W, H - 24 * f)], D, "all"), _poly([(W, H), (W - 24 * f, H), (W, H - 13 * f)], A, "all")]

    return {"name": name, "version": 2, "lang": lang, "doc_type": kind if kind != "invoice" else "invoice",
            "page": {"size": {"A5L": "A5"}.get(size, size), "orientation": "landscape" if size == "A5L" else "portrait", "margin_mm": m, "bg_color": "#FFFFFF",
                     "border": {"width": 0}, "footer_reserve_mm": round(foot_h, 2)},
            "elements": E}


def all_templates(lang="bn"):
    return [build(s, lang) for s in SPECS]


# ---------------------------------------------------------------- English version / font override of existing templates
NOTES_EN = {
    "general": ["Warranty applies only under the stated terms.", "Bring this bill to return or exchange a sold item.", "Keep this bill; it may be needed for future service."],
    "electronics": ["Warranty applies only under the stated terms.", "Report returns within 3 days.", "Used (second-hand) items are not returnable.", "Keep this bill; it may be needed for future service."],
    "repair": ["7-day service warranty after repair (repaired part only).", "Water/impact damage is not covered by warranty.", "We are not responsible for devices left over 30 days."],
    "grocery": ["Sold goods are not taken back.", "Check perishable items at the time of purchase.", "No complaint accepted without the bill."],
    "pharmacy": ["Sold medicines cannot be returned or exchanged.", "Consult a doctor before taking medicine.", "Check the expiry date before buying."],
    "hardware": ["Please check goods on delivery; later complaints not accepted.", "Cut/custom-size items are not returnable.", "Manufacturer's warranty applies."],
    "cloth": ["Cut cloth cannot be returned or exchanged.", "Check colour and size at purchase.", "For exchange, come within 3 days with the bill."],
    "stationery": ["Sold goods are not taken back.", "Report defective items within 24 hours.", "Keep this bill."],
    "wholesale": ["Wholesale goods are not returnable.", "Dues must be paid by the agreed date.", "Check goods and sign the bill."],
    "photo": ["Soft copies of designs/photos are kept for 7 days.", "Advance payment is non-refundable.", "Please check your print before leaving."],
    "sweet": ["Fresh food - consume quickly.", "Sold food is not taken back.", "Advance for ordered food is non-refundable."],
    "gift": ["Items can be exchanged within 3 days with the bill.", "Used or damaged items cannot be exchanged.", "Keep this bill."],
}
PHRASES_EN = {  # thanks / trust / titles
    "ধন্যবাদ!": "Thank you!", "আবার সেবা নিতে আসবেন": "Please visit us again for service", "আবার আসবেন": "Please visit again", "সুস্থ থাকুন": "Stay healthy",
    "ব্যবসায় আপনার পাশে আছি": "We are with your business", "আপনার ব্যবসার জন্য কৃতজ্ঞ": "Grateful for your business", "আপনার আস্থা আমাদের শক্তি": "Your trust is our strength",
    "দ্রুত ও নির্ভরযোগ্য সার্ভিস": "Fast & reliable service", "সততাই আমাদের মূলধন": "Honesty is our capital", "আপনার সুস্বাস্থ্যই আমাদের লক্ষ্য": "Your good health is our goal",
    "মানসম্মত মালের নিশ্চয়তা": "Quality goods guaranteed", "নিরাপদ ও মানসম্মত পণ্য": "Safe & quality products", "পছন্দের কাপড়, সঠিক দামে": "Your choice of cloth at the right price",
    "সর্বনিম্ন দামে সেরা মাল": "Best goods at lowest prices", "দ্রুত ও মানসম্মত সার্ভিস": "Fast & quality service", "সেরা উপহার, সেরা সেবা": "Best gifts, best service",
    "মিষ্টিমুখে ভালোবাসা": "Love in every sweet bite", "ক্যাশ মেমো": "CASH MEMO", "ইনভয়েস / বিল": "INVOICE", "টাকা প্রাপ্তির রশিদ": "MONEY RECEIPT",
}
NAMES_EN = ["Ripon Classic (Computer & Electronics)", "Computer Service & Repair", "Mobile & Accessories", "Grocery Store", "Pharmacy / Medicine Shop", "Hardware & Sanitary",
            "Electrical Shop", "Cloth Shop", "Stationery & Books", "Wholesale", "Retail (General)", "Photocopy & Photo Studio (Landscape)", "General Business (A6 slip)",
            "Mini Slip Grocery (A6)", "Gift Shop (Premium)", "Sweets & Bakery", "Invoice / Bill (with VAT)", "Money Receipt"]
NAME_MAP_EN = {s[0]: n for s, n in zip(SPECS, NAMES_EN)}


def display_name(name, lang):
    return NAME_MAP_EN.get(name, name) if lang == "en" else name


def _maps():
    b, e = L["bn"], L["en"]
    gen = {b[k]: e[k] for k in ("no", "date", "cname", "phone", "addr", "pay", "cash", "card", "bkash", "other", "note", "sig")}
    cols = {b[k]: e[k] for k in ("sn", "name", "qty", "unit", "price", "disc", "total")}
    tots = {b[k]: e[k] for k in ("subtotal", "discount", "vat", "grand", "paid", "due")}
    gen.update(PHRASES_EN)
    for key in NOTES:
        for bl, el in zip(NOTES[key], NOTES_EN[key]): gen[bl] = el
    return gen, cols, tots


def prepare_template(tpl, lang=None, font=None):
    """Return a copy of a template with texts translated to English (lang='en') and/or every font replaced.
    Texts the user wrote themselves are left unchanged; Bengali is the stored source language."""
    import copy
    t = copy.deepcopy(tpl); gen, cols, tots = _maps()

    def tr_text(s):
        if s in gen: return gen[s]
        if "\n• " in s or s.startswith("• "):
            return "\n".join("• " + gen.get(l[2:], l[2:]) if l.startswith("• ") else l for l in s.split("\n"))
        return s
    for e in t["elements"]:
        if font and e["type"] in ("text", "checkbox", "totals", "table"): e["font"] = font
        if lang != "en": continue
        if e["type"] == "text": e["text"] = tr_text(e["text"])
        elif e["type"] == "checkbox": e["label"] = gen.get(e["label"], e["label"])
        elif e["type"] == "totals":
            for r in e["rows"]: r["label"] = tots.get(r["label"], r["label"])
        elif e["type"] == "table":
            for c in e["columns"]: c["label"] = cols.get(c["label"], c["label"])
    if lang == "en" and t.get("lang") == "bn":
        t["lang"] = "en"
    return t
