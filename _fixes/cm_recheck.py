"""
cm_recheck.py - re-run the source-folder photo import for CHIANG MAI, scoped to
cafes / restaurants / street-food only. bars-pubs and any photos_locked:true page
are skipped. Matching is caption->slug (the "petit-peyton" method) PLUS a
near-miss recovery pass that strips branch/variant suffixes (@..., trailing
descriptor words like Cafe/Coffee/Sushi/Bar/Kitchen/Restaurant and mall names)
symmetrically off BOTH the caption and the page name before comparing. Only
confident (unique) matches are imported; everything else is listed un-attributed.

Import rules:
  - hash-dedupe: a source photo whose byte-content already exists on the page is
    skipped (so re-runs are idempotent and never re-add the same image).
  - new files: <slug>-N.jpg, lowercase, numbering continued after the existing max.
  - hero (-1 / first <figure>) is never touched; new photos appended before
    "## Ratings" as side-by-side grid pairs (single <figure> for an odd leftover).
  - <= 10 images total per page (hero included); overflow is reported, not added.

    python _fixes/cm_recheck.py            # DRY-RUN: writes report + plan only
    python _fixes/cm_recheck.py --apply    # copy jpgs + edit pages (no git commit)
"""
from __future__ import annotations
import argparse, glob, hashlib, json, os, re, shutil, unicodedata
from collections import defaultdict

SRC_ROOT = r"D:\Google Photos"
CITY = "chiang-mai"
CITY_CAPTION = "Chiang Mai"
CATS = ("cafes", "restaurants", "street-food")          # bars-pubs deliberately excluded
PAGE_GLOB = "food/thailand/chiang-mai/{cat}/*/index.md"
PHOTOS_DIR = os.path.join("photos", "thailand", "chiang-mai")
PHOTO_URL = "/photos/thailand/chiang-mai/{name}"
MAX_PER_PAGE = 10
REPORT = "_fixes/cm_recheck.txt"
PLAN_CSV = "_fixes/_cm_applyplan.csv"

# trailing descriptor / category words stripped (symmetrically) during near-miss
# recovery only. Order-independent; applied repeatedly from the tail.
DESC_TAIL = {
    "cafe", "coffee", "sushi", "bar", "pub", "kitchen", "restaurant", "eatery",
    "bistro", "buffet", "german", "chinese", "japanese", "izakaya", "breakfast",
    "club", "jungle", "imaginary", "khao", "soi", "thai", "food", "roast",
    "roasted", "grill", "bbq", "brewery", "house",
}


def deaccent(s: str) -> str:
    s = (s or "").replace("’", "'")
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


def norm(s: str) -> str:
    """Compact identity key: deaccent, lowercase, drop all non-alphanumerics."""
    return re.sub(r"[^a-z0-9]", "", deaccent(s).lower())


def tokens(s: str) -> list[str]:
    return [t for t in re.split(r"[^a-z0-9]+", deaccent(s).lower()) if t]


def drop_leading_the(toks: list[str]) -> list[str]:
    """Site convention drops a leading article from slugs (the-baristro-... ->
    baristro-...). Strip a leading 'the' so caption and page compare equal."""
    return toks[1:] if toks and toks[0] == "the" else toks


def ekey(s: str, strip_the: bool) -> str:
    """Exact-match key: compact alphanumerics, optionally minus a leading 'the'."""
    toks = tokens(s)
    return "".join(drop_leading_the(toks) if strip_the else toks)


def head_tokens(name: str) -> list[str]:
    """Near-miss head: drop everything from the first @/-/(/| branch separator
    (en/em dash and '@' and parens), then strip trailing descriptor words."""
    h = re.split(r"\s*[@(|–—]", name or "", 1)[0]
    toks = tokens(h)
    while toks and toks[-1] in DESC_TAIL:
        toks.pop()
    return toks


def hkey(name: str, strip_the: bool) -> str:
    """Near-miss head key, optionally minus a leading 'the'."""
    toks = head_tokens(name)
    return "".join(drop_leading_the(toks) if strip_the else toks)


def md5(path: str) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def front_matter(text: str):
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    return m.group(1) if m else ""


# ----------------------------------------------------------------------------
# 1. Page inventory (cafes/restaurants/street-food, review:true)
# ----------------------------------------------------------------------------
def build_pages():
    pages = []
    for cat in CATS:
        for p in sorted(glob.glob(PAGE_GLOB.format(cat=cat))):
            text = open(p, encoding="utf-8").read()
            fm = front_matter(text)
            if not re.search(r"^review:\s*true", fm, re.M):
                continue
            slug = re.split(r"[\\/]", p)[-2]
            title_m = re.search(r"^title:\s*(.+)$", fm, re.M)
            title = title_m.group(1).strip() if title_m else slug
            locked = bool(re.search(r"^photos_locked:\s*true", fm, re.M))
            # existing photos on disk for this slug -> max N and count
            existing = sorted(glob.glob(os.path.join(PHOTOS_DIR, f"{slug}-*.jpg")))
            nums = [int(m.group(1)) for f in existing
                    if (m := re.search(rf"{re.escape(slug)}-(\d+)\.jpg$", f))]
            # images referenced on the page (count toward the <=10 cap)
            num_refs = len(re.findall(r"<img\s", text))
            pages.append({
                "path": p, "cat": cat, "slug": slug, "title": title,
                "locked": locked, "maxn": max(nums) if nums else 0,
                "num_refs": num_refs, "existing": existing,
                "slug_words": slug.replace("-", " "),
            })
    return pages


# ----------------------------------------------------------------------------
# 2. Walk the source tree: caption -> (folder, file, jpg-path)
# ----------------------------------------------------------------------------
def walk_source():
    """Return (folder_jpg_counts, cm_photos) where cm_photos is a list of dicts
    for every jpg whose caption starts with 'Chiang Mai - '."""
    folder_counts = {}
    cm_photos = []
    total_jpg = 0
    cap_re = re.compile(r"^\s*" + re.escape(CITY_CAPTION) + r"\s*[-–—]\s*(.+?)\s*$")
    for folder in sorted(os.listdir(SRC_ROOT)):
        fdir = os.path.join(SRC_ROOT, folder)
        if not os.path.isdir(fdir):
            continue
        jpgs = 0
        for fn in os.listdir(fdir):
            low = fn.lower()
            if low.endswith((".jpg", ".jpeg")):
                jpgs += 1
            if not low.endswith(".json"):
                continue
            # sidecar metadata: <image>.supplemental-meta*.json
            try:
                meta = json.load(open(os.path.join(fdir, fn), encoding="utf-8"))
            except (ValueError, OSError):
                continue
            desc = (meta.get("description") or "").strip()
            if not desc:
                continue
            m = cap_re.match(desc)
            if not m:
                continue
            img_name = re.sub(r"\.supplemental-met[a-z\-]*\.json$", "", fn, flags=re.I)
            if not img_name.lower().endswith((".jpg", ".jpeg")):
                continue
            img_path = os.path.join(fdir, img_name)
            if not os.path.exists(img_path):
                alt = meta.get("title")            # fall back to recorded filename
                if alt and os.path.exists(os.path.join(fdir, alt)):
                    img_name, img_path = alt, os.path.join(fdir, alt)
                else:
                    continue
            cm_photos.append({"folder": folder, "file": img_name, "path": img_path,
                              "caption": desc, "venue": m.group(1).strip()})
        folder_counts[folder] = jpgs
        total_jpg += jpgs
    return folder_counts, cm_photos, total_jpg


# ----------------------------------------------------------------------------
# 3. Match caption venue -> page (exact, then unique near-miss head)
# ----------------------------------------------------------------------------
def match_photos(cm_photos, pages):
    # four indexes, tried in order: exact / exact[the] / near-miss / near-miss[the].
    # The [the] tiers strip a leading article off BOTH sides (the leading-"the" fix).
    idx = {"exact": defaultdict(list), "exact[the]": defaultdict(list),
           "near-miss": defaultdict(list), "near-miss[the]": defaultdict(list)}
    for pg in pages:
        for k in {ekey(pg["slug"], False), ekey(pg["title"], False)}:
            if k: idx["exact"][k].append(pg)
        for k in {ekey(pg["slug"], True), ekey(pg["title"], True)}:
            if k: idx["exact[the]"][k].append(pg)
        for k in {hkey(pg["slug_words"], False), hkey(pg["title"], False)}:
            if k: idx["near-miss"][k].append(pg)
        for k in {hkey(pg["slug_words"], True), hkey(pg["title"], True)}:
            if k: idx["near-miss[the]"][k].append(pg)

    tiers = [("exact", lambda v: ekey(v, False)),
             ("exact[the]", lambda v: ekey(v, True)),
             ("near-miss", lambda v: hkey(v, False)),
             ("near-miss[the]", lambda v: hkey(v, True))]

    matched = []                        # (page, photo, how)
    unattr_nearmiss = []                # caption looked like a variant but ambiguous/locked
    unattr_nomatch = []                 # no page at all
    for ph in cm_photos:
        chosen, how = None, None
        for tier, keyfn in tiers:
            k = keyfn(ph["venue"])
            cands = idx[tier].get(k, []) if k else []
            uniq = {pg["slug"]: pg for pg in cands}
            if len(uniq) == 1:
                chosen, how = next(iter(uniq.values())), tier
                break
            if len(uniq) >= 2:
                unattr_nearmiss.append((ph, list(uniq.values()), "ambiguous"))
                how = "ambiguous"
                break
        if how == "ambiguous":
            continue
        if chosen is None:
            unattr_nomatch.append(ph)
        elif chosen["locked"]:
            unattr_nearmiss.append((ph, chosen, "locked"))
        else:
            matched.append((chosen, ph, how))
    return matched, unattr_nearmiss, unattr_nomatch


# ----------------------------------------------------------------------------
# 4. Build per-page import plan with hash-dedupe and the <=10 cap
# ----------------------------------------------------------------------------
def build_plan(matched, pages):
    by_page = defaultdict(list)
    for pg, ph, how in matched:
        by_page[pg["slug"]].append((ph, how))

    plan = {}                           # slug -> {page, adds:[(ph,newname,how)], skips:[(ph,reason)]}
    for pg in pages:
        items = by_page.get(pg["slug"])
        if not items:
            continue
        # hashes already present on the page (existing files on disk)
        present = {}
        for f in pg["existing"]:
            try:
                present[md5(f)] = os.path.basename(f)
            except OSError:
                pass
        adds, skips = [], []
        n = pg["maxn"]
        room = MAX_PER_PAGE - pg["num_refs"]
        # stable order: by folder then filename
        for ph, how in sorted(items, key=lambda x: (x[0]["folder"], x[0]["file"])):
            try:
                h = md5(ph["path"])
            except OSError:
                skips.append((ph, "unreadable", how)); continue
            if h in present:
                skips.append((ph, f"dup of {present[h]}", how)); continue
            if room <= 0:
                skips.append((ph, "page already at 10-photo cap", how)); continue
            n += 1
            newname = f"{pg['slug']}-{n}.jpg"
            present[h] = newname
            room -= 1
            adds.append((ph, newname, how))
        plan[pg["slug"]] = {"page": pg, "adds": adds, "skips": skips}
    return plan


# ----------------------------------------------------------------------------
# 5. Page edit: append new photos as side-by-side pairs before "## Ratings"
# ----------------------------------------------------------------------------
def figure_block(url, title):
    return (f'<figure>\n  <img src="{url}" alt="{title}">\n'
            f'  <figcaption>{title}</figcaption>\n</figure>')


def render_new_blocks(newnames, title):
    blocks = []
    i = 0
    while i < len(newnames):
        pair = newnames[i:i + 2]
        figs = [figure_block(PHOTO_URL.format(name=nm), title) for nm in pair]
        if len(pair) == 2:
            blocks.append('<div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;">\n'
                          + "\n".join(figs) + "\n</div>")
        else:
            blocks.append(figs[0])
        i += 2
    return "\n\n".join(blocks)


def apply_to_page(pg, newnames):
    text = open(pg["path"], encoding="utf-8").read()
    block = render_new_blocks(newnames, pg["title"])
    m = re.search(r"\n##\s+Ratings", text)
    if not m:
        raise RuntimeError(f"no '## Ratings' in {pg['path']}")
    new_text = text[:m.start()] + "\n" + block + "\n" + text[m.start():]
    with open(pg["path"], "w", encoding="utf-8", newline="\n") as f:
        f.write(new_text)


# ----------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--exclude", default="", help="comma-separated slugs to drop from imports")
    args = ap.parse_args()
    excluded = {s.strip() for s in args.exclude.split(",") if s.strip()}

    pages = build_pages()
    locked_pages = [pg for pg in pages if pg["locked"]]
    folder_counts, cm_photos, total_jpg = walk_source()
    matched, near, nomatch = match_photos(cm_photos, pages)
    plan = build_plan(matched, pages)
    # operator-excluded slugs: drop their imports (recorded below as held-back)
    held_back = []
    for slug in excluded:
        if slug in plan:
            for ph, newname, how in plan[slug]["adds"]:
                held_back.append((plan[slug]["page"], ph, how))
            plan[slug]["adds"] = []

    total_add = sum(len(v["adds"]) for v in plan.values())
    total_dup = sum(1 for v in plan.values() for s in v["skips"] if "dup" in s[1])
    pages_touched = [s for s, v in plan.items() if v["adds"]]
    n_exact = sum(1 for pg, ph, how in matched if not how.startswith("near-miss"))
    n_nearmiss = len(matched) - n_exact
    recovered = [(v["page"], a) for v in plan.values() for a in v["adds"]
                 if a[2].startswith("near-miss")]
    # leading-"the" fix contribution: any add whose tier required dropping a leading article
    the_adds = [(v["page"], a) for v in plan.values() for a in v["adds"] if a[2].endswith("[the]")]
    the_pages = sorted({pg["slug"] for pg, a in the_adds})

    # ---- apply (copies + edits) ----
    if args.apply:
        for slug, v in plan.items():
            if not v["adds"]:
                continue
            for ph, newname, _ in v["adds"]:
                shutil.copy2(ph["path"], os.path.join(PHOTOS_DIR, newname))
            apply_to_page(v["page"], [nm for _, nm, _ in v["adds"]])

    # ---- report ----
    L = []
    w = L.append
    mode = "APPLIED" if args.apply else "DRY-RUN"
    w("CHIANG MAI PHOTO RE-IMPORT  (cafes / restaurants / street-food)")
    w(f"Mode: {mode}   Source root: {SRC_ROOT}   Matching: caption->slug + near-miss recovery")
    w("")
    w("SUMMARY")
    w(f"  In-scope pages (review:true, 3 categories): {len(pages)}")
    w(f"  Locked pages skipped (photos_locked:true):  {len(locked_pages)}  "
      f"[bars-pubs excluded by scope entirely]")
    w(f"  Chiang Mai captioned photos found:          {len(cm_photos)}")
    w(f"  Confident matches:                          {len(matched)}  "
      f"({n_exact} exact, {n_nearmiss} near-miss recovery)")
    w(f"  Photos to import (net-new):                 {total_add} across {len(pages_touched)} pages")
    w(f"  Caption-matched but already on page (hash dup-skip): {total_dup}")
    w(f"  ADDED by leading-\"the\" fix (net-new):        {len(the_adds)} across {len(the_pages)} pages")
    w("")
    w("=" * 70)
    w("FOLDER COVERAGE (recursive jpg counts)")
    w("=" * 70)
    for folder in sorted(folder_counts):
        w(f"  {folder_counts[folder]:>6}  {folder}")
    w(f"  {total_jpg:>6}  TOTAL JPG")
    w("")
    w("=" * 70)
    w("PHOTOS ADDED (per page:  new file  <=  folder\\source  [caption]  {how})")
    w("=" * 70)
    if not pages_touched:
        w("  (none)")
    for slug in sorted(pages_touched):
        v = plan[slug]
        pg = v["page"]
        w(f"{pg['cat']}/{slug}  (+{len(v['adds'])})   title: {pg['title']}")
        for ph, newname, how in v["adds"]:
            w(f"    {newname:<28} <= {ph['folder']}\\{ph['file']}   [{ph['caption']}]  {{{how}}}")
    w("")
    w("=" * 70)
    w("NEAR-MISS RECOVERIES (caption was a variant; head-match -> page). Review these.")
    w("=" * 70)
    if not recovered:
        w("  (none)")
    for pg, a in sorted(recovered, key=lambda x: x[0]["slug"]):
        ph, newname, how = a
        w(f"  {pg['cat']}/{pg['slug']:<28} caption '{ph['venue']}'  ->  {newname}  {{{how}}}")
    w("")
    w("=" * 70)
    w('LEADING-"THE" FIX RECOVERIES (matched only after dropping a leading article)')
    w("=" * 70)
    if not the_adds:
        w("  (none)")
    for pg, a in sorted(the_adds, key=lambda x: x[0]["slug"]):
        ph, newname, how = a
        w(f"  {pg['cat']}/{pg['slug']:<28} caption '{ph['venue']}'  ->  {newname}  {{{how}}}")
    w("")
    w("=" * 70)
    w("SKIPPED - LOCKED pages (photos_locked:true, in the 3 categories)")
    w("=" * 70)
    if not locked_pages:
        w("  (none in cafes/restaurants/street-food; the 4 bars-pubs are out of scope)")
    for pg in locked_pages:
        w(f"  {pg['cat']}/{pg['slug']}")
    # captions that pointed at a locked page
    locked_hits = [(ph, tgt) for ph, tgt, why in near if why == "locked"]
    if locked_hits:
        w("  -- captioned photos that matched a LOCKED page (not imported):")
        for ph, tgt in sorted(locked_hits, key=lambda x: x[1]["slug"]):
            w(f"     {tgt['cat']}/{tgt['slug']:<28} <= {ph['folder']}\\{ph['file']}  [{ph['caption']}]")
    if held_back:
        w("")
        w("=" * 70)
        w("HELD BACK by operator (--exclude; NOT imported)")
        w("=" * 70)
        for pg, ph, how in sorted(held_back, key=lambda x: x[0]["slug"]):
            w(f"  {pg['cat']}/{pg['slug']:<28} <= {ph['folder']}\\{ph['file']}  [{ph['caption']}]  {{{how}}}")
    w("")
    w("=" * 70)
    w("UN-ATTRIBUTED - AMBIGUOUS (head matched >1 in-scope page; NOT imported)")
    w("=" * 70)
    amb = [(ph, tgts) for ph, tgts, why in near if why == "ambiguous"]
    if not amb:
        w("  (none)")
    for ph, tgts in sorted(amb, key=lambda x: x[0]["venue"]):
        slugs = ", ".join(sorted(t["slug"] for t in tgts))
        w(f"  '{ph['caption']}'  ->  {slugs}")
    w("")
    w("=" * 70)
    w("UN-ATTRIBUTED - NO MATCHING PAGE (no confident venue; NOT imported)")
    w("=" * 70)
    counts = defaultdict(int)
    for ph in nomatch:
        counts[ph["venue"]] += 1
    if not counts:
        w("  (none)")
    for venue in sorted(counts):
        w(f"  {counts[venue]:>3}  Chiang Mai - {venue}")

    report_text = "\n".join(L) + "\n"
    with open(REPORT, "w", encoding="utf-8", newline="\n") as f:
        f.write(report_text)

    # machine-readable plan
    with open(PLAN_CSV, "w", encoding="utf-8", newline="\n") as f:
        f.write('"Cat","Slug","Action","NewName","Folder","File","Caption","How"\n')
        for slug in sorted(plan):
            v = plan[slug]; pg = v["page"]
            for ph, newname, how in v["adds"]:
                f.write(f'"{pg["cat"]}","{slug}","import","{newname}","{ph["folder"]}",'
                        f'"{ph["file"]}","{ph["caption"]}","{how}"\n')
            for ph, reason, how in v["skips"]:
                f.write(f'"{pg["cat"]}","{slug}","skip:{reason}","","{ph["folder"]}",'
                        f'"{ph["file"]}","{ph["caption"]}","{how}"\n')

    print(report_text)
    print(f"\nReport: {REPORT}   Plan: {PLAN_CSV}")
    if not args.apply:
        print("DRY-RUN only - no files copied, no pages edited. Re-run with --apply to execute.")


if __name__ == "__main__":
    main()
