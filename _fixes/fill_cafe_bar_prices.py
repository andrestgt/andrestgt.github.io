"""
fill_cafe_bar_prices.py - write the agreed price tier into each of the 28
previously-empty cafe/bar pages. Values are an explicit, reviewed mapping
below - nothing is inferred at runtime.

Canonical line written:  💰 **Price level:** <value>

- For 27 pages: replaces the empty '—' value.
- For Tiffins (Vietnam): no price line exists, so the line is inserted right
  after the Type/Cuisine line in the Practical block.

Run from repo root:
    python _fixes/fill_cafe_bar_prices.py           # dry-run (shows each change)
    python _fixes/fill_cafe_bar_prices.py --apply    # write changes
"""
from __future__ import annotations

import argparse, re
from pathlib import Path

# path (under food/) -> agreed tier
FILLS = {
    # Cambodia
    "cambodia/battambang/cafes/kinyei-cafe": "inexpensive",
    "cambodia/battambang/cafes/the-kitchen": "moderate",
    "cambodia/phnom-penh/bars-pubs/doors-music-tapas": "moderate",
    # Germany (all moderate)
    "germany/baden-wuerttemberg/heidelberg/cafes/caf-villa": "moderate",
    "germany/baden-wuerttemberg/schwarzwald/cafes/caf-bachbeck-konditorei": "moderate",
    "germany/baden-wuerttemberg/stuttgart/bars-pubs/wirtshaus-troll": "moderate",
    "germany/baden-wuerttemberg/stuttgart/cafes/caf-lesbar": "moderate",
    "germany/baden-wuerttemberg/stuttgart/cafes/caff-bar": "moderate",
    "germany/baden-wuerttemberg/stuttgart/cafes/coffreez-frozen-coffeebar-koenigstrasse": "moderate",
    "germany/bayern/fuessen/cafes/baeckerei-brunners": "moderate",
    "germany/bayern/nuernberg/cafes/hammons-brot-und-kaffeegenuss": "moderate",
    "germany/berlin/berlin/bars-pubs/que-pasa": "moderate",
    "germany/berlin/berlin/cafes/bonanza-coffee-heroes": "moderate",
    "germany/berlin/berlin/cafes/firstcrack-coffee-roasters-cafe-pakolat-berlin": "moderate",
    "germany/berlin/berlin/cafes/the-visit-coffee-roastery": "expensive",  # review explicitly says "expensive prices"
    "germany/brandenburg/potsdam/cafes/die-espressonisten-store-craft-coffeeshop": "moderate",
    "germany/nrw/koeln/cafes/espresso-perfetto-koeln-gmbh": "moderate",
    "germany/nrw/muenster/cafes/fyal-central": "moderate",
    "germany/saarland/saarbruecken/bars-pubs/wallys-irish-pub-saarbruecken": "moderate",
    "germany/saarland/saarbruecken/cafes/henrys-eismanufaktur": "moderate",
    "germany/sachsen/dresden/cafes/combo": "moderate",
    "germany/sachsen/dresden/cafes/oswaldz": "moderate",
    "germany/sachsen/leipzig/bars-pubs/felsenkeller-leipzig": "moderate",
    "germany/thueringen/erfurt/cafes/barista-coffeeshop-erfurt": "moderate",
    # Malaysia
    "malaysia/ipoh/cafes/bareeseta-cafe": "moderate",
    # Thailand
    "thailand/krabi/bars-pubs/pooky-olearys-thairish-pub": "moderate to expensive",
    "thailand/krabi/cafes/prince-coffee": "moderate",
    # Vietnam (no price line yet - will be inserted)
    "vietnam/nha-trang/cafes/tiffins-desserts-and-coffee": "moderate",
}

PRICE_RE = re.compile(r"^.*?\*\*Price level:\*\*[ \t]*.*$", re.MULTILINE)
TYPE_RE = re.compile(r"^.*\*\*(?:Cuisine|Type):\*\*.*$", re.MULTILINE)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    done = inserted = missing = 0
    for rel, tier in FILLS.items():
        p = Path(args.root) / "food" / f"{rel}/index.md"
        if not p.exists():
            missing += 1; print(f"MISSING FILE  {rel}"); continue
        t = p.read_text(encoding="utf-8")
        new_line = f"\U0001f4b0 **Price level:** {tier}"

        if PRICE_RE.search(t):
            old = PRICE_RE.search(t).group(0)
            if old == new_line:
                print(f"already ok    {rel}  [{tier}]"); continue
            t2 = PRICE_RE.sub(lambda m: new_line, t, count=1)
            done += 1
            print(f"FILL    {rel}  ->  {tier}")
        else:
            # no price line: insert after the Type/Cuisine line
            m = TYPE_RE.search(t)
            if not m:
                missing += 1; print(f"NO TYPE LINE  {rel} (insert manually)"); continue
            t2 = t[:m.end()] + "\n" + new_line + t[m.end():]
            inserted += 1
            print(f"INSERT  {rel}  ->  {tier}  (new line added)")

        if args.apply:
            p.write_text(t2, encoding="utf-8", newline="")

    print(f"\n{'APPLIED' if args.apply else 'DRY-RUN'}: "
          f"{done} filled, {inserted} inserted, {missing} problems, "
          f"{len(FILLS)} total.")


if __name__ == "__main__":
    main()
