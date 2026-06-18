import os, re, glob

ROOT = r"C:\Users\andre\Documents\andrestgt.github.io"
IMG_RE = re.compile(r'([A-Za-z0-9_\-]+\.(?:jpg|jpeg|png))', re.I)
STEM_RE = re.compile(r'^(.*?)(\d+)$')

def parse(basename):
    stem = os.path.splitext(basename)[0]
    m = STEM_RE.match(stem)
    if not m:
        return None
    return m.group(1), int(m.group(2)), len(m.group(2))

def runs(nums):
    """collapse sorted unique ints into contiguous runs -> list of (lo,hi)"""
    out = []
    for n in sorted(nums):
        if out and n == out[-1][1] + 1:
            out[-1][1] = n
        else:
            out.append([n, n])
    return [(a, b) for a, b in out]

def fmt_runs(rs):
    return ", ".join(f"{a:04d}" if a == b else f"{a:04d}-{b:04d}" for a, b in rs)

travelogues = sorted(glob.glob(os.path.join(ROOT, "travels", "*", "index.md")))
print(f"Scanning {len(travelogues)} travelogue index.md files\n")

flagged = []
for idx in travelogues:
    folder = os.path.dirname(idx)
    slug = os.path.basename(folder)
    # referenced basenames in index.md
    with open(idx, encoding="utf-8", errors="ignore") as fh:
        text = fh.read()
    ref_by_pref = {}
    for bn in IMG_RE.findall(text):
        p = parse(os.path.basename(bn))
        if not p: continue
        pref, num, _ = p
        ref_by_pref.setdefault(pref, set()).add(num)
    # disk basenames in folder (recursive), dedup by basename
    disk_by_pref = {}
    for dp, dn, fn in os.walk(folder):
        for f in fn:
            if not f.lower().endswith((".jpg", ".jpeg", ".png")): continue
            p = parse(f)
            if not p: continue
            pref, num, _ = p
            disk_by_pref.setdefault(pref, set()).add(num)

    # focus on the dominant photo prefix(es): those actually referenced
    for pref, refs in sorted(ref_by_pref.items()):
        disk = disk_by_pref.get(pref, set())
        if not refs or not disk:
            continue
        lo, hi = min(refs), max(refs)
        # on-disk-but-unreferenced numbers WITHIN the referenced range = candidate dropped block
        gap_nums = sorted(n for n in disk if lo < n < hi and n not in refs)
        # all unreferenced extras (any position)
        extras = sorted(n for n in disk if n not in refs)
        if not gap_nums:
            status = "ok"
        else:
            gr = runs(gap_nums)
            # contiguous if a single long run, or runs each length>=3
            biggest = max(b - a + 1 for a, b in gr)
            status = "GAP"
        # classify extras
        ex_runs = runs(extras) if extras else []
        ex_contig = [ (a,b) for a,b in ex_runs if b> a ]
        line = (f"  prefix '{pref}'  ref={len(refs)} ({lo:04d}-{hi:04d})  "
                f"disk={len(disk)}  unref_extras={len(extras)}")
        print(f"[{slug}]")
        print(line)
        if gap_nums:
            gr = runs(gap_nums)
            print(f"    >>> INTERNAL GAP in referenced sequence: missing-but-on-disk = {fmt_runs(gr)}  ({len(gap_nums)} files) <<<")
            flagged.append((slug, pref, fmt_runs(gr), len(gap_nums)))
        if extras:
            er = runs(extras)
            ncontig = sum(1 for a,b in er if b>a)
            kind = "scattered (genuine extras)" if ncontig == 0 else f"{ncontig} contiguous run(s) present"
            print(f"    unref extras outside/within range: {fmt_runs(er)}  -> {kind}")
        print()

print("="*70)
if flagged:
    print("TRAVELOGUES WITH d-gb FINGERPRINT (contiguous internal gap):")
    for slug, pref, gaps, n in flagged:
        print(f"  - {slug}  [{pref}]  gap {gaps}  ({n} files dropped from page)")
else:
    print("No travelogues with an internal contiguous gap in the referenced sequence.")
