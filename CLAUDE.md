# CLAUDE.md — andrestgt.github.io

Working rules for this Jekyll / GitHub Pages site. Follow exactly. When in doubt, **stop and ask** rather than guess. No hallucinated content, no silent omissions.

## Repo shape

- Venue review pages: `food/<country>/<city>/<category>/<venue-slug>/index.md`
  (with regional nesting where used, e.g. `food/vietnam/<region>/<city>/...`)
- Category landing pages: `food/<country>/<city>/<category>/index.md`
- City landing pages: `food/<country>/<city>/index.md`
- Categories (4): `restaurants` 🍽️ · `cafes` ☕ · `bars-pubs` 🍺 · `street-food` 🥢
- Photos live under `/photos/<country>/<city>/...`, referenced by absolute path from the page.
- **Never** use flat `<venue>.md` files — always `<venue>/index.md` folder structure (this was the Philippines 404 fix).

## Venue page template (locked-in)

Reference pages:
- `food/thailand/phuket-town/restaurants/one-chun-cafe-restaurant/index.md`
- `food/thailand/chiang-mai/street-food/guay-jub-chang-moi-tat-mai/index.md`

Structure, top to bottom:

```
---
layout: default
title: <Venue Name>
subtitle: <Neighbourhood> · <Cuisine> <Category>
section: food
review: true
---

<figure>
  <img src="/photos/<country>/<city>/<venue-slug>-1.jpg" alt="<Venue Name>">
  <figcaption><Venue Name></figcaption>
</figure>

<review body, multiple paragraphs>

## Ratings

| Category        | Score |
|-----------------|-------|
| Food            | 7.5/10 |
| Service         | 6.5/10 |
| Value for money | 7/10   |
| Atmosphere      | 8.5/10 |
| Overall         | 7.5/10 |

### Practical

🗺️ **Google Maps:** [Open in Google Maps](<maps-url>)

🍽️ **Type:** <type>

💰 **Price level:** <price>
```

Hard rules:
- Hero `<figure>` block **first**, immediately after the front matter, then straight into the review prose. Do **not** add a `## Venue Name` heading or an italic `Neighbourhood · Cuisine` subtitle line in the body — only ~12% of legacy pages have those and they are not the standard; the One Chun reference page is an outlier here. Photos are inline `<figure>` blocks in the body. **No** `hero:` / `image:` / `cover:` front matter on review pages, and no auto-selecting the first figure as a hero.
- **Max 10 photos** per page. Side-by-side pairing where used.
- `section:` is plain **`food`** — this is the de facto standard (212/213 Thailand venues). Do not write the full path into `section:` unless explicitly told to change the standard.
- Ratings table must include the **Overall** row. Scores in `N/10` format.
- Category-specific ratings: hotels use Service / Rooms / Location (not Food/Atmosphere). Match the row set to the venue type.
- Practical order: Google Maps (🗺️) → Type (🍽️/☕/🍺) → Price level (💰). The label is always **`Type:`** (standardised site-wide; do not use `Cuisine:`).
- Price level: numeric/currency for restaurants & street-food; word-form for cafés & bars. Never leave the label with a blank value.

## Slugs & file writing

- Slug: lowercase, hyphens, **ASCII only**.
- Always `write_bytes` with **LF** line endings (standing rule).
- Venue slug must be unique within its folder; append `-2`, `-3` on collision.

## Categorisation

- Category is derived from the **review text and what the place actually is**, never from the place name alone.

## Editorial voice (if writing/editing prose)

- Vivid, ironic, personal British English. Smooth, don't over-edit.
- No "the" before venue names unless officially part of the name; restructure pre-modifier constructions rather than dropping them awkwardly.
- Preserve capitalisation choices for dish names.

## Process discipline (every batch task)

1. **Show the full extracted/affected list BEFORE creating or changing any files.** Wait for confirmation.
2. Flag anything that can't be confidently placed (photo match, day, location) rather than guessing.
3. The DOCX source being correct does **not** mean the site renders it — verify the generated markdown and the relevant index/landing page actually include the entry (the Hải Phòng case).
4. Token waste from repeated mistakes is a real cost. Get it right the first time; don't churn.

## Confirmed paths (canonical)

- **Master reviews DOCX:** `C:\Users\andre\Downloads\Reviews-master.docx` — canonical new-venue source. Ignore `andre_reviews_FINAL_city_headings_REPAIRED.docx`.
- **Photo source root:** `D:\Google Photos` — never `C:`, OneDrive, or `Downloads\Google Photos` unless explicitly told otherwise. Verify the relevant `Food <year>` folder is in `TAKEOUT_DIRS` before matching.

---

# Travelogues (long-form trip write-ups) — playbook

How the Palawan 2025 travelogue was built. Follow exactly for new travelogues in the same style.

## File structure

- Travelogue lives at `travels/<slug>/index.md` (e.g. `travels/palawan-2025/`).
- Its photos live in that travelogue's **own** `photos/` subfolder, referenced by **relative** path `photos/SEA25-XXXX.jpg` (NOT the site-wide `/photos/...`).
- Add an entry to `travels/index.md` (newest first): `## Title (Year)` / subtitle with `&middot;` separators / `&rarr; [Read the full travelogue](https://andrestgt.github.io/travels/<slug>/)`.

## Front matter + top of page

```
---
layout: default
section: travels
title: "Palawan Revisited"
subtitle: "Puerto Princesa · Port Barton · San Vicente · El Nido"
date: 2025-03-15
photos_locked: true
---

# Palawan Revisited
**March 2025**

<intro paragraph>

![Hero Alt](photos/SEA25-XXXX.jpg)
*Hero caption*

---

## 15 March 2025
```

- Dated sections are `## DD Month YYYY`.
- City food landings can carry a `hero:` (see below); travelogues use the inline `![...]()` hero + `*caption*` shown above.

## Photo blocks (in-body)

Single:
```
<figure>
  <img src="photos/SEA25-XXXX.jpg" alt="Around El Nido - Nacpan Beach">
  <em>Around El Nido - Nacpan Beach</em>
</figure>
```
Pair (side by side):
```
<div class="photo-row">

  <figure>
    <img src="photos/SEA25-AAAA.jpg" alt="...">
    <em>...</em>
  </figure>

  <figure>
    <img src="photos/SEA25-BBBB.jpg" alt="...">
    <em>...</em>
  </figure>

</div>
```
- Caption style: `Place - Detail` (e.g. `Around San Vicente - Amwani Sunset Colours`, `Bacuit Archipelago`).
- Travelogue captions use `<em>`; food-page captions use `<figcaption>`. Don't mix them.

## Which photos go where

- **Restaurant / café / bar / street-food (any food-venue) photos do NOT go in the travelogue** — they belong in the food section. Beaches, viewpoints, landscapes, accommodation, the bike, boat trips, town scenes → travelogue.
- Source of truth for what a photo is: the EXIF **ImageDescription (tag 270)** = "City - Venue". Fix mojibake with `s.encode('latin-1').decode('utf-8')`. Datetime = tag 306 or 36867 — use it to place photos in the right dated section.

## Photo processing (identical for travelogue, food, and hero images)

- Resize to **1700px long edge** max, JPEG **quality 82**, `progressive=True`, `optimize=True`, and always `ImageOps.exif_transpose(im)` first.
- Hero images for city food landings: `photos/background/<name>hero.jpg` (same 1700px/q82), referenced via `hero: /photos/background/<name>hero.jpg` in the landing's front matter.

## Voice & prose rules (learned from many corrections)

- Plural **"we"** — these are couple trips.
- **No dashes** as sentence punctuation (no em/en dashes). Use commas, semicolons, colons only. Hyphenated compound words (e.g. `Vietnamese-Filipino`, `banh-mi-style`) are fine.
- **Always name prices** where possible (per night, per day, per meal, entrance fees).
- **No AI-slop phrasing.** ("A reliable spot for a proper coffee in town" was explicitly rejected.)
- Match vocabulary/tone of the user's existing travelogues (e.g. `travels/eastern-indonesia-2026/`, `travels/palawan-borneo-2009/`).
- **Check for redundancies** before repeating a description across days.
- **Only edit what was asked.** Do not "improve" untouched paragraphs.
- When the user later hyperlinks venues: link the **first** mention of each venue only; leave repeat mentions and non-venue names (e.g. "Star Apple") plain.

## Food pages (when adding the trip's venues)

Follow the existing `## Venue page template` above in this file. Extra notes confirmed on Palawan:

- **Price level differs by category** (this is a hard rule):
  - restaurants & street-food → **peso range** for two people, average meal, no alcohol (e.g. `₱200–350`).
  - cafés & bars → **word-form** descriptor (`inexpensive` / `moderate` / `expensive`).
- Ratings row set by type: restaurants/street-food = Food/Service/Value/Atmosphere/Overall; cafés = Coffee/...; bars = Service/Value/Atmosphere/Overall (add a Beer row for breweries).
- Category emoji in Type line: 🍽️ restaurants · ☕ cafés · 🍺 bars-pubs · 🥢 street-food.
- Each category `index.md` **manually** lists its venues — add an entry (`## Name` / `*subtitle*` / one-liner / `→ [Read the full review](...)`) when creating a page; remove it when moving a page.
- Google Maps link: reuse the real place-ID `data=!4m2!3m1!...` URL from the user's Google Takeout reviews JSON when the venue is in it; otherwise use a `https://www.google.com/maps/search/?api=1&query=<venue+city>` search URL and say so.
- A town can be its own city landing (we split **Taytay** into `food/philippines/taytay/` with its own hero) or fold into a neighbour — confirm which.

## docx → markdown sync workflow

When the user sends an updated `.docx` of the text:
1. `pandoc file.docx -t plain -o new.txt`.
2. Strip figures/front matter from the current `index.md`, unwrap hard-wrapped paragraphs on both sides, and `diff` to find the real prose changes.
3. Apply each change with targeted edits. **Flag likely typos** (we found "started at.", "1000 pesos .", "I the late afternoon") and apply-as-written unless told to fix.
4. Keep the photo blocks in place; only the prose changes.

## Device-bridge operational rules (IMPORTANT — these caused real damage once)

- **Write whole files atomically.** Build the full file in the cloud → `SendUserFile` → `device_commit_files`. Do **NOT** do read-modify-write on the mounted repo via `device_bash` python for content files: on a flaky mount a partial read gets written back and **truncates the file** (this corrupted 5 food pages once).
- The Linux mount (`device_bash`) can return **stale or partial reads** right after a write. The authoritative check is **`device_list_dir`** (device-side metadata) — compare its reported byte size to the cloud file's size to confirm a commit landed.
- **Deletion is blocked** on the mount (`rm`/`unlink` → Operation not permitted). **Rename/move works** (`os.rename`, `mv`) — move unwanted files into a `_to_delete/` folder, or have the user `git rm` them in Git Bash. `git`-tracked deletions are cleanest via `git rm` / `git add -A`.
- Empty directories don't persist on the mount — create the dir and write a file in the same step.
- **Recursive grep across the whole repo times out** (~45s). Target specific files/paths instead.
- Build-script pattern (only for structural/bulk ops, never for hand-editing prose): write script in cloud → commit as `_build_*.py` (underscore prefix = Jekyll ignores it) → run via `device_bash` → then move the script to `_to_delete/`.

## Git (user runs Git Bash)

```
git add -A
git commit -m "..."
git push origin main
```
If push is rejected: `git pull --rebase origin main`, resolve any conflict (in a rebase, `--theirs` = your local replayed commit, `--ours` = remote), `git add <file>`, `git rebase --continue`, push. CRLF warnings are harmless.
