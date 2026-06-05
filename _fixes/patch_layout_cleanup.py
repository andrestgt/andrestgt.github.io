"""
patch_layout_cleanup.py - two zero-risk surgical fixes to _layouts/default.html:
  (a) delete the dead Portugal hero rule (portugalhead country rule that can
      never win against the portugalhero !important on the same selector).
  (b) scope the hero overlay to .has-overlay so the `hero_overlay: false`
      front-matter toggle actually works. No visual change to existing pages
      (they all get has-overlay by default); pages that set hero_overlay:false
      will now correctly drop the dark overlay.
Idempotent. Touches nothing else.

    python _fixes/patch_layout_cleanup.py            # dry-run
    python _fixes/patch_layout_cleanup.py --apply
"""
from __future__ import annotations
import argparse

PATH = "_layouts/default.html"

# (a) dead Portugal rule - delete the whole line
DEAD_PORTUGAL = '    body.food.food-country.portugal .site-hero { background-image: url("/photos/background/portugalhead.jpg"); }\n'

# (b) overlay scoping
OVERLAY_OLD = "    .site-hero::before {"
OVERLAY_NEW = "    .site-hero.has-overlay::before {"

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    t = open(PATH, encoding="utf-8").read()
    orig = t

    # (a)
    if DEAD_PORTUGAL in t:
        t = t.replace(DEAD_PORTUGAL, "", 1)
        print("  PATCH (a): removed dead Portugal hero rule")
    else:
        print("  (a) already gone / not found")

    # (b)
    if OVERLAY_NEW in t:
        print("  (b) overlay already scoped")
    elif OVERLAY_OLD in t:
        t = t.replace(OVERLAY_OLD, OVERLAY_NEW, 1)
        print("  PATCH (b): scoped overlay to .has-overlay (toggle now works)")
    else:
        print("  !! (b) overlay rule not found -- layout may have changed")

    if t != orig and args.apply:
        open(PATH, "w", encoding="utf-8", newline="").write(t)
        print("  written.")
    print(f"\n{'APPLIED' if args.apply else 'DRY-RUN'} done.")

if __name__ == "__main__":
    main()
