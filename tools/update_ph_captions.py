#!/usr/bin/env python3
"""
Update Philippines food venue captions with dish names from EXIF metadata.

Strategy:
1. Load the pre-built metadata cache (ph_metadata_final.json) which has all
   505 original photos with FileName, DateTimeOriginal, Title, Subject, Keywords.
2. Build a lookup: DateTimeOriginal -> dish name.
3. Scan ALL repo photos in photos/philippines/ at once with exiftool (fast, on C: drive).
4. Match by DateTimeOriginal against the cache.
5. For each venue, find its photos and update figcaptions with dish names.
"""

import subprocess
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Paths
REPO_ROOT = r"C:\Users\andre\Documents\andrestgt.github.io"
PHOTOS_DIR = os.path.join(REPO_ROOT, "photos", "philippines")
FOOD_DIR = os.path.join(REPO_ROOT, "food", "philippines")
CACHE_FILE = r"C:\Users\andre\Desktop\ph_metadata_final.json"

# Source photo folders for Philippines across different years
PH_SOURCE_FOLDERS = [
    r"I:\Pictures\Südostasien 2013\Philippines 2013",
    r"I:\Pictures\Südostasien 2014\Philippines 2014",
    r"I:\Pictures\Südostasien 2015\Philippines 2015",
    r"I:\Pictures\Südostasien 2016\Philippines 2016",
    r"I:\Pictures\Südostasien 2017\Philippines 2017",
    r"I:\Pictures\Südostasien 2018\Philippines 2018",
    r"I:\Pictures\Südostasien 2025\Philippines 2025",
]

# People names to filter out from dish names
PEOPLE_NAMES = {"Linh Truong", "André", "Andre", "Linh", "Truong", "Achim Mohr", "Jen Salcedo"}


def load_cache():
    """Load metadata cache from the pre-built JSON file.
    Returns: (dt_cache, fname_cache) where:
        dt_cache: dict of DateTimeOriginal -> dish name (or None if no dish)
        fname_cache: dict of FileName -> dish name (or None if no dish)
    """
    if not os.path.exists(CACHE_FILE):
        print(f"ERROR: Cache file not found: {CACHE_FILE}")
        print("Run build_cache.bat first to generate it.")
        sys.exit(1)
    
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    dt_cache = {}
    fname_cache = {}
    
    for item in data:
        # Get dish names (filter out people)
        subject = item.get("Subject", "")
        keywords = item.get("Keywords", "")
        
        all_tags = set()
        for val in [subject, keywords]:
            if isinstance(val, str):
                if val.startswith('['):
                    try:
                        parsed = json.loads(val.replace("'", '"'))
                        if isinstance(parsed, list):
                            all_tags.update(parsed)
                    except:
                        all_tags.add(val)
                else:
                    all_tags.add(val)
            elif isinstance(val, list):
                all_tags.update(val)
        
        dishes = [t.strip() for t in all_tags if t.strip() and t.strip() not in PEOPLE_NAMES]
        dish = dishes[0] if dishes else None
        
        # Index by DateTimeOriginal
        dt = item.get("DateTimeOriginal", "")
        if dt:
            dt_cache[dt] = dish
        
        # Index by FileName (for fallback matching)
        fname = item.get("FileName", "")
        if fname:
            fname_cache[fname] = dish
    
    print(f"Loaded {len(data)} entries from cache")
    dish_count = sum(1 for v in dt_cache.values() if v)
    print(f"  {dish_count} with dish names, {len(data) - dish_count} without")
    return dt_cache, fname_cache


def scan_all_repo_photos():
    """Scan ALL repo photos with exiftool in batches and return {filename: datetimeoriginal}."""
    all_photos = []
    for root, dirs, files in os.walk(PHOTOS_DIR):
        for f in files:
            if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                all_photos.append(os.path.join(root, f))
    
    if not all_photos:
        print("No photos found in repo!")
        return {}
    
    print(f"Scanning {len(all_photos)} repo photos with exiftool (in batches)...")
    
    result_map = {}
    batch_size = 50
    for i in range(0, len(all_photos), batch_size):
        batch = all_photos[i:i+batch_size]
        cmd = ["exiftool", "-json", "-DateTimeOriginal", "-filename"] + batch
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
        
        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError:
            print(f"  Error parsing JSON from exiftool: {result.stderr[:200]}")
            continue
        
        for item in data:
            fname = item.get("FileName", "")
            dt = item.get("DateTimeOriginal", "")
            if fname and dt:
                result_map[fname] = dt
        
        print(f"  Batch {i//batch_size + 1}/{(len(all_photos)-1)//batch_size + 1}: {len(data)} photos")
    
    print(f"  Got DateTimeOriginal for {len(result_map)} photos")
    return result_map


def find_all_venue_md_files():
    """Find all venue markdown files."""
    venue_files = []
    for root, dirs, files in os.walk(FOOD_DIR):
        for f in files:
            if f == "index.md":
                full_path = os.path.join(root, f)
                subdirs = [d for d in os.listdir(root) if os.path.isdir(os.path.join(root, d))]
                if not subdirs:
                    venue_files.append(full_path)
    return venue_files


def get_photos_from_md(content):
    """Extract photo filenames from markdown img tags."""
    photos = set()
    for match in re.finditer(r'<img src="[^"]*/([^/"]+\.(?:jpg|jpeg|png|webp))"', content, re.IGNORECASE):
        photos.add(match.group(1))
    return sorted(photos)


def update_venue_captions(venue_md_path, dt_cache, fname_cache, photo_dt_map):
    """Update captions for a single venue markdown file."""
    with open(venue_md_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    venue_photos = get_photos_from_md(content)
    
    if not venue_photos:
        return 0
    
    replacements = {}
    for photo_file in venue_photos:
        dish = None
        
        # Try matching by DateTimeOriginal first
        if photo_file in photo_dt_map:
            dt = photo_dt_map[photo_file]
            if dt in dt_cache:
                dish = dt_cache[dt]
        
        # Fallback: try matching by filename directly
        if dish is None and photo_file in fname_cache:
            dish = fname_cache[photo_file]
        
        if dish:
            # Find the figcaption for this photo
            pattern = rf'(<img src="[^"]*{re.escape(photo_file)}" alt="[^"]*">)\s*<figcaption>([^<]+)</figcaption>'
            match = re.search(pattern, content)
            if match:
                old_caption_text = match.group(2)
                # Skip if caption already has a dish name (contains " — ")
                if " — " in old_caption_text:
                    continue
                old_caption = match.group(0)
                new_caption = f'{match.group(1)}\n  <figcaption>{dish}</figcaption>'
                replacements[old_caption] = new_caption
                print(f"    {photo_file}: '{dish}'")
    
    # Apply replacements
    for old, new in replacements.items():
        content = content.replace(old, new)
    
    if replacements:
        with open(venue_md_path, "w", encoding="utf-8") as f:
            f.write(content)
    
    return len(replacements)


def main():
    print("=" * 60)
    print("Philippines Food Venue Caption Updater")
    print("=" * 60)
    
    # Load cache
    dt_cache, fname_cache = load_cache()
    
    # Scan ALL repo photos at once
    photo_dt_map = scan_all_repo_photos()
    
    # Find all venue markdown files
    venue_files = find_all_venue_md_files()
    print(f"\nFound {len(venue_files)} venue markdown files")
    
    # Process each venue
    total_updated = 0
    total_venues = 0
    for venue_md in sorted(venue_files):
        venue_name = os.path.basename(os.path.dirname(venue_md))
        print(f"\n  [{venue_name}]")
        
        updated = update_venue_captions(venue_md, dt_cache, fname_cache, photo_dt_map)
        if updated > 0:
            total_updated += updated
            total_venues += 1
            print(f"  -> Updated {updated} captions")
        else:
            print(f"  -> No changes")
    
    print(f"\n{'=' * 60}")
    print(f"Done! Updated {total_updated} captions across {total_venues} venues")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
