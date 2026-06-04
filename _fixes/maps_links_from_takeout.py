"""
maps_links_from_takeout.py - replace each venue page's generic Google Maps
search URL with the precise, canonical place URL taken from your Google Maps
Takeout reviews export.

Matching is by normalised venue name + city (from the page path). Anything that
doesn't match confidently is FLAGGED and left untouched - no link is invented.

--takeout accepts one or more paths; each may be a file, a directory (its
*.json are used), or a glob. All exports are parsed and merged as a UNION of
places, so a review edited or deleted since an older export still survives if it
appears in any file. Duplicates are collapsed per place (CID -> canonical URL ->
normalised name+address); when a place appears in several exports the most recent
one wins (recency inferred from the filename, e.g. may26 > jan26 > dec25 > nov24).

Usage (from repo root):
    python _fixes/maps_links_from_takeout.py --takeout "/g/My Drive/travel/Reviews may26.json" "...jan26.json"
    python _fixes/maps_links_from_takeout.py --takeout "/g/My Drive/travel"        # whole folder
    python _fixes/maps_links_from_takeout.py --takeout "/g/My Drive/travel" --apply

Run the dry-run FIRST. It prints how many review entries it parsed and a sample
one. If it parsed 0, or the sample's name/url look wrong, paste a raw entry from
the JSON and the field mapping can be corrected.
"""
from __future__ import annotations

import argparse, difflib, glob, json, os, re, unicodedata

# words that add no identity; stripped during normalisation
STOP = {"the","restaurant","restaurante","ristorante","cafe","café","caffe","coffee",
        "bar","pub","gasthof","gasthaus","wirtshaus","quan","quán","nha","nhà","hang",
        "hàng","restoran","kedai","warung","street","food","shop"}


# chars NFKD does NOT decompose - map them explicitly before normalising
_PREMAP = {"đ": "d", "Đ": "d", "ø": "o", "Ø": "o", "ł": "l", "Ł": "l", "ß": "ss", "ẞ": "ss"}


def deaccent(s):
    s = s or ""
    for k, v in _PREMAP.items():
        if k in s: s = s.replace(k, v)
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


# Branch/city suffix on a venue name: everything from the first  –  —  @  or  (  onward.
# Plain hyphen '-' is intentionally NOT a separator (would break hyphenated names).
SUFFIX_RE = re.compile(r"\s*[–—@(].*$")


def head_of(name):
    """Name with any trailing branch/city suffix removed."""
    return SUFFIX_RE.sub("", name or "").strip()


def suffix_of(name):
    """The stripped branch/city suffix text (without the leading separator), or ''."""
    m = re.search(r"[–—@(]\s*(.*)$", name or "")
    return m.group(1).strip(" )") if m else ""


def strip_head(name):
    """Aggressive, symmetric head used for matching BOTH page titles and review names:
    drop everything after '|' or a –/—/@/( separator, drop trailing .com / GmbH / Branch,
    then drop trailing bare append tokens (pure digits or 1-2 letters, e.g. '4', 'Cm', 'Ph')."""
    h = (name or "").split("|", 1)[0]
    h = SUFFIX_RE.sub("", h)
    h = re.sub(r"\.com\b.*$", "", h, flags=re.I)
    h = re.sub(r"\s+(?:gmbh|branch)\b.*$", "", h, flags=re.I)
    while True:
        h2 = re.sub(r"\s+(?:\d+|[A-Za-z]{1,2})$", "", h)
        if h2 == h: break
        h = h2
    return h.strip()


CATS = ("restaurants", "street-food", "cafes", "bars-pubs")


def page_city(parts):
    """City = the path segment immediately before the category (reliable even for
    region-nested paths like vietnam/binh-dinh/quy-nhon/street-food/...)."""
    for i, seg in enumerate(parts):
        if seg in CATS and i > 0:
            return parts[i-1].replace("-", " ")
    return ""


def city_agrees(city, cand):
    """True if the page city appears in the candidate review's address (deaccented)."""
    if not city: return False
    return deaccent(city).lower() in deaccent(cand.get("addr", "")).lower()


# Manually confirmed band (0.80-0.85) recoveries: same place beyond doubt (trailing
# suffix or typo). Accepted even when the address omits the city word, because the
# name is distinctive. Each links the top same-country fuzzy candidate.
FORCE_BAND = {
    "philippines/davao/restaurants/bahay-cubo/index.md",
    "vietnam/ho-chi-minh-city/restaurants/san-fu-lou-restaurant-hot-pot-ab-tower/index.md",
    "philippines/bohol-panglao/cafes/brewpoint-coffee-club/index.md",
    "philippines/bohol-panglao/restaurants/bougainvillea/index.md",
    "laos/luang-prabang/cafes/le-cafe-ban-vat-sene/index.md",
    "cambodia/kampot-kep/cafes/saravoan-kep/index.md",
    "cambodia/kampot-kep/restaurants/rikitikitavi/index.md",
    "philippines/bohol-panglao/cafes/nikitas-coffee-shop/index.md",
    "thailand/chiang-mai/street-food/tacos-bell/index.md",
}


# site country slug -> ISO 3166-1 alpha-2 (matches Takeout location.country_code)
COUNTRY_CC = {"austria": "AT", "cambodia": "KH", "czechia": "CZ", "france": "FR",
              "germany": "DE", "greece": "GR", "hungary": "HU", "india": "IN",
              "indonesia": "ID", "laos": "LA", "malaysia": "MY", "philippines": "PH",
              "poland": "PL", "portugal": "PT", "slovakia": "SK", "spain": "ES",
              "taiwan": "TW", "thailand": "TH", "vietnam": "VN"}

# fallback only (when a review has no country_code): English + local country names
COUNTRY_ALIASES = {"germany": ["germany", "deutschland"], "vietnam": ["vietnam", "viet nam"],
                   "czechia": ["czechia", "czech", "cesko", "ceska"], "austria": ["austria", "osterreich"],
                   "greece": ["greece", "hellas", "ellada"], "spain": ["spain", "espana"],
                   "poland": ["poland", "polska"], "slovakia": ["slovakia", "slovensko"]}


def country_ok(slug, cand):
    """True if the candidate review is in the page's country. Prefers ISO country_code;
    falls back to country-name (incl. local aliases) in the address."""
    exp = COUNTRY_CC.get(slug)
    if exp and cand.get("cc"):
        return cand["cc"] == exp
    addr = deaccent(cand.get("addr", "")).lower()
    for n in COUNTRY_ALIASES.get(slug, [slug.replace("-", " ")]):
        if deaccent(n).lower() in addr: return True
    return False


def norm(s):
    s = deaccent(s or "").lower()
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    toks = [t for t in s.split() if t and t not in STOP]
    return " ".join(toks)


def dig(d, *keys):
    """try several dotted key paths, return first hit"""
    for path in keys:
        cur = d; ok = True
        for k in path.split("."):
            if isinstance(cur, dict) and k in cur: cur = cur[k]
            else: ok = False; break
        if ok and isinstance(cur, str) and cur.strip(): return cur
    return None


def parse_takeout(path):
    data = json.load(open(path, encoding="utf-8"))
    feats = data.get("features", data) if isinstance(data, dict) else data
    out = []
    for f in feats:
        props = f.get("properties", f) if isinstance(f, dict) else {}
        name = dig(props, "location.name", "Location.Name", "name", "title")
        url  = dig(props, "google_maps_url", "Google Maps URL", "googleMapsUrl", "url")
        addr = dig(props, "location.address", "Location.Address", "address", "formatted_address") or ""
        cc   = dig(props, "location.country_code", "country_code", "Country Code")
        # CID fallback -> build canonical url
        if not url:
            cid = dig(props, "location.cid", "cid", "CID")
            if cid: url = f"https://maps.google.com/?cid={cid}"
        if name and url:
            out.append({"name": name, "url": url, "addr": addr, "cc": cc,
                        "nname": norm(name), "mhead": norm(strip_head(name))})
    return out


def expand_takeout_paths(specs):
    """Turn each spec (file / directory / glob) into a flat, de-duplicated file list."""
    files = []
    for s in specs:
        if os.path.isdir(s):
            files += sorted(glob.glob(os.path.join(s, "*.json")))
        elif any(ch in s for ch in "*?["):
            files += sorted(glob.glob(s))
        else:
            files.append(s)
    seen = set(); out = []
    for f in files:
        if f not in seen and os.path.isfile(f):
            seen.add(f); out.append(f)
    return out


_MONTHS = {m: i for i, m in enumerate(
    ["jan","feb","mar","apr","may","jun","jul","aug","sep","oct","nov","dec"], 1)}


def recency_key(path):
    """Sortable recency from a filename like 'Reviews may26.json' (year*100+month). -1 if unknown."""
    m = re.search(r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\s*'?(\d{2})",
                  os.path.basename(path).lower())
    return int(m.group(2)) * 100 + _MONTHS[m.group(1)] if m else -1


def cid_from_url(url):
    """Extract a stable place id (CID) from a Maps URL, if present."""
    m = re.search(r"[?&]cid=(\d+)", url or "")
    if m: return m.group(1)
    m = re.search(r"!1s0x[0-9a-fA-F]+:0x([0-9a-fA-F]+)", url or "")
    if m:
        try: return str(int(m.group(1), 16))
        except ValueError: return None
    return None


def place_key(e):
    """Dedup key for a place: CID, else canonical URL, else normalised name+address."""
    cid = cid_from_url(e["url"])
    if cid: return ("cid", cid)
    if e["url"]: return ("url", e["url"])
    return ("na", e["nname"] + "|" + norm(e["addr"]))


def load_merged(specs):
    """Parse every export and merge as a union of places; most recent export wins on conflicts.
    Returns (reviews_list, per_file_counts, ordered_files, total_parsed)."""
    files = sorted(expand_takeout_paths(specs), key=recency_key)  # oldest first -> newest overwrites
    merged = {}; per_file = []; total = 0
    for f in files:
        ents = parse_takeout(f)
        per_file.append((os.path.basename(f), len(ents))); total += len(ents)
        for e in ents:
            merged[place_key(e)] = e   # later (more recent) file wins
    return list(merged.values()), per_file, files, total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--takeout", required=True, nargs="+",
                    help="one or more files, directories, or globs")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    reviews, per_file, files, total = load_merged(args.takeout)
    print(f"Parsed {len(files)} export file(s) (oldest -> newest):")
    for name, n in per_file:
        print(f"  {name}: {n} entries")
    print(f"Total entries parsed: {total}   ->   {len(reviews)} unique places after dedup.")
    if reviews:
        s = reviews[0]
        print(f"  sample: name='{s['name']}'  url='{s['url'][:60]}...'  addr='{s['addr'][:40]}'\n")
    if not reviews:
        print("  Parsed 0 - field names differ. Paste one raw JSON entry to fix the mapping.")
        return

    # index by normalised full name, by aggressive symmetric match-head, and by country
    idx = {}; idx_head = {}; by_cc = {}
    for r in reviews:
        idx.setdefault(r["nname"], []).append(r)
        if r["mhead"]:
            idx_head.setdefault(r["mhead"], []).append(r)
        by_cc.setdefault(r.get("cc"), []).append(r)

    maps_re = re.compile(r"^(🗺️ \*\*Google Maps:\*\* \[Open in Google Maps\]\()([^)]*)(\))", re.M)
    matched = recovered = flagged = already = 0
    no_match = ambig = cmis = 0   # flag breakdown
    f_nomatch, f_ambig, f_cmis = [], [], []   # (path, title) per flagged venue
    rec_list = []    # (path, title, review, score, city) recovered via fuzzy
    band_list = []   # (path, title, review, score, city_ok) 0.80-0.85, manual
    for p in glob.glob(f"{args.root}/food/**/index.md", recursive=True):
        parts = re.split(r"[\\/]", p)  # tolerate Windows '\' separators
        if not any(c in parts for c in CATS): continue
        t = open(p, encoding="utf-8").read()
        fm = re.match(r"^---\n(.*?)\n---", t, re.S)
        if not (fm and re.search(r"^review:\s*true", fm.group(1), re.M)): continue
        title = re.search(r"^title:\s*(.+)$", fm.group(1), re.M)
        if not title: continue
        fi = parts.index("food")
        country_slug = parts[fi+1]
        city = page_city(parts)              # segment before the category (reliable)
        title_raw = title.group(1)
        short = "/".join(parts[fi+1:])       # slug-proof (slugs can contain 'food')

        # Pass 1: exact normalised-name. Pass 2: exact match-head (symmetric stripping).
        cands = idx.get(norm(title_raw), [])
        used_head = False
        if not cands:
            nhead = norm(strip_head(title_raw))
            if nhead:
                cands = list(idx_head.get(nhead, []))
                used_head = True

        # Disambiguate multiple candidates: first by the city in the address; for a
        # head match, fall back to the stripped suffix (branch/city) tokens.
        if len(cands) > 1:
            cby = [c for c in cands if city and city in deaccent(c["addr"]).lower()]
            if not cby and used_head:
                suf = deaccent(suffix_of(title_raw)).lower()
                toks = [tok for tok in re.split(r"[^a-z0-9]+", suf) if len(tok) > 2]
                cby = [c for c in cands if any(tok in deaccent(c["addr"]).lower() for tok in toks)]
            cands = cby or cands

        chosen = None
        if len(cands) == 1:
            # country guard: ISO country_code (address-name fallback). Rejects
            # cross-region collisions (Langkawi 'Sun Cafe' vs Nha Trang 'Sun Coffee Bar').
            if country_ok(country_slug, cands[0]):
                chosen = cands[0]
            else:
                flagged += 1; cmis += 1; f_cmis.append((short, title_raw)); continue
        elif len(cands) >= 2:
            flagged += 1; ambig += 1; f_ambig.append((short, title_raw)); continue
        else:
            # Pass 3: fuzzy recovery among SAME-COUNTRY reviews. Accept only if
            # fuzzy(head) >= 0.85 AND the page city appears in the review address.
            # The city test is mandatory - it rejects same-name places in other cities.
            ph = norm(strip_head(title_raw))
            scored = sorted(((difflib.SequenceMatcher(None, ph, r["mhead"]).ratio(), r)
                             for r in by_cc.get(COUNTRY_CC.get(country_slug), [])), key=lambda x: -x[0])
            picked = next(((sc, r) for sc, r in scored if sc >= 0.85 and city_agrees(city, r)), None)
            if picked:
                sc, r = picked
                chosen = r; recovered += 1
                rec_list.append((short, title_raw, r["name"], sc, city))
            elif short in FORCE_BAND and scored:
                sc, r = scored[0]   # manually confirmed: accept top same-country candidate
                chosen = r; recovered += 1
                rec_list.append((short, title_raw, r["name"], sc, (city or "?") + " [manual]"))
            else:
                if scored and 0.80 <= scored[0][0] < 0.85:
                    sc, r = scored[0]
                    band_list.append((short, title_raw, r["name"], sc, city_agrees(city, r)))
                flagged += 1; no_match += 1; f_nomatch.append((short, title_raw)); continue

        url = chosen["url"]
        m = maps_re.search(t)
        if m and m.group(2) == url:
            already += 1; continue
        if m:
            t2 = t[:m.start()] + m.group(1) + url + m.group(3) + t[m.end():]
            matched += 1
            if args.apply:
                open(p, "w", encoding="utf-8", newline="").write(t2)

    print(f"{'APPLIED' if args.apply else 'DRY-RUN'}: {matched} links updated "
          f"({recovered} via fuzzy recovery), {already} already precise, {flagged} flagged "
          f"({no_match} no-match, {ambig} ambiguous, {cmis} country-mismatch).\n")

    # Complete flagged list, split into sections, each sorted by path: "path -> title".
    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "maps_flagged.txt")
    sections = [("NO MATCH", f_nomatch), ("AMBIGUOUS", f_ambig), ("COUNTRY-MISMATCH", f_cmis)]
    with open(out_path, "w", encoding="utf-8", newline="\n") as fo:
        for label, items in sections:
            head = f"{label} ({len(items)})"
            fo.write(head + "\n" + "=" * len(head) + "\n")
            for short, title in sorted(items):
                fo.write(f"  {short} → {title}\n")
            fo.write("\n")
    print(f"Full flagged list written to {out_path}")

    # Recovered (fuzzy >= 0.85 + city agreement) and the 0.80-0.85 manual band.
    nm_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "maps_nearmiss.txt")
    with open(nm_path, "w", encoding="utf-8", newline="\n") as fo:
        fo.write(f"RECOVERED ({len(rec_list)}) - fuzzy head >= 0.85 AND page city in review "
                 f"address AND country_code match. These WILL be linked on --apply.\n")
        fo.write("=" * 70 + "\n")
        for short, title, rev, sc, city in sorted(rec_list):
            fo.write(f"  {short}\n      page: {title}  →  review: {rev}  ({sc:.2f}, city: {city})\n")
        fo.write(f"\nBAND 0.80-0.85 ({len(band_list)}) - NOT applied, manual review.\n")
        fo.write("=" * 70 + "\n")
        for sc, short, title, rev, city_ok in sorted(((b[3], b[0], b[1], b[2], b[4]) for b in band_list),
                                                      key=lambda x: -x[0]):
            fo.write(f"  {sc:.2f}  {short}\n      page: {title}  →  review: {rev}  "
                     f"(city agrees: {city_ok})\n")
    print(f"Recovered + band written to {nm_path}")


if __name__ == "__main__":
    main()
