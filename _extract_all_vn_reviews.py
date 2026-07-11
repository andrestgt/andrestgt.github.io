import docx2txt

t = docx2txt.process(r'C:\Users\andre\Downloads\Reviewsmaster.docx')
lines = t.split('\n')

# Find Vietnam section
viet_start = None
for i, l in enumerate(lines):
    if l.strip() == 'Vietnam' and i > 5000:
        viet_start = i
        break

print(f"Vietnam section starts at line {viet_start}")

# Extract all reviews from Vietnam section
# Structure: Province/city header (contains '/'), then places with optional star rating,
# then optional address line, then review text paragraphs

reviews = []
current_prov = ''
current_name = ''
current_addr = ''
current_text_lines = []
in_star = False  # skip star rating lines

def save_review():
    global current_name, current_addr, current_text_lines
    if current_name and current_text_lines:
        # Join text, clean up
        text = ' '.join(current_text_lines).strip()
        text = ' '.join(text.split())  # normalize whitespace
        reviews.append({
            'prov': current_prov,
            'name': current_name,
            'addr': current_addr,
            'text': text
        })
    current_name = ''
    current_addr = ''
    current_text_lines = []

for i in range(viet_start, len(lines)):
    s = lines[i].strip()
    
    # Skip empty lines
    if not s:
        continue
    
    # Province/city header (e.g. "Hà Nội / Northern Vietnam")
    if '/' in s and len(s) < 80 and '★' not in s and not s.startswith('—'):
        # Check if it looks like a province header (not a review text with slash)
        # Province headers are short and contain exactly one slash
        parts = s.split('/')
        if len(parts) == 2 and len(parts[0]) < 50 and len(parts[1]) < 50:
            save_review()
            current_prov = s
            continue
    
    # Skip lines like "—" or "Service:" or "Food:"
    if s.startswith('—') or s.startswith('Service') or s.startswith('Food:'):
        continue
    
    # Skip star rating lines
    if '★' in s and len(s) < 10:
        continue
    
    # If we haven't set a name yet, this line is the place name
    if not current_name:
        current_name = s
    # If we have a name but no address, check if this looks like an address
    elif not current_addr and not current_text_lines:
        # Addresses typically start with numbers or have commas
        # But also could be the start of review text
        # Heuristic: if line contains digits and has commas/Vietnam, it's likely an address
        if (any(c.isdigit() for c in s) and (',' in s or 'Vietnam' in s or 'P.' in s or 'Đ.' in s or 'QL' in s)) or \
           ('Vietnam' in s and len(s) > 20):
            current_addr = s
        else:
            # This is review text, not an address
            current_text_lines.append(s)
    else:
        # Check if this is a new section header (next province or next place)
        # If line starts a new place (has ★ or is followed by address pattern), save current
        # But if it's just more review text, append it
        current_text_lines.append(s)

# Save last review
save_review()

# Write output
outpath = r'c:\Users\andre\Documents\andrestgt.github.io\_all_vn_reviews.txt'
with open(outpath, 'w', encoding='utf-8') as f:
    f.write(f"Total reviews found: {len(reviews)}\n\n")
    for r in reviews:
        f.write(f"PROV: {r['prov']}\n")
        f.write(f"NAME: {r['name']}\n")
        f.write(f"ADDR: {r['addr']}\n")
        f.write(f"TEXT: {r['text']}\n")
        f.write("---\n")

print(f"Done - {len(reviews)} reviews written to {outpath}")