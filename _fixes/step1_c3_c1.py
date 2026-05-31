#!/usr/bin/env python3
"""
Step 1: C3 (strip price suffix) and C1 (word-form to placeholder).
Bytes mode, LF output.
"""
import os, re, sys

REPO = r"C:\Users\andre\Documents\andrestgt.github.io"

def read_bytes(path):
    with open(path, 'rb') as f:
        return f.read()

def write_lf(path, data):
    data = data.replace(b'\r\n', b'\n').replace(b'\r', b'\n')
    with open(path, 'wb') as f:
        f.write(data)

def fix_line(path, old_pat, new_text):
    full = os.path.join(REPO, path)
    raw = read_bytes(full)
    # Normalize to LF before regex so $ works correctly
    s = raw.decode('utf-8').replace('\r\n', '\n').replace('\r', '\n')
    hits = re.findall(old_pat, s, re.MULTILINE)
    if len(hits) == 0:
        print("  FAIL no match: " + path)
        return False
    if len(hits) > 1:
        print("  FAIL " + str(len(hits)) + " matches: " + path)
        return False
    s2 = re.sub(old_pat, new_text, s, count=1, flags=re.MULTILINE)
    if s2 == s:
        print("  FAIL no change: " + path)
        return False
    write_lf(full, s2.encode('utf-8'))
    return True

ok = 0
fail = 0

# ------------------------------------------------------------------
# C3: strip "per person", "per main", "per person including tour"
# ------------------------------------------------------------------
print("=== C3 ===")

# 23 bars/pubs + Philippines: strip " per person"
c3_per_person = [
    r"food\vietnam\hue\bars-pubs\why-not-bar-restaurant\index.md",
    r"food\vietnam\hoi-an\bars-pubs\bungalow-beach-bar\index.md",
    r"food\vietnam\quang-binh\phong-nha\bars-pubs\momma-d\index.md",
    r"food\vietnam\quang-binh\dong-hoi\bars-pubs\buffalo-beach-bar\index.md",
    r"food\vietnam\ho-chi-minh-city\bars-pubs\lela-saigon\index.md",
    r"food\vietnam\ho-chi-minh-city\bars-pubs\dams-cocktail-bar\index.md",
    r"food\vietnam\ho-chi-minh-city\bars-pubs\bittersweet-brewing-co-khong-tu\index.md",
    r"food\vietnam\ho-chi-minh-city\bars-pubs\belgo-da-kao-belgian-craft-beer-gastropub\index.md",
    r"food\vietnam\hanoi\bars-pubs\turtle-lake-brewing-company\index.md",
    r"food\vietnam\hanoi\bars-pubs\the-100-garden\index.md",
    r"food\vietnam\hanoi\bars-pubs\polite-co\index.md",
    r"food\vietnam\hanoi\bars-pubs\new-gentry-beer-house\index.md",
    r"food\vietnam\hanoi\bars-pubs\lua-craft-beer\index.md",
    r"food\vietnam\nha-trang\bars-pubs\z-beach-nha-trang\index.md",
    r"food\vietnam\nha-trang\bars-pubs\the-temple-shisha-place\index.md",
    r"food\vietnam\nha-trang\bars-pubs\schulz-beer-brewery-vietnam\index.md",
    r"food\vietnam\nha-trang\bars-pubs\mijack-bar-nha-trang\index.md",
    r"food\vietnam\nha-trang\bars-pubs\brewhaha\index.md",
    r"food\vietnam\da-nang\bars-pubs\section-30-craft-beer-cocktail-pub\index.md",
    r"food\vietnam\binh-dinh\quy-nhon\bars-pubs\surf-bar\index.md",
    r"food\vietnam\da-lat\bars-pubs\woody-classic-bar\index.md",
    r"food\philippines\port-barton-san-vicente\bars-pubs\the-beach-barn\index.md",
    r"food\philippines\manila\bars-pubs\oarhouse-pub\index.md",
]

# Pattern: "Price level:** <value> per person" -> strip " per person"
PAT_PP = r'(\*\*Price level:\*\*[ \t]+\S.*?) per person[ \t]*$'

for f in c3_per_person:
    if fix_line(f, PAT_PP, r'\1'):
        ok += 1
        print("  ok: " + f.split('\\')[-2])
    else:
        fail += 1

# India: "550 Rs per person including tour" -> "550 Rs"
PAT_IND1 = r'(\*\*Price level:\*\*[ \t]+550 Rs) per person including tour[ \t]*$'
if fix_line(r"food\india\south-goa\restaurants\tanshikar-spice-farm\index.md", PAT_IND1, r'\1'):
    ok += 1; print("  ok: tanshikar-spice-farm")
else:
    fail += 1

# India: "Around 250 Rs per main" -> "Around 250 Rs"
PAT_IND2 = r'(\*\*Price level:\*\*[ \t]+Around 250 Rs) per main[ \t]*$'
if fix_line(r"food\india\lucknow\restaurants\coffee-culture\index.md", PAT_IND2, r'\1'):
    ok += 1; print("  ok: coffee-culture")
else:
    fail += 1

# India: "450 Rs per main" -> "450 Rs"
PAT_IND3 = r'(\*\*Price level:\*\*[ \t]+450 Rs) per main[ \t]*$'
if fix_line(r"food\india\kolkata\restaurants\limelight-restaurant\index.md", PAT_IND3, r'\1'):
    ok += 1; print("  ok: limelight-restaurant")
else:
    fail += 1

# ------------------------------------------------------------------
# C1: word-form price -> em-dash placeholder
# No numeric original recoverable from git history.
# ------------------------------------------------------------------
print("=== C1 ===")

EMDASH = u'—'  # —

c1 = [
    (r"food\india\south-goa\restaurants\holiday-inn-cafe\index.md", "inexpensive"),
    (r"food\india\south-goa\restaurants\boom-shankar-resort\index.md", "moderate"),
    (r"food\india\north-goa\restaurants\bees-knees-cafe\index.md", "inexpensive"),
]

for (f, val) in c1:
    pat = r'(\*\*Price level:\*\*[ \t]+)' + re.escape(val) + r'[ \t]*$'
    rep = u'\\1' + EMDASH
    if fix_line(f, pat, rep):
        ok += 1; print("  ok: " + f.split('\\')[-2] + " (" + val + " -> em-dash)")
    else:
        fail += 1

# ------------------------------------------------------------------
print("")
print("ok=" + str(ok) + " fail=" + str(fail))
if fail:
    sys.exit(1)
