#!/usr/bin/env python3
"""
D3: Remove double-dash separator debris (extra trailing --- before footer or end of file).
B1 items 7-9: Remove all 3 figure blocks from far-east-rock-cafe (photoless page).
"""
import os, re, sys

REPO = r"C:\Users\andre\Documents\andrestgt.github.io"

def read_bytes(path):
    with open(path, 'rb') as f:
        return f.read()

def write_lf(path, data):
    if isinstance(data, str):
        data = data.encode('utf-8')
    data = data.replace(b'\r\n', b'\n').replace(b'\r', b'\n')
    with open(path, 'wb') as f:
        f.write(data)

ok = 0
fail = 0

# =============================================================================
# D3: double-dash separator debris
# Pattern: \n---\n\n---\n  →  \n---\n  (removes one extra --- and one blank line)
# Each file must drop by exactly 2 lines.
# =============================================================================
print("=== D3: double-dash separator debris (13 files) ===")

d3_files = [
    "food/cambodia/phnom-penh/street-food/index.md",
    "food/india/kolkata/street-food/index.md",
    "food/india/lucknow/street-food/index.md",
    "food/india/mysore/street-food/index.md",
    "food/india/north-goa/restaurants/index.md",
    "food/india/south-goa/street-food/index.md",
    "food/india/varanasi/street-food/index.md",
    "food/laos/luang-prabang/street-food/index.md",
    "food/malaysia/ipoh/street-food/index.md",
    "food/malaysia/kuala-lumpur/street-food/index.md",
    "food/malaysia/kuching/street-food/index.md",
    "food/taiwan/tainan/street-food/index.md",
    "food/taiwan/taipei/street-food/index.md",
]

for f in d3_files:
    path = os.path.join(REPO, f.replace('/', os.sep))
    raw = read_bytes(path)
    s = raw.decode('utf-8').replace('\r\n', '\n').replace('\r', '\n')
    lines_before = s.count('\n')

    # The debris is an extra --- preceded and followed by blank lines.
    # Pattern: "---\n\n---\n" anywhere in the file (the second --- is debris).
    # Replace with "---\n" removing the blank line + extra ---.
    count = s.count('\n---\n\n---\n')
    if count == 0:
        print("  FAIL no double-dash found: " + f)
        fail += 1
        continue
    if count > 1:
        print("  FAIL " + str(count) + " double-dash matches: " + f)
        fail += 1
        continue

    s2 = s.replace('\n---\n\n---\n', '\n---\n', 1)
    lines_after = s2.count('\n')
    delta = lines_after - lines_before
    if delta != -2:
        print("  FAIL delta=" + str(delta) + " expected -2: " + f)
        fail += 1
        continue

    write_lf(path, s2)
    print("  ok: " + f.split('/')[-3] + "/" + f.split('/')[-2])
    ok += 1

# =============================================================================
# B1 items 7-9: far-east-rock-cafe — remove ALL 3 figure blocks (page goes photoless)
# File has unusual spacing (blank lines inside figure tags).
# =============================================================================
print("\n=== B1 items 7-9: far-east-rock-cafe (remove all photos) ===")

fercafe = os.path.join(REPO, r"food\vietnam\nha-trang\bars-pubs\far-east-rock-cafe\index.md")
raw = read_bytes(fercafe)
s = raw.decode('utf-8').replace('\r\n', '\n').replace('\r', '\n')
lines_before = s.count('\n')

# Remove figure-1 (standalone before review text)
pat1 = r'\n<figure>\n\n  <img src="/photos/vietnam/nha-trang/far-east-rock-cafe-1\.jpg"[^\n]*>\n\n  <figcaption>Far East Rock Café</figcaption>\n\n</figure>\n'
# Remove grid div with figure-2 and figure-3
pat2 = r'\n<div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;">\n\n<figure>\n\n  <img src="/photos/vietnam/nha-trang/far-east-rock-cafe-2\.jpg"[^\n]*>\n\n  <figcaption>Far East Rock Café</figcaption>\n\n</figure>\n\n<figure>\n\n  <img src="/photos/vietnam/nha-trang/far-east-rock-cafe-3\.jpg"[^\n]*>\n\n  <figcaption>Far East Rock Café</figcaption>\n\n</figure>\n\n</div>\n'

m1 = re.search(pat1, s)
m2 = re.search(pat2, s)

if not m1:
    print("  FAIL: figure-1 pattern not found")
    fail += 1
elif not m2:
    print("  FAIL: grid div pattern not found")
    fail += 1
else:
    s2 = re.sub(pat1, '\n', s, count=1)
    s2 = re.sub(pat2, '\n', s2, count=1)
    lines_after = s2.count('\n')
    delta = lines_after - lines_before
    # Expect to lose the 3 figures + grid wrapper: roughly 7+14 = 21 lines
    if delta >= 0:
        print("  FAIL delta=" + str(delta) + " (expected negative)")
        fail += 1
    else:
        write_lf(fercafe, s2)
        print("  ok: far-east-rock-cafe (removed " + str(-delta) + " lines, page is now photoless)")
        ok += 1

print("\nok=" + str(ok) + " fail=" + str(fail))
if fail:
    sys.exit(1)
