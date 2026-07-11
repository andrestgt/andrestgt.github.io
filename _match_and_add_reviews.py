"""Match missing reviews from docx to travelogue files."""
import docx2txt
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

# 1. Extract raw docx text
t = docx2txt.process(r'C:\Users\andre\Downloads\Reviewsmaster.docx')
lines = t.split('\n')

# Find Vietnam section
viet_start = None
for i, l in enumerate(lines):
    if l.strip() == 'Vietnam' and i > 5000:
        viet_start = i
        break

viet_lines = lines[viet_start:]

# 2. Build a cleaner review extractor - find all place names and their review text
# The docx structure seems to be:
# Province header (with /)
# blank line
# Place name
# blank line
# Stars
# blank line 
# Address (optional)
# Review text paragraphs...

# Let me just search for known missing place names and extract context

# Missing entries from _missing.txt
missing_entries = {
    # da-nang-to-hanoi.md
    'Sumo Cafe': 'da-nang-to-hanoi.md',
    'Nghia Phuc': 'da-nang-to-hanoi.md',
    
    # hanoi-to-danang.md
    'Quảng Dũng': 'hanoi-to-danang.md',
    'Chào Vietnam': 'hanoi-to-danang.md',
    
    # hanoi-to-sapa.md
    'phở thịt trâu': 'hanoi-to-sapa.md',
    'nem chua': 'hanoi-to-sapa.md',
    'Cát Bà Ferry': 'hanoi-to-sapa.md',
    'bánh cuốn': 'hanoi-to-sapa.md',
    
    # hoi-an-to-nha-trang.md
    "Chips&Fish": 'hoi-an-to-nha-trang.md',
    "Bungalow Beach Bar": 'hoi-an-to-nha-trang.md',
    "Baby Mustard": 'hoi-an-to-nha-trang.md',
    "Roving Chillhouse": 'hoi-an-to-nha-trang.md',
    "Madame Khanh": 'hoi-an-to-nha-trang.md',
    "Madamquan": 'hoi-an-to-nha-trang.md',
    "Gỏi Lá": 'hoi-an-to-nha-trang.md',
    "Eva Café": 'hoi-an-to-nha-trang.md',
    "Phở Khô Hồng": 'hoi-an-to-nha-trang.md',
    "Daklac Coffee": 'hoi-an-to-nha-trang.md',
    
    # sapa-to-hanoi-ha-giang.md
    "Phúc Bản Mề": 'sapa-to-hanoi-ha-giang.md',
    "Hoàng Su Phì": 'sapa-to-hanoi-ha-giang.md',
    "Nam Thy": 'sapa-to-hanoi-ha-giang.md',
    "Khánh Chi": 'sapa-to-hanoi-ha-giang.md',
    "Quản Bạ": 'sapa-to-hanoi-ha-giang.md',
    "thắng cổ": 'sapa-to-hanoi-ha-giang.md',
    "currywurst": 'sapa-to-hanoi-ha-giang.md',
}

# For each search term, find it in the docx and extract surrounding text
for search_term, fname in sorted(missing_entries.items()):
    found_idx = None
    for i, l in enumerate(viet_lines):
        if search_term.lower() in l.lower():
            found_idx = i
            break
    
    if found_idx:
        # Extract surrounding context - go back to find province and name
        start = max(0, found_idx - 20)
        end = min(len(viet_lines), found_idx + 30)
        context = viet_lines[start:end]
        
        print(f"\n{'='*60}")
        print(f"SEARCH: {search_term} -> {fname}")
        print(f"CONTEXT:")
        for j, cl in enumerate(context):
            marker = ">>>" if start + j == found_idx else "   "
            print(f"{marker} {start+j}: {cl}")
    else:
        print(f"\nNOT FOUND: {search_term}")

print("\nDone.")