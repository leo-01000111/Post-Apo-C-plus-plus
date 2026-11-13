#!/usr/bin/env bash
# One-shot setup on a school Linux PC (a few seconds).
#   In Dolphin: open the drive's Post-Apo-C-plus-plus folder, Shift+F4 (terminal here), then:  bash tools/setup.sh
# Copies the study material to ~/Post-Apo-C-plus-plus (local disk = fast, writable) and links the
# offline C++ docs from the stick (7,000 small files, too slow to copy). Safe to run twice.
set -u
USB="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK="$HOME/Post-Apo-C-plus-plus"
echo "== Stick: $USB"
if [ "$USB" = "$WORK" ]; then echo "== Already running from $WORK, nothing to copy."; exit 0; fi
echo "== Copying study material to $WORK"
mkdir -p "$WORK"
for d in 1_cheatsheet 2_snippets 3_solved_exams 4_course 5_repo tools START_HERE.html README.md; do
  [ -e "$USB/$d" ] && cp -r "$USB/$d" "$WORK/"
done
# link (not copy) the offline cppreference so START_HERE.html's link works from ~/Post-Apo-C-plus-plus
rm -rf "$WORK/6_reference" 2>/dev/null
ln -s "$USB/6_reference" "$WORK/6_reference" 2>/dev/null \
  || echo "   (could not link the C++ docs; open $USB/6_reference/cppreference/reference/en/index.html directly)"
echo "== Done. Next:"
echo "   cd $WORK"
echo "   xdg-open START_HERE.html          # start page in the browser"
echo "   bash tools/find.sh <word>         # search everything"
