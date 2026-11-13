#!/usr/bin/env bash
# Search EVERYTHING on the stick (cheat-sheets, snippets, solved exams, slides text, course repo).
#   bash find.sh priority_queue
#   bash find.sh "erase.*remove"      (regex, case-insensitive)
#   bash find.sh -w set               (extra grep flags go first)
# Add -C 3 for 3 lines of context:  bash find.sh -C 3 min_element
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [ $# -eq 0 ]; then sed -n '2,7p' "${BASH_SOURCE[0]}"; exit 1; fi
cd "$HERE"
grep -rniE --color=always --exclude-dir=.git --exclude-dir=build --exclude-dir=6_reference \
  --include='*.md' --include='*.txt' --include='*.cpp' --include='*.h' --include='*.hpp' --include='*.py' --include='*.yaml' \
  "$@" 1_cheatsheet 2_snippets 3_solved_exams 4_course/text 5_repo | less -RFX
