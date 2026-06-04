"""
link_cm_orphans.py - insert existing-but-unreferenced repo photos into their
Chiang Mai pages (the orphan-linking fix). Files already exist in /photos/;
this only edits the markdown. Idempotent; skips photos_locked pages and any
photo already referenced. 32-coffee-hill intentionally excluded (locked).

    python _fixes/link_cm_orphans.py            # dry-run
    python _fixes/link_cm_orphans.py --apply
"""
from __future__ import annotations
import argparse, re

CITY = "chiang-mai"
TARGETS = {
    "food/thailand/chiang-mai/cafes/baristro-asian-style/index.md":
        ["baristro-asian-style-main.jpg", "baristro-asian-style-main-2.jpg"],
    "food/thailand/chiang-mai/cafes/akha-ama/index.md":
        ["akha-ama-1.jpg"],
}

def figure(photo, title):
    return (f'<figure>\n  <img src="/photos/thailand/{CITY}/{photo}" alt="{title}">\n'
            f'  <figcaption>{title}</figcaption>\n</figure>')

def build_block(photos, title):
    figs = [figure(p, title) for p in photos]
    if len(figs) == 1:
        return figs[0]
    return ('<div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;">\n'
            + "\n".join(figs) + "\n</div>")

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    for path, photos in TARGETS.items():
        try:
            t = open(path, encoding="utf-8").read()
        except FileNotFoundError:
            print("  MISSING PAGE:", path); continue
        fm = re.match(r"^---\n(.*?)\n---", t, re.S)
        if fm and re.search(r"^photos_locked:\s*true", fm.group(1), re.M):
            print("  SKIP (locked):", path.split(CITY+'/')[1]); continue
        title = re.search(r"^title:\s*(.+)$", t, re.M).group(1).strip()
        todo = [p for p in photos if p not in t]
        if not todo:
            print("  already linked:", path.split(CITY+'/')[1]); continue
        m = re.search(r"^#{1,3} +Ratings\b", t, re.M)
        if not m:
            print("  NO RATINGS HEADING:", path); continue
        block = build_block(todo, title)
        new = t[:m.start()] + block + "\n\n" + t[m.start():]
        print(f"  ADD {len(todo)} -> {path.split(CITY+'/')[1]}: {', '.join(todo)}")
        if args.apply:
            open(path, "w", encoding="utf-8", newline="").write(new)
    print(f"\n{'APPLIED' if args.apply else 'DRY-RUN'} done.")

if __name__ == "__main__":
    main()
