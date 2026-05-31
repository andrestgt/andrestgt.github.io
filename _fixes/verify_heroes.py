#!/usr/bin/env python3
"""Build-equivalent hero verification: replicate body-class + CSS cascade. Read-only."""
import os, re, glob, json

CATS = {"restaurants", "street-food", "cafes", "bars-pubs"}
P = json.load(open("_fixes/hero_plan.json", encoding="utf-8"))
our68 = {dest for _, dest in P["copies"]}

def fm(path):
    t = open(path, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---", t, re.S)
    d = {}
    if m:
        for line in m.group(1).splitlines():
            mm = re.match(r"^([a-z_]+):\s*(.*)$", line)
            if mm: d[mm.group(1)] = mm.group(2).strip()
    return d

# body class per layout lines 845-855
def body_classes(d):
    c = []
    if d.get("section"): c.append(d["section"])
    if d.get("index") == "true": c.append("index")
    if d.get("country"): c.append("food-country")
    if d.get("city"):
        c.append("food-city"); c.append(d["city"])
    if d.get("category"):
        c.append("food-category"); c.append(d["category"])
    if d.get("review"): c.append("food-review")
    if d.get("slug"): c += d["slug"].split()
    return set(c)

# parse CSS .site-hero rules: classes, url, important
html = open("_layouts/default.html", encoding="utf-8").read()
rules = []  # (set(classes), url, important, order)
for i, m in enumerate(re.finditer(r'body\.([a-z0-9.\-]+)\s+\.site-hero\s*\{([^}]*)\}', html)):
    cls = set(m.group(1).split("."))
    body = m.group(2)
    um = re.search(r'url\(["\']?([^"\')]+)["\']?\)', body)
    if not um: continue
    rules.append((cls, um.group(1), "!important" in body, i))

def render_hero(d):
    """Return (url, source) the page actually shows, per cascade.
    Tiebreak: specificity (class count) then source order — like real CSS."""
    bc = body_classes(d)
    matches = [(u, imp, o, len(cls)) for cls, u, imp, o in rules if cls <= bc]
    inline = d.get("hero")
    imp_matches = [m for m in matches if m[1]]
    if imp_matches:  # !important stylesheet beats inline; most specific, then last
        u = sorted(imp_matches, key=lambda x: (x[3], x[2]))[-1][0]
        return u, "CSS!important"
    if inline:
        return inline, "front-matter"
    if matches:
        return sorted(matches, key=lambda x: (x[3], x[2]))[-1][0], "CSS"
    return None, "NONE"

# walk all landings, compute rendered hero
url_to_landings = {}
for f in glob.glob("food/**/index.md", recursive=True):
    f = f.replace("\\", "/"); parts = f.split("/")
    if len(parts) >= 4 and parts[-3] in CATS: continue  # venue
    d = fm(f)
    url, src = render_hero(d)
    if url:
        fn = url.split("/")[-1]
        url_to_landings.setdefault(fn, []).append((f, src))

# verify each of our 68 images renders on a landing + file exists
print(f"Verifying {len(our68)} hero images render on their landing...\n")
ok = miss_render = miss_file = 0
problems = []
for img in sorted(our68):
    landings = url_to_landings.get(img, [])
    file_ok = os.path.exists("photos/background/" + img)
    if not landings:
        miss_render += 1; problems.append(f"NOT RENDERED by any landing: {img}")
    elif not file_ok:
        miss_file += 1; problems.append(f"file missing on disk: {img}")
    else:
        ok += 1
print(f"✅ render+file OK: {ok}")
print(f"❌ not rendered:   {miss_render}")
print(f"❌ file missing:   {miss_file}")
if problems:
    print("\n--- PROBLEMS ---")
    for p in problems: print(" ", p)

# spot samples: one CSS, one front-matter, the category pair, a province/city same-name pair
print("\n=== SPOT SAMPLES (landing -> rendered hero [source]) ===")
for img in ["salzburghero.jpg", "quangbinhhero.jpg", "cafescanthohero.jpg",
            "restocanthohero.jpg", "kontumhero.jpg", "kontumprovincehero.jpg",
            "portugalhero.jpg", "hagiangcityhero.jpg", "mucangchaihero.jpg"]:
    for f, src in url_to_landings.get(img, [("(none)", "NONE")]):
        print(f"  {img:<26} <- {f}  [{src}]")

# collision check: any landing rendering an UNEXPECTED hero among province/city pairs
print("\n=== Province pages must NOT render a city's !important hero ===")
for prov in ["kon-tum", "ninh-binh", "soc-trang", "thanh-hoa", "tra-vinh", "quang-ngai"]:
    f = f"food/vietnam/{prov}/index.md"
    if os.path.exists(f):
        u, s = render_hero(fm(f))
        print(f"  {prov:<12} -> {u.split('/')[-1] if u else None} [{s}]")
