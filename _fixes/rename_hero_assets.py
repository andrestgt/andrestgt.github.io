"""
rename_hero_assets.py - rename the 6 German hero backgrounds with umlauts in the
filename to ASCII (matching the ASCII city slugs), and update the matching url()
refs in _layouts/default.html in the same pass so they never get out of sync.
Old names are written as \\u escapes so this script's own source stays pure ASCII
and survives any Windows download. default.html is the ONLY referrer (verified).
Idempotent.

    python _fixes/rename_hero_assets.py            # dry-run
    python _fixes/rename_hero_assets.py --apply
"""
from __future__ import annotations
import argparse, os

BG = "photos/background"
LAYOUT = "_layouts/default.html"

RENAMES = [
    ("allg\u00e4uhead.jpg",        "allgaeuhead.jpg"),
    ("dinkelsb\u00fchlhead.jpg",   "dinkelsbuehlhead.jpg"),
    ("k\u00f6lnhead.jpg",          "koelnhead.jpg"),
    ("m\u00fcnchenhead.jpg",       "muenchenhead.jpg"),
    ("n\u00fcrnberghead.jpg",      "nuernberghead.jpg"),
    ("saarbr\u00fcckenhead.jpg",   "saarbrueckenhead.jpg"),
]

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    t = open(LAYOUT, encoding="utf-8").read()
    orig = t
    for old, new in RENAMES:
        op, npath = os.path.join(BG, old), os.path.join(BG, new)
        # rename file
        if os.path.exists(op):
            print(f"  RENAME file: {old} -> {new}")
            if args.apply:
                os.replace(op, npath)
        elif os.path.exists(npath):
            print(f"  file already renamed: {new}")
        else:
            print(f"  !! file not found: {op} (run on the machine that has /photos)")
        # update ref
        ref_old, ref_new = f"/{BG}/{old}", f"/{BG}/{new}"
        if ref_old in t:
            t = t.replace(ref_old, ref_new)
            print(f"  update ref: {old} -> {new}")
    if t != orig and args.apply:
        open(LAYOUT, "w", encoding="utf-8", newline="").write(t)
    print(f"\n{'APPLIED' if args.apply else 'DRY-RUN'} done.")

if __name__ == "__main__":
    main()
