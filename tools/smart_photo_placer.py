#!/usr/bin/env python3
"""
Universal photo placer for travelogues with automatic section detection.
Rules:
- Specific place name -> after paragraph containing that name.
- City name -> after the section that describes that city.
- Sections are split by transition phrases or city name changes.
- Max 2 images per row.
"""

import re
import argparse
from collections import defaultdict
import sys

# ------------------------------------------------------------
# CONFIGURATION – adjust these lists for each travelogue
# ------------------------------------------------------------
SPECIFIC_PLACES = [
    "River View", "Strand Bar", "Café Brolly", "Candacraig",
    "Shwedagon Pagoda", "Sule Pagoda", "Bogyoke Market",
    "U Bein Bridge", "Kuthodaw Pagoda", "Ananda Temple",
    "Shwesandaw Pagoda", "Dhamma Yan Gyi", "Mt Popa",
    "Kalaw", "Inle Lake", "Golden Rock", "Kyaiktiyo",
    "Bagan", "Mandalay Hill", "Amarapura", "Mingun",
]

CITY_NAMES = [
    "Rangoon", "Yangon", "Mandalay", "Myitkyina", "Pyin Oo Lwin",
    "Maymyo", "Bhamo", "Katha", "Sagaing", "Inwa", "Ava",
    "Pagan", "Bagan", "Ngapali", "Pyay", "Prome", "Kyaikto", "Bago",
    "Pegu", "Taungoo", "Toungoo",
]

# Transition phrases that indicate a new section within a day
TRANSITION_PHRASES = [
    r"In the afternoon",
    r"In the morning",
    r"After that",
    r"Later that",
    r"Then we",
    r"We then",
    r"Next, we",
    r"Afterwards",
    r"Following this",
    r"On the next day",
    r"The next day",
]
# ------------------------------------------------------------

def extract_figures(content):
    """Return list of (full_figure_html, caption_text)."""
    pattern = r'<figure>(.*?)</figure>'
    figures = []
    for match in re.finditer(pattern, content, re.DOTALL):
        full = match.group(0)
        inner = match.group(1)
        cap = re.search(r'<em>(.*?)</em>', inner, re.DOTALL)
        caption = cap.group(1).strip() if cap else ""
        figures.append((full, caption))
    return figures

def split_into_sections(content):
    """
    Split markdown into sections based on headings, transitions, and city changes.
    Returns a list of (section_title, section_content) where section_title is
    a heading (existing or automatically generated).
    """
    lines = content.split('\n')
    sections = []
    current_section_title = None
    current_section_lines = []
    
    heading_pattern = re.compile(r'^(#{1,6})\s+(.*)$')
    
    i = 0
    while i < len(lines):
        line = lines[i]
        heading_match = heading_pattern.match(line)
        if heading_match:
            if current_section_lines:
                sections.append((current_section_title, '\n'.join(current_section_lines)))
            current_section_title = line.strip()
            current_section_lines = [line]
            i += 1
            continue
        
        is_transition = False
        for phrase in TRANSITION_PHRASES:
            if re.search(phrase, line, re.IGNORECASE):
                is_transition = True
                break
        
        if is_transition:
            if current_section_lines:
                sections.append((current_section_title, '\n'.join(current_section_lines)))
            city_found = None
            for city in CITY_NAMES:
                if city.lower() in line.lower():
                    city_found = city
                    break
            if city_found:
                current_section_title = f"### {city_found}"
            else:
                current_section_title = "### (continued)"
            current_section_lines = [line]
        else:
            current_section_lines.append(line)
        i += 1
    
    if current_section_lines:
        sections.append((current_section_title, '\n'.join(current_section_lines)))
    
    return sections

def find_best_section_for_caption(caption, sections):
    caption_lower = caption.lower()
    
    # 1. Specific places
    sorted_specific = sorted(SPECIFIC_PLACES, key=len, reverse=True)
    for place in sorted_specific:
        place_lower = place.lower()
        if place_lower in caption_lower:
            for idx, (_, sec_content) in enumerate(sections):
                if place_lower in sec_content.lower():
                    return idx
    
    # 2. City names
    for city in CITY_NAMES:
        city_lower = city.lower()
        if city_lower in caption_lower:
            best_idx = None
            best_score = -1
            for idx, (heading, sec_content) in enumerate(sections):
                if heading and city_lower in heading.lower():
                    return idx
                if city_lower in sec_content.lower():
                    other_cities = sum(1 for c in CITY_NAMES if c.lower() != city_lower and c.lower() in sec_content.lower())
                    score = 10 - other_cities
                    if score > best_score:
                        best_score = score
                        best_idx = idx
            if best_idx is not None:
                return best_idx
    
    return 0

def group_figures_by_section(figures, sections):
    groups = defaultdict(list)
    for fig_html, caption in figures:
        sec_idx = find_best_section_for_caption(caption, sections)
        groups[sec_idx].append((fig_html, caption))
    return groups

def chunk_into_rows(items, max_per_row=2):
    return [items[i:i+max_per_row] for i in range(0, len(items), max_per_row)]

def render_row(row):
    if len(row) == 1:
        return row[0][0]
    else:
        return f'<div class="photo-row">\n' + ''.join(fig for fig, _ in row) + '\n</div>'

def insert_figures_into_sections(sections, groups):
    result = []
    for idx, (heading, content) in enumerate(sections):
        clean_content = re.sub(r'<figure>.*?</figure>', '', content, flags=re.DOTALL)
        clean_content = re.sub(r'<div class="photo-row">.*?</div>', '', clean_content, flags=re.DOTALL)
        clean_content = re.sub(r'\n\s*\n', '\n\n', clean_content)
        
        if idx in groups:
            fig_list = groups[idx]
            rows = chunk_into_rows(fig_list)
            fig_blocks = [render_row(row) for row in rows]
            insertion = '\n\n' + '\n\n'.join(fig_blocks) + '\n\n'
        else:
            insertion = ''
        
        section_text = heading + '\n\n' + clean_content + insertion if heading else clean_content + insertion
        result.append(section_text)
    
    return '\n\n'.join(result)

def dry_run_table(groups, sections):
    print("\n" + "="*80)
    print("DRY RUN: Photo placement by section")
    print("="*80)
    for idx in sorted(groups.keys()):
        heading, content = sections[idx]
        preview = heading + " " + content[:60].replace('\n', ' ')
        print(f"\nSection {idx}: {preview[:80]}...")
        for _, cap in groups[idx]:
            print(f"  -> {cap[:60]}")
    print(f"\nTotal photos: {sum(len(v) for v in groups.values())}")
    print("="*80)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    with open(args.input, 'r', encoding='utf-8') as f:
        content = f.read()

    sections = split_into_sections(content)
    figures = extract_figures(content)
    if not figures:
        print("No figures found.")
        return

    groups = group_figures_by_section(figures, sections)

    if args.dry_run:
        dry_run_table(groups, sections)
        return

    new_content = insert_figures_into_sections(sections, groups)
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"Written to {args.output}")

if __name__ == '__main__':
    main()
