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
