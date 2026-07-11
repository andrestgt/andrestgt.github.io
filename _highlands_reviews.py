import docx2txt

t = docx2txt.process(r'C:\Users\andre\Downloads\Reviewsmaster.docx')
lines = t.split('\n')

# Find Vietnam section
viet_start = None
for i,l in enumerate(lines):
    if l.strip()=='Vietnam' and i>5000: viet_start=i; break

# Extract reviews from Kon Tum, Gia Lai / Pleiku, Đắk Lắk / Buôn Ma Thuột
targets = ['Kon Tum', 'Gia Lai', 'Đắk Lắk', 'Dak Lak', 'Buôn Ma Thuột']
reviews = []
current_prov = ''
in_target = False
current_name = None
current_stars = ''
current_addr = ''
current_text = []

for i in range(viet_start, len(lines)):
    s = lines[i].strip()
    
    # Province boundary
    if '/' in s and len(s) < 60:
        # Save current review if any
        if current_name and current_text:
            reviews.append({'prov': current_prov, 'name': current_name, 'addr': current_addr, 'text': '\n'.join(current_text)})
            current_name = None
            current_text = []
        current_prov = s
        in_target = any(t.lower() in s.lower() for t in targets)
        continue
    
    if not in_target:
        continue
    
    if not s:
        # Empty line - might end a review
        if current_name and current_text:
            n = i + 1
            while n < len(lines) and not lines[n].strip():
                n += 1
            if n < len(lines):
                nl = lines[n].strip()
                if '★' in nl or ('/' in nl and len(nl) < 60):
                    reviews.append({'prov': current_prov, 'name': current_name, 'addr': current_addr, 'text': '\n'.join(current_text)})
                    current_name = None
                    current_text = []
        continue
    
    if s.startswith('—') or s.startswith('Service') or s.startswith('Food:'):
        continue
    
    if '★' in s:
        current_stars = s
        continue
    
    if not current_name:
        current_name = s
    elif not current_addr:
        current_addr = s
    else:
        current_text.append(s)

# Last review
if current_name and current_text:
    reviews.append({'prov': current_prov, 'name': current_name, 'addr': current_addr, 'text': '\n'.join(current_text)})

# Write output
with open(r'c:\Users\andre\Documents\andrestgt.github.io\_highlands.txt', 'w', encoding='utf-8') as f:
    f.write(f"Total reviews found: {len(reviews)}\n\n")
    for r in reviews:
        f.write(f"PROV: {r['prov']}\n")
        f.write(f"NAME: {r['name']}\n")
        f.write(f"ADDR: {r['addr']}\n")
        f.write(f"TEXT: {r['text']}\n")
        f.write("---\n")

print(f'Done - {len(reviews)} reviews')