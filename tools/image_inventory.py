import os, sys
from PIL import Image

ROOT = r"C:\Users\andre\Documents\andrestgt.github.io"
IMG_EXT = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tif", ".tiff"}
# text extensions to scan for references
TEXT_EXT = {".md", ".markdown", ".html", ".htm", ".liquid", ".yml", ".yaml",
            ".json", ".scss", ".css", ".txt", ".rb", ".xml", ".js", ".csv"}
SKIP_DIRS = {".git"}
# generated artifacts that must NOT be counted as references to themselves
SKIP_BASENAMES = {"_listA_unreferenced.txt", "_listB_oversized.txt"}

def walk_files():
    for dp, dn, fn in os.walk(ROOT):
        dn[:] = [d for d in dn if d not in SKIP_DIRS]
        for f in fn:
            yield os.path.join(dp, f)

# 1. collect images
images = []
for p in walk_files():
    ext = os.path.splitext(p)[1].lower()
    if ext in IMG_EXT:
        images.append(p)

# 2. build big text blob from all text files
blob_parts = []
for p in walk_files():
    ext = os.path.splitext(p)[1].lower()
    if os.path.basename(p) in SKIP_BASENAMES:
        continue
    if ext in TEXT_EXT:
        try:
            with open(p, "r", encoding="utf-8", errors="ignore") as fh:
                blob_parts.append(fh.read())
        except Exception as e:
            sys.stderr.write(f"READERR {p}: {e}\n")
blob = "\n".join(blob_parts)
sys.stderr.write(f"scanned {len(blob_parts)} text files, blob {len(blob)} chars\n")

unreferenced = []   # (path, size)
oversized = []      # (path, w, h, size)
errors = []
total_img_size = 0

for p in sorted(images):
    rel = os.path.relpath(p, ROOT).replace("\\", "/")
    base = os.path.basename(p)
    try:
        size = os.path.getsize(p)
    except Exception:
        size = 0
    total_img_size += size
    used = base in blob
    try:
        with Image.open(p) as im:
            w, h = im.size
    except Exception as e:
        w = h = -1
        errors.append((rel, str(e)))
    if not used:
        unreferenced.append((rel, size))
    else:
        if w > 0 and max(w, h) > 1700:
            oversized.append((rel, w, h, size))

def human(n):
    for u in ["B","KB","MB","GB"]:
        if n < 1024: return f"{n:.1f}{u}"
        n /= 1024
    return f"{n:.1f}TB"

print("="*70)
print(f"TOTAL IMAGES: {len(images)}  (total size {human(total_img_size)})")
print(f"DECODE ERRORS: {len(errors)}")
for rel,e in errors:
    print(f"   !! {rel}: {e}")
print("="*70)

unref_total = sum(s for _,s in unreferenced)
print(f"\n### LIST A — UNREFERENCED (delete candidates): {len(unreferenced)} files, reclaimable {human(unref_total)}")
for rel,size in sorted(unreferenced, key=lambda x:-x[1]):
    print(f"   {human(size):>9}  {rel}")

print(f"\n### LIST B — REFERENCED BUT OVERSIZED (long edge > 1700px): {len(oversized)} files")
for rel,w,h,size in sorted(oversized, key=lambda x:-(x[1]*x[2])):
    print(f"   {w}x{h}  {human(size):>9}  {rel}")

# write machine-readable List A for step 2
with open(os.path.join(ROOT, "tools", "_listA_unreferenced.txt"), "w", encoding="utf-8") as fh:
    for rel,size in sorted(unreferenced):
        fh.write(rel + "\n")
with open(os.path.join(ROOT, "tools", "_listB_oversized.txt"), "w", encoding="utf-8") as fh:
    for rel,w,h,size in sorted(oversized):
        fh.write(f"{rel}\t{w}x{h}\t{size}\n")
print("\n(wrote tools/_listA_unreferenced.txt and tools/_listB_oversized.txt)")
