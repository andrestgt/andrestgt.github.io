"""
lock_photos.py - add 'photos_locked: true' to every venue page (review: true)
under a given path. Idempotent; skips landing pages. Reusable for any scope.

    python _fixes/lock_photos.py --path food/thailand/chiang-mai/bars-pubs
    python _fixes/lock_photos.py --path food/thailand/chiang-mai/bars-pubs --apply
"""
from __future__ import annotations
import argparse, glob, re

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", required=True, help="dir under repo, e.g. food/thailand/chiang-mai/bars-pubs")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    added = already = skipped = 0
    for p in sorted(glob.glob(f"{args.path}/**/index.md", recursive=True)):
        t = open(p, encoding="utf-8").read()
        m = re.match(r"^(---\n.*?\n)(---)", t, re.S)
        if not m:
            continue
        fm = m.group(1)
        if not re.search(r"^review:\s*true", fm, re.M):
            skipped += 1; continue
        if re.search(r"^photos_locked:", fm, re.M):
            already += 1; continue
        added += 1
        print("  LOCK", re.split(r"[\\/]", p)[-2])
        if args.apply:
            open(p, "w", encoding="utf-8", newline="").write(fm + "photos_locked: true\n---" + t[m.end():])
    print(f"\n{'APPLIED' if args.apply else 'DRY-RUN'}: {added} newly locked, "
          f"{already} already locked, {skipped} non-venue skipped.")

if __name__ == "__main__":
    main()
