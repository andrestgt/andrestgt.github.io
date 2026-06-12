#!/usr/bin/env python3
"""Standing photo-resize script for andrestgt.github.io.

Run on any new photo batch BEFORE git staging.
Example: python _fixes/resize_new_photos.py travels/new-trip/photos/

Walks the paths given as arguments (files or directories). For each image
(.jpg/.jpeg/.png/.webp) wider than 1700px, resizes to a max 1700px long edge
(aspect preserved, Lanczos) and saves as JPEG quality 85, preserving the EXIF
block and ICC profile. Images already <= 1700px wide are left byte-identical.
Never deletes or renames; resizes strictly in place.

No arguments => print usage and exit. It will never sweep the repo on its own.
"""

import os
import sys

from PIL import Image

MAX_EDGE = 1700
EXTS = {".jpg", ".jpeg", ".png", ".webp"}


def iter_images(paths):
    for p in paths:
        if os.path.isfile(p):
            if os.path.splitext(p)[1].lower() in EXTS:
                yield p
        elif os.path.isdir(p):
            for root, _, files in os.walk(p):
                for f in sorted(files):
                    if os.path.splitext(f)[1].lower() in EXTS:
                        yield os.path.join(root, f)
        else:
            print(f"  ! not found: {p}", file=sys.stderr)


def kb(path):
    return os.path.getsize(path) / 1024.0


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 1

    resized = skipped = errors = 0
    for path in iter_images(argv[1:]):
        try:
            with Image.open(path) as im:
                ow, oh = im.size
                if ow <= MAX_EDGE:
                    print(f"skip   {path}  {ow}x{oh}  (<= {MAX_EDGE}px)")
                    skipped += 1
                    continue

                old_kb = kb(path)
                exif = im.info.get("exif")
                icc = im.info.get("icc_profile")

                scale = MAX_EDGE / float(max(ow, oh))
                nw, nh = round(ow * scale), round(oh * scale)
                out = im.convert("RGB").resize((nw, nh), Image.LANCZOS)

                save_kwargs = {"quality": 85}
                if exif:
                    save_kwargs["exif"] = exif
                if icc:
                    save_kwargs["icc_profile"] = icc
                out.save(path, "JPEG", **save_kwargs)

            new_kb = kb(path)
            print(
                f"resize {path}  {ow}x{oh} -> {nw}x{nh}  "
                f"{old_kb:.0f}KB -> {new_kb:.0f}KB"
            )
            resized += 1
        except Exception as e:  # noqa: BLE001
            print(f"  ! error {path}: {e}", file=sys.stderr)
            errors += 1

    print(f"\nDone. resized={resized} skipped={skipped} errors={errors}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
