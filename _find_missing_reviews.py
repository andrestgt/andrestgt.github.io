"""Scan vietnam-2020 travelogue files and identify entries missing review text."""
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

base = r'c:\Users\andre\Documents\andrestgt.github.io\travels\vietnam-2020'
files = sorted(os.listdir(base))

out_lines = []

for fname in files:
    if not fname.endswith('.md'):
        continue
    fpath = os.path.join(base, fname)
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    out_lines.append(f"\n=== {fname} ===")
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        # Find ### entries (place headers)
        if line.startswith('### ') and '—' in line:
            header = line[4:]  # remove '### '
            # Look ahead: next line should be photo timestamp
            i += 1
            if i < len(lines):
                next_line = lines[i].strip()
                if next_line.startswith('*') and 'Vietnam20' in next_line:
                    # This is a photo line, look for review text after
                    i += 1
                    # Skip any blank lines
                    while i < len(lines) and not lines[i].strip():
                        i += 1
                    # Check if next substantive line is review text or another header
                    if i < len(lines):
                        following = lines[i].strip()
                        if following.startswith('###') or following.startswith('##') or following.startswith('---') or following.startswith('**'):
                            out_lines.append(f"  MISSING: {header}")
                        elif following.startswith('*') and 'Vietnam20' in following:
                            # Another photo line (double photo), skip
                            i += 1
                            while i < len(lines) and not lines[i].strip():
                                i += 1
                            if i < len(lines):
                                following2 = lines[i].strip()
                                if following2.startswith('###') or following2.startswith('##') or following2.startswith('---') or following2.startswith('**'):
                                    out_lines.append(f"  MISSING: {header}")
        i += 1

out_lines.append("\nDone.")

outpath = r'c:\Users\andre\Documents\andrestgt.github.io\_missing.txt'
with open(outpath, 'w', encoding='utf-8') as f:
    f.write('\n'.join(out_lines))
print(f"Output written to {outpath}")
