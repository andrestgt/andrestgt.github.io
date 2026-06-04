"""
normalize_thai_prices.py - make every restaurant / street-food price level
in food/thailand use identical symbols and layout.

Canonical form:  💰 **Price level:** ฿<low>–<high>
  - ฿ prefix glued to the number
  - en-dash – (U+2013) for ranges, no surrounding spaces
  - single value: ฿<n>     open-ended: ฿<n>+
  - never ฿฿, never a 'Bt'/'THB'/'baht' suffix, never a leading —

Strategy: parse the numbers out of each value and re-emit a clean line.
Anything with NO number is left untouched and REPORTED (never invented).

Run from repo root:
    python _fixes/normalize_thai_prices.py            # dry-run (shows diffs)
    python _fixes/normalize_thai_prices.py --apply     # write changes
"""
from __future__ import annotations

import argparse, glob, re, sys

CATS = ("restaurants", "street-food")
LINE_RE = re.compile(r"^.*?\*\*Price level:\*\*[ \t]*(.*)$", re.MULTILINE)
EN = "–"  # –


def canon(raw: str):
    """Return (new_value, status). status in {'ok','empty','ambiguous'}."""
    v = raw.strip()
    open_ended = v.rstrip().endswith("+")
    nums = re.findall(r"\d+", v)
    if not nums:
        return raw, "empty"
    if len(nums) == 1:
        return (f"฿{nums[0]}+" if open_ended else f"฿{nums[0]}"), "ok"
    if len(nums) == 2:
        return f"฿{nums[0]}{EN}{nums[1]}", "ok"
    return raw, "ambiguous"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--apply", action="store_true", help="write changes (default: dry-run)")
    args = ap.parse_args()

    pages = []
    for p in sorted(glob.glob(f"{args.root}/food/thailand/**/index.md", recursive=True)):
        parts = re.split(r"[\\/]", p)  # tolerate Windows '\' separators
        if not any(c in parts for c in CATS):
            continue
        with open(p, encoding="utf-8") as f:
            t = f.read()
        fm = re.match(r"^---\n(.*?)\n---", t, re.S)
        if fm and re.search(r"^review:\s*true", fm.group(1), re.M):
            pages.append((p, t))

    changed = empties = ambiguous = 0
    for p, t in pages:
        m = LINE_RE.search(t)
        if not m:
            print(f"NO PRICE LINE: {p}")
            continue
        raw = m.group(1)
        new_val, status = canon(raw)
        short = p.replace("\\", "/").split("food/thailand/")[-1]
        if status == "empty":
            empties += 1
            print(f"EMPTY  [{raw.strip()}]  {short}")
            continue
        if status == "ambiguous":
            ambiguous += 1
            print(f"AMBIG  [{raw.strip()}]  {short}")
            continue
        new_line = f"\U0001f4b0 **Price level:** {new_val}"
        old_line = m.group(0)
        if old_line != new_line:
            changed += 1
            print(f"FIX    [{raw.strip()}] -> [{new_val}]  {short}")
            if args.apply:
                t2 = t[:m.start()] + new_line + t[m.end():]
                # preserve exact line endings; write bytes as UTF-8 with LF
                with open(p, "w", encoding="utf-8", newline="") as f:
                    f.write(t2)

    print(f"\n{'APPLIED' if args.apply else 'DRY-RUN'}: "
          f"{changed} reformatted, {empties} empty, {ambiguous} ambiguous, "
          f"{len(pages)} pages scanned.")
    if empties:
        print("Empty fields left untouched - fill them in manually (no values invented).")


if __name__ == "__main__":
    main()
