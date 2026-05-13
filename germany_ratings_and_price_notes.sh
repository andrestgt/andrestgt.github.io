#!/usr/bin/env bash
set -euo pipefail

add_block() {
  file="$1"
  label="$2"

  grep -q "## Ratings" "$file" && return

  awk -v cat="$label" '
  /### Practical/ && !done {
    print "## Ratings"
    print ""
    print "| Category        | Score  |"
    print "|-----------------|--------|"
    print "| " cat " | —/10 |"
    print "| Service         | —/10 |"
    print "| Value for money | —/10 |"
    print "| Atmosphere      | —/10 |"
    print "| Overall         | —/10 |"
    print ""
    done=1
  }
  { print }
  ' "$file" > "$file.tmp" && mv "$file.tmp" "$file"
}

# restaurants
find food/germany -path "*/restaurants/*/index.md" | while read -r f; do
  add_block "$f" "Food           "
done

# cafes
find food/germany -path "*/cafes/*/index.md" | while read -r f; do
  add_block "$f" "Coffee         "
done

# bars drinks
for f in \
food/germany/baden-wuerttemberg/stuttgart/bars-pubs/tschechen-soehne/index.md \
food/germany/berlin/berlin/bars-pubs/luftgarten/index.md \
food/germany/berlin/berlin/bars-pubs/que-pasa/index.md \
food/germany/saarland/saarbruecken/bars-pubs/wallys-irish-pub-saarbruecken/index.md \
food/germany/sachsen/leipzig/bars-pubs/peter-k/index.md
do
  add_block "$f" "Drinks         "
done

# bars food
for f in \
food/germany/baden-wuerttemberg/stuttgart/bars-pubs/wirtshaus-troll/index.md \
food/germany/sachsen/leipzig/bars-pubs/felsenkeller-leipzig/index.md
do
  add_block "$f" "Bar food       "
done

# price note
find food/germany -path "*/restaurants/index.md" | while read -r f; do
  grep -q "Price level note" "$f" && continue
  cat >> "$f" <<EOF

**Price level note:**  
Price levels refer to the approximate cost for **two people** ordering an average meal **without alcoholic drinks**.
EOF
done
