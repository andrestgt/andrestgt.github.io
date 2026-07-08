#!/usr/bin/env python3
# Create a Taytay food landing and move Leonida's + Casa Rosa there from el-nido.
import os, re, shutil

BASE = "food/philippines"
EN_R = os.path.join(BASE, "el-nido", "restaurants")
TY   = os.path.join(BASE, "taytay")
TY_R = os.path.join(TY, "restaurants")

os.makedirs(TY_R, exist_ok=True)

# 1. Move the two review pages (rename works on this mount; delete does not)
for slug in ["leonidas", "casa-rosa-seaview-inn"]:
    src = os.path.join(EN_R, slug)
    dst = os.path.join(TY_R, slug)
    if os.path.isdir(src):
        if os.path.isdir(dst):
            # dst already exists (rerun) - skip
            pass
        else:
            os.rename(src, dst)
            print("MOVED", src, "->", dst)
    else:
        print("SRC MISSING (already moved?)", src)

# 2. Taytay city landing
landing = """---
layout: default
section: food
country: philippines
city: taytay
title: Taytay – Food & Drink
subtitle: Restaurants on the road between El Nido and Puerto Princesa
---

# Taytay

Reviews grouped by category. Taytay sits on the long ride between El Nido and Puerto Princesa, a handy place to break the journey.

## Restaurants
- [Restaurants](/food/philippines/taytay/restaurants/)
"""
open(os.path.join(TY, "index.md"), "w", encoding="utf-8").write(landing)
print("WROTE", os.path.join(TY, "index.md"))

# 3. Taytay restaurants category index
cat = """---
layout: default
section: food
city: taytay
category: restaurants
title: Restaurants
subtitle: Restaurants in and around Taytay
---

# Restaurants

---

## Leonida's
*Taytay, Palawan · Filipino*
An unexpected gem in the middle of nowhere, a beautifully decorated garden café with outstanding Filipino food and fair prices.
→ [Read the full review](/food/philippines/taytay/restaurants/leonidas/)

---

## Casa Rosa Seaview Inn & Restaurant
*Taytay, Palawan · Filipino*
A very quiet hilltop resort with beautiful views over Taytay bay, a lovely rest stop on the long ride even if the food is so-so.
→ [Read the full review](/food/philippines/taytay/restaurants/casa-rosa-seaview-inn/)

---

**Price level note:**
Price levels refer to the approximate cost for **two people** ordering an average meal **without alcoholic drinks**.
"""
open(os.path.join(TY_R, "index.md"), "w", encoding="utf-8").write(cat)
print("WROTE", os.path.join(TY_R, "index.md"))

# 4. Remove the two entries from el-nido restaurants index
en_idx = os.path.join(EN_R, "index.md")
c = open(en_idx, encoding="utf-8").read()
for slug in ["leonidas", "casa-rosa-seaview-inn"]:
    pat = r"## [^\n]*\n\*[^\n]*\*\n[^\n]*\n→ \[Read the full review\]\(/food/philippines/el-nido/restaurants/" + re.escape(slug) + r"/\)\n\n---\n\n"
    c2 = re.sub(pat, "", c)
    print(("REMOVED" if c2 != c else "NOT-FOUND"), slug, "from el-nido restaurants index")
    c = c2
open(en_idx, "w", encoding="utf-8").write(c)

# 5. Update el-nido city landing note (drop the Taytay parenthetical)
en_city = os.path.join(BASE, "el-nido", "index.md")
c = open(en_city, encoding="utf-8").read()
c = c.replace(
    "Reviews grouped by category. Also covers the route to El Nido (including Leonida's near Taytay).",
    "Reviews grouped by category. Also covers the route north to El Nido.")
open(en_city, "w", encoding="utf-8").write(c)
print("UPDATED el-nido landing note")

# 6. Add Taytay to the Philippines food index (under Palawan)
ph = os.path.join(BASE, "index.md")
c = open(ph, encoding="utf-8").read()
anchor = "- [Port Barton & San Vicente](/food/philippines/port-barton-san-vicente/)\n"
if "taytay" not in c:
    c = c.replace(anchor, anchor + "- [Taytay](/food/philippines/taytay/)\n")
    open(ph, "w", encoding="utf-8").write(c)
    print("ADDED Taytay to philippines food index")
else:
    print("Taytay already in philippines index")

# 7. tidy leftover rename-test junk into _to_delete
td = "_to_delete"
os.makedirs(td, exist_ok=True)
for junk in ["food/philippines/_mvtest_dst_x", "food/philippines/_mvtest_dst", "food/philippines/_mvtest_src"]:
    if os.path.exists(junk):
        try:
            os.rename(junk, os.path.join(td, os.path.basename(junk)))
            print("parked junk:", junk)
        except Exception as e:
            print("junk move failed", junk, e)

print("DONE")
