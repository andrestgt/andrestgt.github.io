#!/usr/bin/env python3
"""
Step 1 fixes: C3 (strip price suffix), C4 (normalize raw-currency), C1 (word-form → placeholder)
All file I/O in bytes mode with LF line endings.
"""

import os
import re
import sys

REPO = r"C:\Users\andre\Documents\andrestgt.github.io"

def read_bytes(path):
    with open(path, 'rb') as f:
        return f.read()

def write_lf(path, data):
    # Normalize to LF
    data = data.replace(b'\r\n', b'\n').replace(b'\r', b'\n')
    with open(path, 'wb') as f:
        f.write(data)

def apply_price_fix(path, old_pattern, new_text, expected_delta=0):
    """Replace exactly one price line. Assert line count changes by expected_delta."""
    full = os.path.join(REPO, path)
    data = read_bytes(full)
    lines_before = data.count(b'\n')

    data_str = data.decode('utf-8')

    # Use MULTILINE so $ matches end of each line (not just end of string)
    flags = re.MULTILINE
    matches = len(re.findall(old_pattern, data_str, flags=flags))
    if matches == 0:
        print(f"  ERROR: pattern not found in {path}")
        return False
    if matches > 1:
        print(f"  ERROR: pattern matched {matches} times in {path} (expected 1)")
        return False

    new_data_str = re.sub(old_pattern, new_text, data_str, count=1, flags=flags)
    new_data = new_data_str.encode('utf-8')
    lines_after = new_data.count(b'\n')

    if lines_after - lines_before != expected_delta:
        print(f"  ERROR: line count delta = {lines_after - lines_before}, expected {expected_delta} in {path}")
        return False

    write_lf(full, new_data)
    return True

errors = []
changes = []

# =============================================================================
# C3: Strip "per person/per main/per coffee/per person including tour" suffix
# =============================================================================
print("=== C3: Strip price suffix (26 pages) ===")

# Vietnam bars-pubs: "₫ X per person" → "₫ X" or "₫X–Yk per person" → "₫X–Yk"
# Philippines bars-pubs: "₱X–Y per person" → "₱X–Y"
c3_files = [
    "food/vietnam/hue/bars-pubs/why-not-bar-restaurant/index.md",
    "food/vietnam/hoi-an/bars-pubs/bungalow-beach-bar/index.md",
    "food/vietnam/quang-binh/phong-nha/bars-pubs/momma-d/index.md",
    "food/vietnam/quang-binh/dong-hoi/bars-pubs/buffalo-beach-bar/index.md",
    "food/vietnam/ho-chi-minh-city/bars-pubs/lela-saigon/index.md",
    "food/vietnam/ho-chi-minh-city/bars-pubs/dams-cocktail-bar/index.md",
    "food/vietnam/ho-chi-minh-city/bars-pubs/bittersweet-brewing-co-khong-tu/index.md",
    "food/vietnam/ho-chi-minh-city/bars-pubs/belgo-da-kao-belgian-craft-beer-gastropub/index.md",
    "food/vietnam/hanoi/bars-pubs/turtle-lake-brewing-company/index.md",
    "food/vietnam/hanoi/bars-pubs/the-100-garden/index.md",
    "food/vietnam/hanoi/bars-pubs/polite-co/index.md",
    "food/vietnam/hanoi/bars-pubs/new-gentry-beer-house/index.md",
    "food/vietnam/hanoi/bars-pubs/lua-craft-beer/index.md",
    "food/vietnam/nha-trang/bars-pubs/z-beach-nha-trang/index.md",
    "food/vietnam/nha-trang/bars-pubs/the-temple-shisha-place/index.md",
    "food/vietnam/nha-trang/bars-pubs/schulz-beer-brewery-vietnam/index.md",
    "food/vietnam/nha-trang/bars-pubs/mijack-bar-nha-trang/index.md",
    "food/vietnam/nha-trang/bars-pubs/brewhaha/index.md",
    "food/vietnam/da-nang/bars-pubs/section-30-craft-beer-cocktail-pub/index.md",
    "food/vietnam/binh-dinh/quy-nhon/bars-pubs/surf-bar/index.md",
    "food/vietnam/da-lat/bars-pubs/woody-classic-bar/index.md",
    "food/philippines/port-barton-san-vicente/bars-pubs/the-beach-barn/index.md",
    "food/philippines/manila/bars-pubs/oarhouse-pub/index.md",
]

for f in c3_files:
    path = f.replace('/', os.sep)
    ok = apply_price_fix(
        path,
        r'(\*\*Price level:\*\*\s+.+?) per person\s*$',
        r'\1',
        expected_delta=0
    )
    if ok:
        changes.append(f"C3: {f}")
        print(f"  OK: {f}")
    else:
        errors.append(f"C3 FAILED: {f}")

# India restaurant: "550 Rs per person including tour" → "550 Rs"
ok = apply_price_fix(
    r"food\india\south-goa\restaurants\tanshikar-spice-farm\index.md",
    r'(\*\*Price level:\*\*\s+550 Rs) per person including tour\s*$',
    r'\1',
    expected_delta=0
)
if ok:
    changes.append("C3: india/south-goa/restaurants/tanshikar-spice-farm")
    print("  OK: tanshikar-spice-farm")
else:
    errors.append("C3 FAILED: tanshikar-spice-farm")

# India restaurant: "Around 250 Rs per main" → "Around 250 Rs"
ok = apply_price_fix(
    r"food\india\lucknow\restaurants\coffee-culture\index.md",
    r'(\*\*Price level:\*\*\s+Around 250 Rs) per main\s*$',
    r'\1',
    expected_delta=0
)
if ok:
    changes.append("C3: india/lucknow/restaurants/coffee-culture")
    print("  OK: coffee-culture")
else:
    errors.append("C3 FAILED: coffee-culture")

# India restaurant: "450 Rs per main" → "450 Rs"
ok = apply_price_fix(
    r"food\india\kolkata\restaurants\limelight-restaurant\index.md",
    r'(\*\*Price level:\*\*\s+450 Rs) per main\s*$',
    r'\1',
    expected_delta=0
)
if ok:
    changes.append("C3: india/kolkata/restaurants/limelight-restaurant")
    print("  OK: limelight-restaurant")
else:
    errors.append("C3 FAILED: limelight-restaurant")

# =============================================================================
# C4: Normalize raw-currency (12 RM en-dash → hyphen + 1 VND → ₫)
# =============================================================================
print("\n=== C4: Normalize raw-currency (13 pages) ===")

# RM en-dash pages: change – to - in price level line
c4_rm_files = [
    ("food/malaysia/kuala-lumpur/restaurants/canton-i-the-gardens/index.md", "RM 60–90", "RM 60-90"),
    ("food/malaysia/kuala-lumpur/restaurants/dolly-dim-sum-nu-sentral/index.md", "RM 40–70", "RM 40-70"),
    ("food/malaysia/kuala-lumpur/restaurants/fuel-shack-low-yat/index.md", "RM 40–70", "RM 40-70"),
    ("food/malaysia/kuala-lumpur/restaurants/grandmamas-pavilion/index.md", "RM 60–90", "RM 60-90"),
    ("food/malaysia/kuala-lumpur/restaurants/ichiban-boshi-publika/index.md", "RM 60–90", "RM 60-90"),
    ("food/malaysia/kuala-lumpur/restaurants/mtr-kl-sentral/index.md", "RM 20–40", "RM 20-40"),
    ("food/malaysia/kuala-lumpur/street-food/abc-one-bistro/index.md", "RM 1–20", "RM 1-20"),
    ("food/malaysia/langkawi/restaurants/fat-cupid/index.md", "RM 50–80", "RM 50-80"),
    ("food/malaysia/langkawi/restaurants/scarborough-fish-and-chips/index.md", "RM 40–70", "RM 40-70"),
    ("food/malaysia/langkawi/restaurants/yasmin-syrian-restaurant/index.md", "RM 80–120", "RM 80-120"),
    ("food/malaysia/penang/restaurants/max-cafe/index.md", "RM 25–40", "RM 25-40"),
    ("food/malaysia/penang/restaurants/yong-pin-restaurant/index.md", "RM 1–20", "RM 1-20"),
]

for (f, old_val, new_val) in c4_rm_files:
    path = f.replace('/', os.sep)
    old_pat = re.escape(old_val)
    ok = apply_price_fix(
        path,
        r'(\*\*Price level:\*\*\s+)' + old_pat,
        r'\g<1>' + new_val,
        expected_delta=0
    )
    if ok:
        changes.append(f"C4: {f} ({old_val} → {new_val})")
        print(f"  OK: {f}")
    else:
        errors.append(f"C4 FAILED: {f}")

# VND suffix page: "250–350k VND" → "₫250-350k"
ok = apply_price_fix(
    r"food\vietnam\sa-pa\restaurants\paradise-restaurant.md",
    r'(\*\*Price level:\*\*\s+)250–350k VND',
    r'\g<1>₫250-350k',
    expected_delta=0
)
if ok:
    changes.append("C4: vietnam/sa-pa/restaurants/paradise-restaurant.md (VND → ₫)")
    print("  OK: paradise-restaurant.md VND fix")
else:
    errors.append("C4 FAILED: paradise-restaurant.md VND")

# =============================================================================
# C1: Word-form price → "—" (no numeric original recoverable)
# =============================================================================
print("\n=== C1: Word-form price -> placeholder (3 pages) ===")

c1_files = [
    ("food/india/south-goa/restaurants/holiday-inn-cafe/index.md", "inexpensive"),
    ("food/india/south-goa/restaurants/boom-shankar-resort/index.md", "moderate"),
    ("food/india/north-goa/restaurants/bees-knees-cafe/index.md", "inexpensive"),
]

for (f, old_val) in c1_files:
    path = f.replace('/', os.sep)
    ok = apply_price_fix(
        path,
        r'(\*\*Price level:\*\*\s+)' + re.escape(old_val) + r'\s*$',
        u'\g<1>—',
        expected_delta=0
    )
    if ok:
        changes.append(f"C1: {f} ({old_val} -> em-dash)")
        print(f"  OK: {f}")
    else:
        errors.append(f"C1 FAILED: {f}")

# =============================================================================
# Summary
# =============================================================================
print(f"\n=== RESULTS ===")
print(f"Changes applied: {len(changes)}")
print(f"Errors: {len(errors)}")
for e in errors:
    print(f"  {e}")

if errors:
    sys.exit(1)
