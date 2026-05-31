#!/usr/bin/env python3
"""Step 1: match Downloads hero images to landing pages. Read-only."""
import os, re, glob, unicodedata, difflib

DL = r"C:\Users\andre\Downloads"
CATS = {"restaurants", "street-food", "cafes", "bars-pubs"}

def norm(s):
    s = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]", "", s.lower())

def fm(path):
    t = open(path, encoding="utf-8").read()
    m = re.match(r"^---\n(.*?)\n---", t, re.S)
    d = {}
    if m:
        for line in m.group(1).splitlines():
            mm = re.match(r"^([a-z_]+):\s*(.*)$", line)
            if mm:
                d[mm.group(1)] = mm.group(2).strip()
    return d

# --- build landing inventory ---
landings = []
for f in glob.glob("food/**/index.md", recursive=True):
    f = f.replace("\\", "/")
    parts = f.split("/")
    if len(parts) >= 4 and parts[-3] in CATS:
        continue  # venue page
    d = fm(f)
    country = parts[1] if len(parts) > 2 else None
    if len(parts) == 3:
        level = "country"; dirslug = parts[1]
    elif parts[-2] in CATS:
        level = "category"; dirslug = parts[-3] + "-" + parts[-2]
    elif "city" in d:
        level = "city"; dirslug = parts[-2]
    else:
        level = "region"; dirslug = parts[-2]
    landings.append({
        "path": f, "level": level, "dirslug": parts[-2],
        "city": d.get("city"), "country": d.get("country"),
        "region": d.get("region"), "slug": d.get("slug"),
        "index": d.get("index"), "title": d.get("title", ""),
        "ndir": norm(parts[-2]), "ntitle": norm(d.get("title", "")),
        "catkind": parts[-2] if parts[-2] in CATS else None,
        "pcity": norm(parts[-3]) if parts[-2] in CATS else None,
        "fmhero": d.get("hero"),
    })

# existing background files + existing CSS body selectors
BG = set(os.listdir("photos/background"))
html = open("_layouts/default.html", encoding="utf-8").read()
CSS_SEL = set(re.findall(r"body\.([a-z0-9.\-]+)\s*\.site-hero", html))

def mechanism(L):
    if L["city"]:
        return "CSS", f'body.food.food-city.{L["city"]} .site-hero'
    if L["country"] and L["slug"] and L["level"] == "country":
        return "CSS", f'body.food.food-country.{L["slug"]} .site-hero'
    if L["slug"]:
        return "front-matter", f'(body .{L["slug"]})'
    return "front-matter?", "(no slug — needs check)"

# --- match each image ---
imgs = sorted(os.listdir(DL))
imgs = [i for i in imgs if i.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))]

# pre-scan: which base keys have an explicit province/city sibling
def imgkey(img):
    b = re.sub(r"\.(jpg|jpeg|png|webp)$", "", img, flags=re.I).lower()
    b = re.sub(r"(hero|head)$", "", b)
    for p in ("cafes", "restaurants", "resto", "streetfood"):
        if b.startswith(p): return None
    hint = None
    if b.endswith("province"): hint, b = "region", b[:-8]
    elif b.endswith("city"): hint, b = "city", b[:-4]
    return norm(b), hint
suffixed = {}
for img in imgs:
    k = imgkey(img)
    if k and k[1]:
        suffixed.setdefault(k[0], set()).add(k[1])

print(f"{'IMAGE':<28}{'MATCH':<6}{'LANDING PATH':<58}{'MECH'}")
print("-" * 120)
rows = []
for img in imgs:
    base = re.sub(r"\.(jpg|jpeg|png|webp)$", "", img, flags=re.I)
    b = base.lower()
    b = re.sub(r"(hero|head)$", "", b)
    cat_pref = None
    if b.startswith("cafes"): cat_pref, b = "cafes", b[5:]
    elif b.startswith("restaurants"): cat_pref, b = "restaurants", b[11:]
    elif b.startswith("resto"): cat_pref, b = "restaurants", b[5:]
    elif b.startswith("streetfood"): cat_pref, b = "street-food", b[10:]
    level_hint = None
    if b.endswith("province"): level_hint, b = "region", b[:-8]
    elif b.endswith("city"): level_hint, b = "city", b[:-4]
    key = norm(b)
    # no-suffix image but a sibling carries 'province' -> this one is the city
    if not level_hint and not cat_pref and "region" in suffixed.get(key, set()):
        level_hint = "city"

    cands = landings
    if cat_pref:
        cands = [L for L in landings if L["catkind"] == cat_pref]
        best = [L for L in cands if L["pcity"] == key]
        match, conf = (best[0], "OK-cat") if best else (None, "NONE")
    else:
        # exact dir-slug
        exact = [L for L in cands if L["ndir"] == key]
        if level_hint:
            pref = [L for L in exact if L["level"] == level_hint]
            exact = pref or exact
        if exact:
            match, conf = exact[0], "EXACT"
        else:
            tmatch = [L for L in cands if L["ntitle"] == key]
            if level_hint:
                pref = [L for L in tmatch if L["level"] == level_hint]
                tmatch = pref or tmatch
            if tmatch:
                match, conf = tmatch[0], "TITLE"
            else:
                # fuzzy on dirslug
                scored = sorted(cands, key=lambda L: difflib.SequenceMatcher(None, L["ndir"], key).ratio(), reverse=True)
                top = scored[0]
                r = difflib.SequenceMatcher(None, top["ndir"], key).ratio()
                if r >= 0.8:
                    match, conf = top, f"FUZZY{r:.2f}"
                else:
                    match, conf = None, "NONE"
    flags = []
    if match:
        mech, sel = mechanism(match)
        if img in BG: flags.append("TGT-EXISTS")
        if match["fmhero"]: flags.append(f"FM-HERO={match['fmhero'].split('/')[-1]}")
        cssslug = sel.split(".site-hero")[0].replace("body.", "") if mech == "CSS" else (match["slug"] or "")
        if cssslug and cssslug in CSS_SEL: flags.append("CSS-EXISTS")
        if match["slug"] and match["slug"] in CSS_SEL: flags.append(f"CSS-RULE({match['slug']})")
        rows.append((img, conf, match["path"], mech, ";".join(flags), match))
    else:
        rows.append((img, conf, "", "", "NO-LANDING", None))

CITY_FM = {"ha-giang", "ha-tinh"}  # city pages that already use front-matter hero

def plan_for(img, match):
    """Return (action, detail) for Step 2 pre-flight."""
    if match is None:
        return ("CREATE-LANDING+CSS", "mu-cang-chai")
    L = match
    country = L["path"].split("/")[1]
    f = f"/photos/background/{img}"
    if L["catkind"]:
        sel = f'body.food.food-city.{L["city"]}.food-category.{L["catkind"]} .site-hero'
        return ("CSS", f'{sel} {{ background-image: url("{f}") !important; }}')
    if L["level"] == "city":
        sel = f'body.food.food-city.{L["city"]} .site-hero'
        if L["city"] in CITY_FM:
            return ("FM-REPLACE", f'hero: {f}   (replaces {L["fmhero"]})')
        return ("CSS", f'{sel} {{ background-image: url("{f}") !important; }}')
    # region/country -> front matter
    if L["fmhero"]:
        return ("FM-REPLACE", f'hero: {f}   (replaces {L["fmhero"]})')
    return ("FM-ADD", f'hero: {f}  +  hero_overlay: false')

print("\n############ STEP 2 PRE-FLIGHT PLAN ############")
from collections import defaultdict
css_by_country = defaultdict(list)
fm_changes = []
for img, conf, path, mech, fl, m in rows:
    action, detail = plan_for(img, m)
    src_ok = "OK" if os.path.exists(os.path.join(DL, img)) else "MISSING"
    collide = "OVERWRITE" if img in BG else "new"
    if action == "CSS":
        country = m["path"].split("/")[1]
        css_by_country[country].append((img, detail))
    elif action in ("FM-ADD", "FM-REPLACE"):
        fm_changes.append((img, path, action, detail, collide))
    else:  # CREATE-LANDING+CSS (mu-cang-chai)
        fm_changes.append((img, "food/vietnam/yen-bai/mu-cang-chai/index.md", action, detail, collide))

print("\n----- A) FRONT-MATTER changes (province / country / existing-hero) -----")
print(f"{'IMAGE':<28}{'COPY':<10}{'ACTION':<12}{'LANDING'}")
for img, path, action, detail, collide in fm_changes:
    print(f"{img:<28}{collide:<10}{action:<12}{path}")
    print(f"      -> {detail}")

print("\n----- B) CSS rules to ADD, grouped by country section -----")
for country in sorted(css_by_country):
    print(f"\n  /* ── {country.upper()} (new) ── */")
    for img, line in css_by_country[country]:
        col = "OVERWRITE" if img in BG else "new"
        print(f"    [{col:<9}] {line}")

print(f"\n----- C) FILE COPIES: {len(rows)} images Downloads -> photos/background/ -----")
overw = [img for img, *_ in rows if img in BG]
print(f"  overwrites ({len(overw)}): {', '.join(overw) if overw else 'none'}")
print(f"  uppercase-ext to flag: {[img for img,*_ in rows if img.endswith('.JPG')]}")

print("\n=== NEEDS ATTENTION ===")
for img, conf, path, mech, fl, m in rows:
    if conf not in ("EXACT", "OK-cat") or any(x in fl for x in ("EXISTS", "FM-HERO", "CSS-RULE", "NO-LANDING")):
        print(f"  {conf:<10} {img:<28} {fl}  -> {path or '(none)'}")

# ---------------- machine-readable plan ----------------
import json
def dest_of(img):
    base, ext = os.path.splitext(img)
    return base + ext.lower()  # lowercases .JPG -> .jpg

JPLAN = {"copies": [], "css": defaultdict(list), "fm_add": [], "fm_replace": [],
         "create_landing": None}
for img, conf, path, mech, fl, m in rows:
    dest = dest_of(img)
    JPLAN["copies"].append([img, dest])
    fpath = f"/photos/background/{dest}"
    if m is None:  # mu-cang-chai
        JPLAN["create_landing"] = {
            "path": "food/vietnam/yen-bai/mu-cang-chai/index.md",
            "city": "mu-cang-chai", "title": "Mù Cang Chải",
            "link": "/food/vietnam/yen-bai/mu-cang-chai/restaurants/",
            "linktext": "Restaurants"}
        JPLAN["css"]["vietnam"].append(
            [f"body.food.food-city.mu-cang-chai .site-hero", fpath])
        continue
    if m["catkind"]:
        sel = f'body.food.food-city.{m["city"]}.food-category.{m["catkind"]} .site-hero'
        JPLAN["css"][m["path"].split("/")[1]].append([sel, fpath])
    elif m["level"] == "city" and m["city"] not in CITY_FM:
        sel = f'body.food.food-city.{m["city"]} .site-hero'
        JPLAN["css"][m["path"].split("/")[1]].append([sel, fpath])
    else:  # province/country/existing-fm
        old = (m["fmhero"] or "").split("/")[-1]
        if old and old != dest:
            JPLAN["fm_replace"].append([m["path"], old, dest])
        elif not old:
            JPLAN["fm_add"].append([m["path"], fpath])
        # old == dest (ha-tinh): copy only, no edit
JPLAN["css"] = dict(JPLAN["css"])
json.dump(JPLAN, open("_fixes/hero_plan.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("\nPlan written to _fixes/hero_plan.json")
print("  copies:", len(JPLAN["copies"]), "| css:", sum(len(v) for v in JPLAN["css"].values()),
      "| fm_add:", len(JPLAN["fm_add"]), "| fm_replace:", len(JPLAN["fm_replace"]),
      "| create_landing:", bool(JPLAN["create_landing"]))
