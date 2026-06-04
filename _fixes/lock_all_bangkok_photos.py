"""
lock_all_bangkok_photos.py - add 'photos_locked: true' to EVERY Bangkok venue
page (all categories) that doesn't already have it. Idempotent; skips landing
pages (only acts on review: true). Bangkok photos are finalised by hand.

    python _fixes/lock_all_bangkok_photos.py            # dry-run
    python _fixes/lock_all_bangkok_photos.py --apply
"""
from __future__ import annotations
import argparse, glob, re

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="."); ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    added = already = skipped = 0
    for p in sorted(glob.glob(f"{args.root}/food/thailand/bangkok/**/index.md", recursive=True)):
        t = open(p, encoding="utf-8").read()
        m = re.match(r"^(---\n.*?\n)(---)", t, re.S)
        if not m:
            continue
        fm = m.group(1)
        if not re.search(r"^review:\s*true", fm, re.M):   # skip landing/index pages
            skipped += 1; continue
        if re.search(r"^photos_locked:", fm, re.M):
            already += 1; continue
        new = fm + "photos_locked: true\n"
        added += 1
        print("  LOCK", re.split(r"[\\/]", p)[-2])
        if args.apply:
            open(p, "w", encoding="utf-8", newline="").write(new + "---" + t[m.end():])
    print(f"\n{'APPLIED' if args.apply else 'DRY-RUN'}: {added} newly locked, "
          f"{already} already locked, {skipped} non-venue pages skipped.")

if __name__ == "__main__":
    main()
