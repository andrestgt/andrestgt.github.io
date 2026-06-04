"""
cuisine_to_type.py - standardise the Practical-block label on every venue page
from '**Cuisine:**' to '**Type:**'. The leading icon (🍽️/☕/🍺) is untouched.

Run from repo root:
    python _fixes/cuisine_to_type.py            # dry-run (lists files)
    python _fixes/cuisine_to_type.py --apply     # write changes
"""
from __future__ import annotations

import argparse, glob

OLD = "**Cuisine:**"
NEW = "**Type:**"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    changed = 0
    for p in glob.glob(f"{args.root}/food/**/index.md", recursive=True):
        with open(p, encoding="utf-8") as f:
            t = f.read()
        if OLD in t:
            changed += 1
            print(p.split("food/")[-1] if False else p)
            if args.apply:
                with open(p, "w", encoding="utf-8", newline="") as f:
                    f.write(t.replace(OLD, NEW))
    print(f"\n{'APPLIED' if args.apply else 'DRY-RUN'}: {changed} files contain '{OLD}'")


if __name__ == "__main__":
    main()
