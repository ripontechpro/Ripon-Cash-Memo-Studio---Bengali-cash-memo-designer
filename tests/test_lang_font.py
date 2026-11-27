import glob, os, re, tempfile, unittest
from pathlib import Path


class LangFontTests(unittest.TestCase):
    def test_every_ui_string_has_english(self):
        from ui.strings_en import EN
        missing = []
        for f in glob.glob(str(Path(__file__).resolve().parent.parent / "ui" / "*.py")):
            for m in re.finditer(r'T\("((?:[^"\\\n]|\\.)*)"\)', open(f, encoding="utf-8").read()):
                t = m.group(1).replace("\\n", "\n")
                if t not in EN and t != "৳ ": missing.append(t)
        self.assertEqual(missing, [])

    def test_ui_strings_are_bengali_sources(self):  # no English-only literal wrapped in T()
        for f in glob.glob(str(Path(__file__).resolve().parent.parent / "ui" / "*.py")):
            for m in re.finditer(r'T\("((?:[^"\\\n]|\\.)*)"\)', open(f, encoding="utf-8").read()):
                t = m.group(1)
                if t.strip() and not re.search(r"[\u0980-\u09FF]", t):
                    self.assertTrue(t.strip() in ("৳",), (f, t))

    def test_prepare_template_english_and_font(self):
        from templates_lib.bn_presets import all_templates, prepare_template
        bn = re.compile(r"[\u0980-\u09FF]")
        for t in all_templates("bn"):
            e = prepare_template(t, "en", "Kalpurush")
            for el in e["elements"]:
                if el["type"] in ("text", "checkbox", "totals", "table"): self.assertEqual(el["font"], "Kalpurush")
                if el["type"] == "table":
                    for c in el["columns"]: self.assertFalse(bn.search(c["label"]), (t["name"], c["label"]))
                if el["type"] == "totals":
                    for r in el["rows"]: self.assertFalse(bn.search(r["label"]), (t["name"], r["label"]))
                if el["type"] == "checkbox": self.assertFalse(bn.search(el["label"]))
                if el["type"] == "text" and el["text"].startswith("•"): self.assertFalse(bn.search(el["text"]), (t["name"], el["text"]))
            texts = " ".join(el.get("text", "") for el in e["elements"] if el["type"] == "text")
            self.assertFalse(bn.search(texts.replace("{", "")), (t["name"], texts))

    def test_prepare_keeps_bengali_and_user_text(self):
        from templates_lib.bn_presets import all_templates, prepare_template
        t = all_templates("bn")[0]; t["elements"].append({"type": "text", "text": "আমার নিজের লেখা", "x": 1, "y": 1, "w": 20, "h": 5})
        b = prepare_template(t, "bn", None); self.assertEqual(b["elements"][-1]["text"], "আমার নিজের লেখা")
        e = prepare_template(t, "en", None); self.assertEqual(e["elements"][-1]["text"], "আমার নিজের লেখা")
        self.assertEqual(t["elements"], prepare_template(t, "bn", None)["elements"])  # original untouched / no-op

    def test_english_template_renders_one_page(self):
        from render.context import make_context
        from render.fonts import FontManager
        from render.layout import layout
        from templates_lib.bn_presets import all_templates, prepare_template
        from templates_lib.model import SAMPLE_DOC, sample_payload
        fm = FontManager(); ctx = make_context({"business_name": "Ripon Computer", "address": "x", "phone": "1"}, SAMPLE_DOC, sample_payload())
        for t in all_templates("bn"):
            pages = layout(prepare_template(t, "en"), ctx, lambda a, b, c, d: fm.measure(a, b, c, d), {})
            self.assertEqual(len(pages), 1, t["name"])

    def test_prefs_roundtrip(self):
        tmp = tempfile.mkdtemp(); os.environ["HOME"] = tmp; os.environ["USERPROFILE"] = tmp
        from core import prefs
        self.assertEqual(prefs.get("language"), "bn"); self.assertEqual(prefs.get("ui_scale"), 115)
        prefs.save(language="en", doc_font="Kalpurush")
        self.assertEqual((prefs.get("language"), prefs.get("doc_font")), ("en", "Kalpurush"))

    def test_names_translate(self):
        from templates_lib.bn_presets import SPECS, display_name
        self.assertEqual(display_name(SPECS[3][0], "en"), "Grocery Store"); self.assertEqual(display_name(SPECS[3][0], "bn"), SPECS[3][0])


if __name__ == "__main__":
    unittest.main()
