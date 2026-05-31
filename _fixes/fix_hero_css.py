#!/usr/bin/env python3
"""Convert inline front-matter heroes to the proven CSS !important mechanism."""
import re

HTML = "_layouts/default.html"

# province slug -> image (bare body.<slug> rule; safe: same-name city rules are more specific)
PROV = {
 "dak-lak": "daklakhero.jpg", "hai-phong": "haiphongprovincehero.jpg",
 "kon-tum": "kontumprovincehero.jpg", "lao-cai": "laocaihero.jpg",
 "nghe-an": "ngheanhero.jpg", "ninh-binh": "ninhbinhprovincehero.jpg",
 "ninh-thuan": "ninhthuanhero.jpg", "phu-yen": "phuyenhero.jpg",
 "quang-binh": "quangbinhhero.jpg", "quang-nam": "quangnamhero.jpg",
 "quang-ngai": "quangngaiprovincehero.jpg", "quang-tri": "quangtrihero.jpg",
 "soc-trang": "soctrangprovincehero.jpg", "thanh-hoa": "thanhhoaprovincehero.jpg",
 "tra-vinh": "travinhprovincehero.jpg", "yen-bai": "yenbaihero.jpg",
}
# city-type pages (have city:) -> food-city form
CITY = {"ha-giang": "hagiangcityhero.jpg", "ha-tinh": "hatinhhero.jpg"}
# country pages -> need slug added, food-country form
COUNTRY = {"austria": "austriahero.jpg", "portugal": "portugalhero.jpg"}

def rule(sel, img):
    return f'    {sel} .site-hero {{ background-image: url("/photos/background/{img}") !important; }}\n'

# 1) add slug: to austria & portugal so a class exists to target
for c in COUNTRY:
    p = f"food/{c}/index.md"
    t = open(p, encoding="utf-8").read()
    if f"slug: {c}" not in t:
        anchor = f"country: {c}\n"
        assert t.count(anchor) == 1, f"country anchor !=1 in {p}"
        t = t.replace(anchor, anchor + f"slug: {c}\n", 1)
        open(p, "w", encoding="utf-8", newline="\n").write(t)
        print(f"[fm] added slug: {c} to {p}")

# 2) build CSS blocks
viet_block = "".join(rule(f"body.{s}", img) for s, img in PROV.items())
viet_block += "".join(rule(f"body.food.food-city.{s}", img) for s, img in CITY.items())
aut_block = rule("body.food.food-country.austria", COUNTRY["austria"])
por_block = rule("body.food.food-country.portugal", COUNTRY["portugal"])

html = open(HTML, encoding="utf-8").read()
b0 = (html.count("{"), html.count("}"))

inserts = [
    ("/* ── VIETNAM (additional) ── */", viet_block),
    ("/* ── AUSTRIA ── */", aut_block),
    ("/* ── PORTUGAL ── */", por_block),
]
for anchor, block in inserts:
    assert html.count(anchor) == 1, f"ANCHOR {anchor!r} count != 1"
    html = html.replace(anchor, anchor + "\n" + block.rstrip("\n"), 1)
    print(f"[css] inserted {block.count('!important')} rule(s) after {anchor!r}")

b1 = (html.count("{"), html.count("}"))
assert b1[0] == b1[1], f"BRACE IMBALANCE {b1}"
open(HTML, "w", encoding="utf-8", newline="\n").write(html)
print(f"[css] braces {b0} -> {b1}")
print("DONE")
