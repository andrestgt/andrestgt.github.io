#!/usr/bin/env python3
"""Read-only price-level audit. Classifier locked per user approval."""
import re, glob, os
from collections import defaultdict

CATS = {"restaurants", "street-food", "cafes", "bars-pubs"}
QUANT = {"cafes", "bars-pubs"}          # qualitative tier expected
NUMER = {"restaurants", "street-food"}  # bare numeric expected

TIERS = {"inexpensive", "moderate", "expensive"}
EMPTY = {"", "—", "–", "-", "...", "…", "n/a", "na", "tbd"}

price_re = re.compile(r'^\s*💰\s*\*\*Price level:\*\*\s*(.*?)\s*$', re.M)
per_re   = re.compile(r'\bper\s+(dish|bowl|plate|portion|person|head|pax|cup)\b', re.I)
alc_re   = re.compile(r'with\s+(alcohol|drinks?)', re.I)
num_re   = re.compile(r'[\d₫฿$€₱£₹]|Rp|Rs')

def classify(cat, raw):
    if raw is None:
        return "⚪", "field-missing"
    v = raw.strip()
    if v.lower().strip(" .—–-") == "" or v.lower() in EMPTY:
        return "⚪", "empty-value"
    if cat in NUMER:
        if per_re.search(v):                 return "❌", "per-unit"
        if alc_re.search(v):                 return "🟡", "with-alcohol"
        if num_re.search(v):                 return "✅", "ok"
        return "🟡", "no-figure"
    else:  # cafes / bars-pubs
        low = v.lower().strip()
        if low in TIERS:                     return "✅", "ok"
        if num_re.search(v):                 return "❌", "quantitative"
        return "🟡", "other-tier"

rows = []
for f in glob.glob("food/**/index.md", recursive=True):
    parts = f.replace("\\", "/").split("/")
    # venue page = .../<category>/<slug>/index.md  → category is parts[-3]
    if len(parts) < 4:
        continue
    cat = parts[-3]
    if cat not in CATS:
        continue
    country = parts[1]
    slug = parts[-2]
    with open(f, encoding="utf-8") as fh:
        txt = fh.read()
    m = price_re.search(txt)
    raw = m.group(1) if m else None
    mark, etype = classify(cat, raw)
    rows.append((mark, etype, cat, country, slug, raw if raw is not None else "(no field)", f))

# ---- Summary by category ----
print("=" * 70)
print("TOTAL VENUE PAGES SCANNED:", len(rows))
print("=" * 70)
bycat = defaultdict(lambda: defaultdict(int))
for mark, etype, cat, country, slug, raw, f in rows:
    bycat[cat][mark] += 1
print("\n### COUNTS BY CATEGORY (✅ ❌ 🟡 ⚪)")
print(f"{'category':<14}{'✅':>6}{'❌':>6}{'🟡':>6}{'⚪':>6}{'total':>8}")
for cat in ["restaurants", "street-food", "cafes", "bars-pubs"]:
    d = bycat[cat]
    tot = sum(d.values())
    print(f"{cat:<14}{d['✅']:>6}{d['❌']:>5}{d['🟡']:>6}{d['⚪']:>6}{tot:>8}")

# ---- By error type ----
print("\n### COUNTS BY ERROR TYPE")
byet = defaultdict(int)
for mark, etype, *_ in rows:
    byet[(mark, etype)] += 1
for (mark, etype), n in sorted(byet.items(), key=lambda x: -x[1]):
    print(f"  {mark} {etype:<16} {n}")

# ---- By country (problem rows only) ----
print("\n### PROBLEM ROWS (❌/🟡/⚪) BY COUNTRY")
bycountry = defaultdict(lambda: defaultdict(int))
for mark, etype, cat, country, slug, raw, f in rows:
    if mark != "✅":
        bycountry[country][mark] += 1
print(f"{'country':<16}{'❌':>5}{'🟡':>6}{'⚪':>6}")
for country in sorted(bycountry):
    d = bycountry[country]
    print(f"{country:<16}{d['❌']:>4}{d['🟡']:>6}{d['⚪']:>6}")

# Sanity flag: any country ~100% one bucket
print("\n### SANITY CHECK (per-category-per-country dominant bucket)")
ccc = defaultdict(lambda: defaultdict(int))
for mark, etype, cat, country, slug, raw, f in rows:
    ccc[(country, cat)][mark] += 1
flagged = []
for (country, cat), d in ccc.items():
    tot = sum(d.values())
    if tot >= 4:
        for mark in ("❌", "🟡"):
            if d[mark] / tot >= 0.95:
                flagged.append(f"  ⚠ {country}/{cat}: {d[mark]}/{tot} = {mark}")
print("\n".join(flagged) if flagged else "  none — no country/category is ~100% in an error bucket")

# ---- Full list of ❌ and 🟡 ----
print("\n" + "=" * 70)
print("### FULL LIST: ❌ and 🟡 PAGES (verbatim value + slug)")
print("=" * 70)
probs = [r for r in rows if r[0] in ("❌", "🟡")]
probs.sort(key=lambda r: (r[0], r[2], r[3], r[4]))
for mark, etype, cat, country, slug, raw, f in probs:
    print(f"{mark} [{cat}/{country}] {slug:<30} | {etype:<14} | value: «{raw}»")
print(f"\n(❌+🟡 total: {len(probs)})")

# ---- ⚪ summary (large, list counts not every page) ----
print("\n### ⚪ EMPTY/MISSING SUMMARY BY CATEGORY")
emptycat = defaultdict(int)
for mark, etype, cat, *_ in rows:
    if mark == "⚪":
        emptycat[cat] += 1
for cat, n in sorted(emptycat.items(), key=lambda x: -x[1]):
    print(f"  {cat}: {n}")
