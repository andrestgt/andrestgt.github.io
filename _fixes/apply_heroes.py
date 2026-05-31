#!/usr/bin/env python3
"""Step 3: apply hero plan. Reads _fixes/hero_plan.json. Loud asserts; additive CSS."""
import json, os, re, shutil

DL = r"C:\Users\andre\Downloads"
BG = "photos/background"
HTML = "_layouts/default.html"
P = json.load(open("_fixes/hero_plan.json", encoding="utf-8"))

# 1) COPIES
copied = 0
for src, dest in P["copies"]:
    s = os.path.join(DL, src)
    assert os.path.exists(s), f"SOURCE MISSING: {s}"
    shutil.copy2(s, os.path.join(BG, dest))
    copied += 1
print(f"[copies] {copied} images -> {BG}/")

# 2) CREATE LANDING
cl = P["create_landing"]
if cl:
    if os.path.exists(cl["path"]):
        print(f"[landing] EXISTS, skip: {cl['path']}")
    else:
        body = (f"---\nlayout: default\nsection: food\ncity: {cl['city']}\n"
                f"slug: {cl['city']}\ntitle: {cl['title']}\n"
                f"subtitle: Food and drink in {cl['title']}\n---\n\n"
                f"# {cl['title']}\n\nReviews grouped by category.\n\n"
                f"- [{cl['linktext']}]({cl['link']})\n")
        open(cl["path"], "w", encoding="utf-8", newline="\n").write(body)
        print(f"[landing] created {cl['path']}")

# 3) FRONT-MATTER ADD
for path, fpath in P["fm_add"]:
    t = open(path, encoding="utf-8").read()
    m = re.match(r"^(---\n.*?\n)(---\s*\n?)", t, re.S)
    assert m, f"NO FRONT MATTER: {path}"
    assert "hero:" not in m.group(1), f"ALREADY HAS hero: {path}"
    new = m.group(1) + f"hero: {fpath}\nhero_overlay: false\n" + m.group(2) + t[m.end():]
    open(path, "w", encoding="utf-8", newline="\n").write(new)
print(f"[fm_add] {len(P['fm_add'])} province landings got hero front matter")

# 4) FRONT-MATTER REPLACE (filename swap, covers hero: and background:)
for path, old, new in P["fm_replace"]:
    t = open(path, encoding="utf-8").read()
    n = t.count(old)
    assert n >= 1, f"OLD FILENAME {old} NOT FOUND in {path}"
    open(path, "w", encoding="utf-8", newline="\n").write(t.replace(old, new))
    print(f"[fm_replace] {path}: {old} -> {new}  ({n}x)")

# 5) CSS (additive)
html = open(HTML, encoding="utf-8").read()
braces_before = (html.count("{"), html.count("}"))

def rules_block(rules, indent="    "):
    return "".join(f'{indent}{sel} {{ background-image: url("{f}") !important; }}\n'
                   for sel, f in rules)

EXISTING = {"germany": "/* ── GERMANY ── */", "hungary": "/* ── HUNGARY ── */",
            "portugal": "/* ── PORTUGAL ── */", "slovakia": "/* ── SLOVAKIA ── */"}
for country, anchor in EXISTING.items():
    if country not in P["css"]:
        continue
    assert html.count(anchor) == 1, f"ANCHOR {anchor} count != 1"
    block = rules_block(P["css"][country])
    html = html.replace(anchor, anchor + "\n" + block.rstrip("\n"), 1)
    print(f"[css] appended {len(P['css'][country])} rule(s) to {country} section")

# new sections before Floating nav
NEW_ORDER = [("austria", "AUSTRIA"), ("thailand", "THAILAND (additional)"),
             ("vietnam", "VIETNAM (additional)")]
newblock = ""
for country, label in NEW_ORDER:
    if country in P["css"]:
        newblock += f"    /* ── {label} ── */\n" + rules_block(P["css"][country])
nav = "/* Floating nav */"
assert html.count(nav) == 1, "Floating nav anchor count != 1"
html = html.replace(nav, newblock + "    " + nav, 1)
print(f"[css] inserted new sections: {[l for c,l in NEW_ORDER if c in P['css']]}")

braces_after = (html.count("{"), html.count("}"))
added = braces_after[0] - braces_before[0]
assert braces_after[0] == braces_after[1], f"BRACE IMBALANCE: {braces_after}"
assert added == braces_after[1] - braces_before[1], "open/close add mismatch"
open(HTML, "w", encoding="utf-8", newline="\n").write(html)
print(f"[css] braces balanced ({braces_before} -> {braces_after}, +{added} pairs)")
print("DONE")
