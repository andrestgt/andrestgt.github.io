"""
patch_mobile_noclick.py - make venue/photo thumbnails non-clickable on MOBILE
(lightbox opens on desktop only). Two surgical edits to _layouts/default.html:
  1. JS: handleOpen() bails out below the 1024px desktop breakpoint.
  2. CSS: zoom-in cursor + hover dim apply on desktop only.
Idempotent. Additive/surgical - touches nothing else in the locked layout.

    python _fixes/patch_mobile_noclick.py            # dry-run
    python _fixes/patch_mobile_noclick.py --apply
"""
from __future__ import annotations
import argparse

PATH = "_layouts/default.html"

JS_OLD = """        function handleOpen(e) {
          e.preventDefault();
          e.stopPropagation();
          openLightbox(img.src, img.alt);
        }"""
JS_NEW = """        function handleOpen(e) {
          // Mobile view: thumbnails are not clickable (no lightbox). Desktop only.
          if (!window.matchMedia('(min-width: 1024px)').matches) return;
          e.preventDefault();
          e.stopPropagation();
          openLightbox(img.src, img.alt);
        }"""

CSS_OLD = """    .page-body img {
      cursor: zoom-in;
      transition: opacity 0.15s ease;
    }

    .page-body img:hover { opacity: 0.88; }"""
CSS_NEW = """    .page-body img {
      cursor: default;
      transition: opacity 0.15s ease;
    }

    @media (min-width: 1024px) {
      .page-body img { cursor: zoom-in; }
      .page-body img:hover { opacity: 0.88; }
    }"""

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    t = open(PATH, encoding="utf-8").read()
    orig = t
    for label, old, new in [("JS handleOpen", JS_OLD, JS_NEW), ("CSS cursor", CSS_OLD, CSS_NEW)]:
        if new in t:
            print(f"  already patched: {label}")
        elif old in t:
            t = t.replace(old, new, 1)
            print(f"  PATCH: {label}")
        else:
            print(f"  !! NOT FOUND (skipped): {label} -- layout may have changed")
    if t != orig and args.apply:
        open(PATH, "w", encoding="utf-8", newline="").write(t)
        print("  written.")
    print(f"\n{'APPLIED' if args.apply else 'DRY-RUN'} done.")

if __name__ == "__main__":
    main()
