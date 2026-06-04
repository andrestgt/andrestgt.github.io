"""
normalize_all_prices.py - normalise the FORMAT of populated price levels on
restaurant/street-food pages, all countries. Pure-ASCII source (all special
characters are unicode escapes) so it survives any download/encoding on Windows.

Fixes: hyphen/em-dash ranges -> en-dash, leading junk, Bt/THB->baht, CZK->Kc,
double symbols, currency to prefix, canonical spacing (glyph glued, letter-code
one space). Surgical: numbers (commas, 'k') kept verbatim; trailing ' . Lunch'
qualifier preserved. Stray tier-words, prose, and ambiguous typos are FLAGGED,
not changed.

    python _fixes/normalize_all_prices.py            # dry-run
    python _fixes/normalize_all_prices.py --apply
"""
from __future__ import annotations
import argparse, glob, re

EN   = "\u2013"   # en-dash
EM   = "\u2014"   # em-dash
BAHT = "\u0e3f"; EUR = "\u20ac"; DONG = "\u20ab"; KIP = "\u20ad"; PESO = "\u20b1"
SS   = "\u00df"   # ss
ACUT = "\u00b4"   # acute
KC   = "K\u010d"; ZL = "z\u0142"; MIDDOT = "\u00b7"
MONEY = "\U0001f4b0"

# (token in source, canonical symbol, spacing). Order matters: NT$/codes before $/glyphs.
CURR = [("NT$","NT$","sp"),("THB",BAHT,"glue"),("Bt",BAHT,"glue"),("CZK",KC,"sp"),
        ("RM","RM","sp"),("Rs","Rs","sp"),("Rp","Rp","sp"),("Ft","Ft","sp"),
        (KC,KC,"sp"),(ZL,ZL,"sp"),(BAHT,BAHT,"glue"),(EUR,EUR,"glue"),
        (DONG,DONG,"glue"),(KIP,KIP,"glue"),(PESO,PESO,"glue"),("$","$","glue")]

def normalize(raw):
    v = raw.strip()
    v = re.sub(r"^.*\*\*Price level:\*\*[ \t]*", "", v)          # un-double a duplicated label
    qual = ""
    if (" " + MIDDOT + " ") in v:
        v, q = v.split(" " + MIDDOT + " ", 1); qual = " " + MIDDOT + " " + q.strip()
    v = v.lstrip(EM + EN + ". ").strip()                         # strip leading em/en-dash, dots
    if re.fullmatch(r"(?i)(inexpensive|moderate|expensive)", v): return None, "stray-tier-word"
    if re.search(r"(?i)\b(under|around|approx|about|from|for two|per)\b", v): return None, "prose"
    sym = spacing = None; rest = v
    for tok, canon, sp in CURR:
        if tok in v:
            sym, spacing, rest = canon, sp, v.replace(tok, "")    # remove ALL occurrences (double-glyph)
            break
    if sym is None: return None, "no-currency"
    rest = rest.strip()
    rest = re.sub(r"(?<=\d)\s*[" + ACUT + SS + r"]\s*(?=\d)", EN, rest)   # ss/acute between digits
    if SS in rest or ACUT in rest: return None, "ambiguous-typo"
    rest = re.sub(r"\s*[-" + EM + r"]\s*", EN, rest)              # hyphen/em-dash -> en-dash
    rest = re.sub(r"\s+", " ", rest).strip()
    if not re.search(r"\d", rest): return None, "no-number"
    out = (sym + rest) if spacing == "glue" else (sym + " " + rest)
    return out + qual, "ok"

LINE = re.compile(r"^.*?\*\*Price level:\*\*[ \t]*(.*)$", re.MULTILINE)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="."); ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    scanned = changed = 0; flags = {}
    for p in glob.glob(f"{args.root}/food/**/index.md", recursive=True):
        parts = re.split(r"[\\/]", p)                             # cross-platform path split
        if not any(c in parts for c in ("restaurants","street-food")): continue
        t = open(p, encoding="utf-8").read()
        fm = re.match(r"^---\n(.*?)\n---", t, re.S)
        if not (fm and re.search(r"^review:\s*true", fm.group(1), re.M)): continue
        m = LINE.search(t)
        if not m: continue
        scanned += 1
        raw = m.group(1)
        new, status = normalize(raw)
        short = p.split("food")[-1]
        if status != "ok":
            flags.setdefault(status, []).append(f"[{raw.strip()[:32]}] {short}")
            continue
        newline = f"{MONEY} **Price level:** {new}"
        if m.group(0) != newline:
            changed += 1
            print(f"FIX  [{raw.strip()}] -> [{new}] {short}")
            if args.apply:
                open(p, "w", encoding="utf-8", newline="").write(t[:m.start()] + newline + t[m.end():])
    print(f"\nScanned {scanned} priced resto/street pages.")
    print(f"{'APPLIED' if args.apply else 'DRY-RUN'}: {changed} reformatted.")
    for k, v in flags.items():
        print(f"FLAGGED {k}: {len(v)}")
        for line in v[:6]: print("   ", line)

if __name__ == "__main__":
    main()
