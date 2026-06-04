"""
lock_bangkok_photos.py - add 'photos_locked: true' to the front matter of:
  - ALL Bangkok bars-pubs pages
  - Bangkok cafe pages alphabetically through 'not-just-another-cup'
so the photo-reconciliation run skips them (deliberate deletions).

    python _fixes/lock_bangkok_photos.py            # dry-run
    python _fixes/lock_bangkok_photos.py --apply
"""
from __future__ import annotations
import argparse, glob, re

CUTOFF = "not-just-another-cup"

def targets(root):
    bars = sorted(glob.glob(f"{root}/food/thailand/bangkok/bars-pubs/*/index.md"))
    cafes = sorted(glob.glob(f"{root}/food/thailand/bangkok/cafes/*/index.md"),
                   key=lambda p: re.split(r"[\\/]", p)[-2])
    slugs = [re.split(r"[\\/]", p)[-2] for p in cafes]
    if CUTOFF in slugs:
        cafes = cafes[:slugs.index(CUTOFF) + 1]
    else:
        cafes = [p for p in cafes if re.split(r"[\\/]", p)[-2] <= CUTOFF]
    return bars + cafes

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="."); ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    added = already = 0
    for p in targets(args.root):
        t = open(p, encoding="utf-8").read()
        m = re.match(r"^(---\n.*?\n)(---)", t, re.S)
        if not m:
            print("  NO FRONT MATTER:", p); continue
        fm = m.group(1)
        if re.search(r"^photos_locked:", fm, re.M):
            already += 1; continue
        new = fm + "photos_locked: true\n"
        added += 1
        print("  LOCK", p.split("food/")[-1])
        if args.apply:
            open(p, "w", encoding="utf-8", newline="").write(new + "---" + t[m.end():])
    print(f"\n{'APPLIED' if args.apply else 'DRY-RUN'}: {added} locked, {already} already locked.")

if __name__ == "__main__":
    main()
