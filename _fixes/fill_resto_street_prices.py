"""
fill_resto_street_prices.py  (v2 - rebuilt against current repo)

Fills the 45 restaurant/street-food pages that are STILL empty or hold a stray
tier-word, as of repo HEAD 01f7cd4 (2026-06-04). Supersedes v1, which had two
faults: street-food paths were mangled to 'street-...', and it still listed
Vietnamese pages that have since been filled.

Values use the 2-pax + non-alcoholic-drinks basis (a meal for two) and are
calibrated against each country's existing populated bands.

Run from repo root:
    python _fixes/fill_resto_street_prices.py            # dry-run
    python _fixes/fill_resto_street_prices.py --apply     # write
"""
from __future__ import annotations

import argparse, re
from pathlib import Path

E="€"; DASH="–"; DONG="₫"; KIP="₭"; PESO="₱"; KC="Kč"

FILLS = {
    # Czechia
    f"czechia/bohemia/nove-mesto-metuje/restaurants/zamek-bar": f"{KC} 400{DASH}600",  # kept page's existing value
    # Germany (2-pax basis; aligned to existing €10-40 bands)
    "germany/baden-wuerttemberg/karlsruhe/restaurants/erste-fracht-braugasthaus": f"{E}25{DASH}35",
    "germany/baden-wuerttemberg/leutkirch/restaurants/brauerei-gasthof-mohren": f"{E}20{DASH}30",
    "germany/baden-wuerttemberg/schwarzwald/restaurants/alte-traenke": f"{E}20{DASH}30",
    "germany/baden-wuerttemberg/schwarzwald/restaurants/klosterscheuer": f"{E}25{DASH}35",
    "germany/baden-wuerttemberg/stuttgart/restaurants/besenwirtschaft-rauscher": f"{E}15{DASH}25",
    "germany/baden-wuerttemberg/stuttgart/restaurants/biergarten-killesberg": f"{E}20{DASH}30",
    "germany/baden-wuerttemberg/stuttgart/restaurants/brauhaus-schoenbuch": f"{E}25{DASH}35",
    "germany/baden-wuerttemberg/stuttgart/restaurants/harmonie-griechisches-restaurant": f"{E}15{DASH}25",
    "germany/baden-wuerttemberg/stuttgart/restaurants/ristorante-la-scala": f"{E}50{DASH}80",
    "germany/baden-wuerttemberg/stuttgart/restaurants/trattoria-vivaldi": f"{E}15{DASH}25",
    "germany/baden-wuerttemberg/tuebingen/restaurants/neckarmueller-biergarten": f"{E}20{DASH}30",
    "germany/bayern/bamberg/restaurants/schlenkerla-rauchbierbrauerei": f"{E}20{DASH}30",
    "germany/bayern/dinkelsbuehl/restaurants/zur-glocke": f"{E}20{DASH}30",
    "germany/bayern/muenchen/restaurants/augustiner-stammhaus": f"{E}20{DASH}30",
    "germany/bayern/muenchen/restaurants/biergarten-am-chinesischen-turm": f"{E}20{DASH}30",
    "germany/bayern/nuernberg/restaurants/goldenes-posthorn": f"{E}20{DASH}30",
    "germany/bayern/nuernberg/restaurants/wirtshaus-huettn": f"{E}25{DASH}35",
    "germany/bayern/regensburg/restaurants/spitalgarten": f"{E}20{DASH}30",
    "germany/berlin/berlin/restaurants/dicke-wirtin": f"{E}25{DASH}35",
    "germany/berlin/berlin/restaurants/konnopkes-imbiss": f"{E}10{DASH}20",
    "germany/berlin/berlin/restaurants/song-nguu-wasserbueffel": f"{E}15{DASH}25",
    "germany/hessen/frankfurt/restaurants/apfelwein-wirtschaft-fichtekraenzi": f"{E}20{DASH}30",
    "germany/nrw/koeln/restaurants/frueh-em-golde-kappes": f"{E}20{DASH}30",
    "germany/rheinland-pfalz/weinstrasse/restaurants/alter-kastanienhof": f"{E}20{DASH}30",
    "germany/rheinland-pfalz/weinstrasse/restaurants/gaststaette-muehlengrund": f"{E}25{DASH}35",
    "germany/rheinland-pfalz/weinstrasse/restaurants/naturfreundehaus-edenkoben": f"{E}15{DASH}25",
    "germany/saarland/kirkel/restaurants/ressmanns-residence": f"{E}30{DASH}40",
    "germany/sachsen/dresden/restaurants/codo": f"{E}15{DASH}25",
    # India (2-pax)
    "india/kolkata/restaurants/afraa-lounge": f"Rs 500{DASH}800",
    "india/north-goa/restaurants/bees-knees-cafe": f"Rs 400{DASH}600",
    "india/north-goa/restaurants/comida-caseira": f"Rs 700{DASH}1000",
    "india/south-goa/restaurants/boom-shankar-resort": f"Rs 400{DASH}600",
    "india/south-goa/restaurants/holiday-inn-cafe": f"Rs 300{DASH}500",
    # Laos
    "laos/luang-prabang/restaurants/lao-lao-garden": f"{KIP}60k{DASH}80k",  # kept page's existing value
    "laos/luang-prabang/street-food/local-noodle-shop": f"{KIP}50k{DASH}90k",
    # Malaysia (first was stray 'expensive'; a grocer/oyster bar - loose)
    "malaysia/kuala-lumpur/restaurants/bens-independent-grocer": f"RM 60{DASH}120",
    "malaysia/kuching/street-food/chong-choon-cafe": f"RM 20{DASH}40",
    "malaysia/kuching/street-food/kapit-cafe": f"RM 20{DASH}40",
    # Philippines (first was stray 'moderate')
    "philippines/manila/restaurants/brothers-burger-bgc": f"{PESO}600{DASH}900",
    "philippines/manila/restaurants/lentrecote-bgc": f"{PESO}1500{DASH}2500",
    # Vietnam (only the 4 still empty)
    "vietnam/nha-trang/restaurants/la-villa-boutique-hotel": f"{DONG}300k{DASH}500k",
    "vietnam/nha-trang/street-food/cay-xoai-quan": f"{DONG}200{DASH}300k",  # kept page's existing value
    "vietnam/nha-trang/street-food/cuon-papas": f"{DONG}200k",              # kept page's existing value
    "vietnam/nha-trang/street-food/quan-an-xo": f"{DONG}200{DASH}300k",     # kept page's existing value
}

PRICE_RE = re.compile(r"^.*?\*\*Price level:\*\*[ \t]*.*$", re.MULTILINE)
TYPE_RE = re.compile(r"^.*\*\*(?:Cuisine|Type):\*\*.*$", re.MULTILINE)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="."); ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    filled = inserted = problems = 0
    for rel, val in FILLS.items():
        p = Path(args.root) / "food" / f"{rel}/index.md"
        if not p.exists():
            problems += 1; print(f"MISSING FILE  {rel}"); continue
        t = p.read_text(encoding="utf-8")
        new_line = f"\U0001f4b0 **Price level:** {val}"
        if PRICE_RE.search(t):
            t2 = PRICE_RE.sub(lambda m: new_line, t, count=1); filled += 1
            print(f"FILL    {rel}  ->  {val}")
        else:
            # No canonical '**Price level:**' line. If a malformed/loose price
            # line exists (missing closing '**', stray '💰' line, etc.), do NOT
            # insert a duplicate - flag it loudly for manual fixing.
            if re.search(r"💰|Price level:", t):
                problems += 1; print(f"MALFORMED PRICE  {rel} (fix manually)"); continue
            m = TYPE_RE.search(t)
            if not m: problems += 1; print(f"NO ANCHOR  {rel}"); continue
            t2 = t[:m.end()] + "\n" + new_line + t[m.end():]; inserted += 1
            print(f"INSERT  {rel}  ->  {val}")
        if args.apply: p.write_text(t2, encoding="utf-8", newline="")
    print(f"\n{'APPLIED' if args.apply else 'DRY-RUN'}: {filled} filled, "
          f"{inserted} inserted, {problems} problems, {len(FILLS)} total.")


if __name__ == "__main__":
    main()
