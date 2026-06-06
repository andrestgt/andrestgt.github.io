"""
orphan_photos.py - find (and optionally remove) unreferenced photos.

Scans every .md/.html/.css/.scss/.yml file under the repo for /photos/... references,
walks the photos/ tree, and reports files that exist on disk but aren't
referenced anywhere. Default mode is DRY RUN - nothing is touched.

Run from the repo root:

    python _fixes/orphan_photos.py                  # dry-run report
    python _fixes/orphan_photos.py --soft-delete    # move orphans to _orphans/
    python _fixes/orphan_photos.py --hard-delete --confirm   # rm orphans

Notes / known traps already accounted for:
- Scans the WHOLE file (incl. YAML front matter) so 'hero:' keys are caught.
- Scans _layouts/ and _includes/ so default.html background images are caught.
- Scans .css/.scss/.yml so CSS background-image url() heroes are caught too.
- Case-sensitive comparison (matches GitHub Pages / Linux build).
- URL-decodes %xx in references before comparing.
- Skips the _orphans/ staging dir on subsequent runs.

CANNOT detect external references (e.g. TravelBlog.org posts hotlinking your
photos). Review the report before deleting anything.
"""
from __future__ import annotations

import argparse, os, re, shutil, sys, urllib.parse
from pathlib import Path

IMG_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif", ".svg"}
# Background/hero images are wired up via CSS `background-image: url(...)` in
# assets/css/custom.css and per-page heroes may live in _config.yml / _data,
# so scan those text formats too -- not just .md/.html. (.json is deliberately
# excluded: _fixes/hero_plan.json lists planned-but-not-yet-created heroes and
# would flood the "referenced but missing" list with false entries.)
SCAN_EXTS = {".md", ".html", ".htm", ".css", ".scss", ".sass", ".yml", ".yaml"}

# Top-level folders under photos/ that are NEVER deletion candidates. These
# hold CSS background-image / front-matter heroes whose wiring needs manual
# judgement, so the orphan heuristic must not propose them for deletion.
# (Reference-scan side is untouched -- they simply never enter the candidate set.)
EXCLUDE_DIRS = {"background"}

REF_RE = re.compile(
    r"/photos/[A-Za-z0-9_./%\-+()' ]+?\.(?:jpg|jpeg|png|webp|gif|avif|svg)",
    re.IGNORECASE,
)


def collect_references(root: Path) -> set[str]:
    """Return set of /photos/... paths referenced anywhere in repo content."""
    refs: set[str] = set()
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in SCAN_EXTS:
            # Skip generated/ignored dirs
            if "_site" in p.parts or "_orphans" in p.parts or ".git" in p.parts:
                continue
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for m in REF_RE.findall(text):
                refs.add(urllib.parse.unquote(m))
    return refs


def collect_on_disk(photos_dir: Path) -> list[Path]:
    return [
        p
        for p in photos_dir.rglob("*")
        if p.is_file() and p.suffix.lower() in IMG_EXTS
    ]


def is_excluded(web_path: str) -> bool:
    """True if web_path lives under a protected top-level photos/ folder."""
    parts = web_path.split("/")  # ['', 'photos', '<top>', ...]
    return len(parts) > 2 and parts[2] in EXCLUDE_DIRS


def to_web_path(p: Path, root: Path) -> str:
    return "/" + p.relative_to(root).as_posix()


def fmt_size(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".", help="repo root (default: .)")
    ap.add_argument(
        "--soft-delete",
        action="store_true",
        help="move orphans to _orphans/ mirroring source tree",
    )
    ap.add_argument(
        "--hard-delete",
        action="store_true",
        help="permanently delete orphans (requires --confirm)",
    )
    ap.add_argument(
        "--confirm",
        action="store_true",
        help="required with --hard-delete",
    )
    ap.add_argument("--report", default="_fixes/orphans_report.txt")
    args = ap.parse_args()

    if args.hard_delete and not args.confirm:
        sys.exit("Refusing to hard-delete without --confirm.")
    if args.soft_delete and args.hard_delete:
        sys.exit("Pick one: --soft-delete OR --hard-delete.")

    root = Path(args.root).resolve()
    photos = root / "photos"
    if not photos.is_dir():
        sys.exit(f"No photos/ directory at {photos}")

    print(f"Scanning {root} ...")
    refs = collect_references(root)
    on_disk = collect_on_disk(photos)
    on_disk_paths = {to_web_path(p, root): p for p in on_disk}

    # Deletion candidates = unreferenced files, minus protected folders.
    orphans = sorted(w for w in (set(on_disk_paths) - refs) if not is_excluded(w))
    referenced_missing = sorted(refs - set(on_disk_paths))

    total_size = sum(on_disk_paths[w].stat().st_size for w in on_disk_paths)
    orphan_size = sum(on_disk_paths[w].stat().st_size for w in orphans)

    print(f"  references found:       {len(refs):>6}")
    print(f"  files on disk:          {len(on_disk):>6}  ({fmt_size(total_size)})")
    print(f"  ORPHANS (on disk, no ref): {len(orphans):>6}  ({fmt_size(orphan_size)})")
    print(f"  referenced but MISSING:  {len(referenced_missing):>6}")

    # Write report (always, so the dry-run leaves a trail)
    report = Path(args.root) / args.report
    report.parent.mkdir(parents=True, exist_ok=True)
    with report.open("w", encoding="utf-8") as f:
        f.write(f"ORPHANS ({len(orphans)}, {fmt_size(orphan_size)})\n")
        for w in orphans:
            f.write(f"  {fmt_size(on_disk_paths[w].stat().st_size):>10}  {w}\n")
        f.write(f"\nREFERENCED BUT MISSING ON DISK ({len(referenced_missing)})\n")
        for w in referenced_missing:
            f.write(f"  {w}\n")
    print(f"\nReport written: {report}")

    if not (args.soft_delete or args.hard_delete):
        print("(dry-run; pass --soft-delete or --hard-delete to act)")
        return

    if args.soft_delete:
        staging = root / "_orphans"
        for w in orphans:
            src = on_disk_paths[w]
            dst = staging / src.relative_to(root)
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
        print(f"Moved {len(orphans)} files to {staging}")

    if args.hard_delete:
        for w in orphans:
            on_disk_paths[w].unlink()
        print(f"Deleted {len(orphans)} files.")


if __name__ == "__main__":
    main()
