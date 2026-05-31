#!/usr/bin/env python3
"""Step 3 C4: normalize CZK/LAK raw-currency price fields to Kc/lak symbol format."""
import os, re, sys

REPO = r"C:\Users\andre\Documents\andrestgt.github.io"

def read_bytes(path):
    with open(path, 'rb') as f: return f.read()

def write_lf(path, data):
    if isinstance(data, str): data = data.encode('utf-8')
    data = data.replace(b'\r\n', b'\n').replace(b'\r', b'\n')
    with open(path, 'wb') as f: f.write(data)

fixes = [
    # CZK already converted in a prior run — skip
    # ("food/czechia/budweis/restaurants/minipivovar-krajinska-27/index.md",
    #  "CZK 600–1,000", "Kč 600-1,000"),
    # ("food/czechia/olomouc/restaurants/sunrise-vietnamese/index.md",
    #  "CZK 350–500", "Kč 350-500"),
    # LAK dot-thousands -> lak k notation
    ("food/laos/luang-prabang/restaurants/pizza-phan-luang/index.md",
     "LAK 200.000", "₭200k"),
    ("food/laos/luang-prabang/restaurants/sabaidee-restaurant/index.md",
     "LAK 40.000-60.000", "₭40k-60k"),
    # LAK k-format -> just prefix change
    ("food/laos/luang-prabang/restaurants/secret-pizza/index.md",
     "LAK 200k-250k", "₭200k-250k"),
    ("food/laos/luang-prabang/restaurants/tamarind/index.md",
     "LAK 150k-250k", "₭150k-250k"),
    ("food/laos/nong-khiaw/restaurants/chennai-restaurant/index.md",
     "LAK 80k", "₭80k"),
    ("food/laos/nong-khiaw/restaurants/coco-home-bar/index.md",
     "LAK 100k-120k", "₭100k-120k"),
    ("food/laos/nong-khiaw/restaurants/keochampar-restaurant/index.md",
     "LAK 80k-100k", "₭80k-100k"),
    ("food/laos/nong-khiaw/restaurants/ma-ma-alex-restaurant/index.md",
     "LAK 80k-100k", "₭80k-100k"),
    ("food/laos/vang-vieng/restaurants/amigos-restaurant/index.md",
     "LAK 100k-150k", "₭100k-150k"),
    ("food/laos/vang-vieng/restaurants/nazim-indian-restaurant/index.md",
     "LAK 100k-120k", "₭100k-120k"),
    ("food/laos/vang-vieng/restaurants/viman-german-restaurant/index.md",
     "LAK 100k-120k", "₭100k-120k"),
    ("food/laos/vientiane/restaurants/tyson-kitchen/index.md",
     "LAK 200k", "₭200k"),
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
    lines_after = s2.count('\n')
    if lines_after != lines_before:
        print("  FAIL line count changed (" + str(lines_before) + "->" + str(lines_after) + "): " + f.split('/')[-2])
        fail += 1; continue

    write_lf(path, s2)
    sys.stdout.buffer.write(("  ok: " + f.split('/')[-2] + "\n").encode('utf-8'))
    ok += 1

print("\nok=" + str(ok) + " fail=" + str(fail))
if fail: sys.exit(1)
