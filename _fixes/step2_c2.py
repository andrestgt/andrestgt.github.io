#!/usr/bin/env python3
"""Step 2 C2: convert numeric prices to word-form on cafe/bar pages."""
import os, re, sys

REPO = r"C:\Users\andre\Documents\andrestgt.github.io"

def read_bytes(path):
    with open(path, 'rb') as f: return f.read()

def write_lf(path, data):
    if isinstance(data, str): data = data.encode('utf-8')
    data = data.replace(b'\r\n', b'\n').replace(b'\r', b'\n')
    with open(path, 'wb') as f: f.write(data)

fixes = [
    ("food/germany/baden-wuerttemberg/stuttgart/bars-pubs/tschechen-soehne/index.md",        "€1–10",       "moderate"),
    ("food/germany/sachsen/leipzig/bars-pubs/peter-k/index.md",                               "€1–10",       "inexpensive"),
    ("food/philippines/manila/bars-pubs/oarhouse-pub/index.md",                               "₱400–600",   "inexpensive"),
    ("food/philippines/port-barton-san-vicente/bars-pubs/the-beach-barn/index.md",            "₱200–400",   "inexpensive"),
    ("food/thailand/around-bangkok/bars-pubs/the-junction-bang-kachao/index.md",              "฿200–400",   "inexpensive"),
    ("food/thailand/around-bangkok/cafes/bread-and-brew-coffee-shop/index.md",                "฿50–100",    "inexpensive"),
    ("food/thailand/around-bangkok/cafes/devaree-boutique/index.md",                          "฿80+",            "moderate"),
    ("food/vietnam/binh-dinh/quy-nhon/bars-pubs/surf-bar/index.md",                           "₫ Under 50k",    "inexpensive"),
    ("food/vietnam/da-lat/bars-pubs/district-1-world-beer-collection/index.md",               "₫200–300k",  "moderate"),
    ("food/vietnam/da-lat/bars-pubs/woody-classic-bar/index.md",                              "₫ Under 50k",    "inexpensive"),
    ("food/vietnam/da-nang/bars-pubs/section-30-craft-beer-cocktail-pub/index.md",            "₫ Under 50k",    "moderate"),
    ("food/vietnam/hanoi/bars-pubs/lua-craft-beer/index.md",                                  "₫ Under 50k",    "inexpensive"),
    ("food/vietnam/hanoi/bars-pubs/new-gentry-beer-house/index.md",                           "₫ Under 50k",    "moderate"),
    ("food/vietnam/hanoi/bars-pubs/polite-co/index.md",                                       "₫ Under 50k",    "inexpensive"),
    ("food/vietnam/hanoi/bars-pubs/the-100-garden/index.md",                                  "₫50–100k",  "inexpensive"),
    ("food/vietnam/hanoi/bars-pubs/turtle-lake-brewing-company/index.md",                     "₫100–200k", "moderate"),
    ("food/vietnam/ho-chi-minh-city/bars-pubs/belgo-da-kao-belgian-craft-beer-gastropub/index.md", "₫100–200k", "moderate"),
    ("food/vietnam/ho-chi-minh-city/bars-pubs/biacraft-xuan-thuy-d2/index.md",               "₫300–400k", "expensive"),
    ("food/vietnam/ho-chi-minh-city/bars-pubs/bittersweet-brewing-co-khong-tu/index.md",     "₫100–200k", "moderate"),
    ("food/vietnam/ho-chi-minh-city/bars-pubs/chenh-venh-rooftop/index.md",                  "₫100–200k", "moderate"),
    ("food/vietnam/ho-chi-minh-city/bars-pubs/dams-cocktail-bar/index.md",                   "₫ Under 50k",    "inexpensive"),
    ("food/vietnam/ho-chi-minh-city/bars-pubs/lela-saigon/index.md",                         "₫100–200k", "expensive"),
    ("food/vietnam/hoi-an/bars-pubs/bungalow-beach-bar/index.md",                            "₫ Under 50k",    "inexpensive"),
    ("food/vietnam/hue/bars-pubs/why-not-bar-restaurant/index.md",                           "₫ Under 50k",    "inexpensive"),
    ("food/vietnam/nha-trang/bars-pubs/brewhaha/index.md",                                   "₫ Under 50k",    "inexpensive"),
    ("food/vietnam/nha-trang/bars-pubs/craft-beer-ub-eatrang/index.md",                      "₫100–200k", "moderate"),
    ("food/vietnam/nha-trang/bars-pubs/hurra-beer/index.md",                                 "₫100–200k", "inexpensive"),
    ("food/vietnam/nha-trang/bars-pubs/jelly-brew-pub/index.md",                             "₫200–300k", "inexpensive"),
    ("food/vietnam/nha-trang/bars-pubs/kilo-distillery-bar/index.md",                        "₫200–300k", "inexpensive"),
    ("food/vietnam/nha-trang/bars-pubs/mijack-bar-nha-trang/index.md",                       "₫ Under 50k",    "expensive"),
    ("food/vietnam/nha-trang/bars-pubs/schulz-beer-brewery-vietnam/index.md",                "₫ Under 50k",    "inexpensive"),
    ("food/vietnam/nha-trang/bars-pubs/sunshine-bar-rooftop/index.md",                       "₫300–400k", "moderate"),
    ("food/vietnam/nha-trang/bars-pubs/the-temple-shisha-place/index.md",                    "₫ Under 50k",    "moderate"),
    ("food/vietnam/nha-trang/bars-pubs/z-beach-nha-trang/index.md",                          "₫ Under 50k",    "moderate"),
    ("food/vietnam/quang-binh/dong-hoi/bars-pubs/buffalo-beach-bar/index.md",                "₫ Under 50k",    "inexpensive"),
    ("food/vietnam/quang-binh/phong-nha/bars-pubs/momma-d/index.md",                         "₫ Under 50k",    "inexpensive"),
]

ok = fail = 0
for (f, old_val, new_val) in fixes:
    path = os.path.join(REPO, f.replace('/', os.sep))
    raw = read_bytes(path)
    s = raw.decode('utf-8').replace('\r\n', '\n').replace('\r', '\n')
    lines_before = s.count('\n')

    pat = r'(\U0001F4B0 \*\*Price level:\*\* )' + re.escape(old_val) + r'[ \t]*$'
    hits = re.findall(pat, s, re.MULTILINE)
    if len(hits) == 0:
        print("  FAIL no match: " + f.split('/')[-2])
        fail += 1; continue
    if len(hits) > 1:
        print("  FAIL " + str(len(hits)) + " matches: " + f.split('/')[-2])
        fail += 1; continue

    s2 = re.sub(pat, r'\g<1>' + new_val, s, count=1, flags=re.MULTILINE)
    if s2.count('\n') != lines_before:
        print("  FAIL line count changed: " + f.split('/')[-2])
        fail += 1; continue

    write_lf(path, s2)
    print("  ok [" + new_val + "]: " + f.split('/')[-2])
    ok += 1

print("\nok=" + str(ok) + " fail=" + str(fail))
if fail: sys.exit(1)
