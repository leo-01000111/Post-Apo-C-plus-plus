#!/usr/bin/env bash
# Fetch everything that is NOT in the public repository (needs internet, run once, safe to re-run):
#   - Kermorgant's course repo          -> 5_repo/ecn_arpro
#   - the exam subjects from that repo   -> 4_course/subjects/
#   - offline cppreference (HTML book)   -> 6_reference/cppreference/
#   - searchable text of every PDF       -> 4_course/text/   (needs pdftotext: sudo apt install poppler-utils)
# Slides are not public: download them from Hippocampus (ARPRO course page), drop the PDFs into
# 4_course/slides/, then run this script again so they become searchable too.
#
#   bash tools/fetch_extras.sh
set -eu
K="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$K"
PY="$(command -v python3 || command -v python || true)"
mkdir -p 4_course/slides 4_course/subjects 4_course/text 5_repo 6_reference

echo "== 1/4 Course repo (github.com/oKermorgant/ecn_arpro)"
if [ -d 5_repo/ecn_arpro/.git ]; then git -C 5_repo/ecn_arpro pull -q; else git clone -q https://github.com/oKermorgant/ecn_arpro.git 5_repo/ecn_arpro; fi

echo "== 2/4 Exam subjects"
R=5_repo/ecn_arpro
cp "$R/sudoku/subject/sudoku.pdf"           4_course/subjects/sudoku_exam.pdf
cp "$R/maze/subject/ARPRO_maze.pdf"         4_course/subjects/maze_exam.pdf
cp "$R/mobile_robot/subject/ARPRO_lab2.pdf" 4_course/subjects/mobile_robot_lab2.pdf
cp "$R/open_projects/open_projects.pdf"     4_course/subjects/open_projects.pdf

echo "== 3/4 Offline cppreference"
if [ -f 6_reference/cppreference/reference/en/index.html ]; then
  echo "   already there"
else
  V=20250209
  TMP="$(mktemp -d)"
  curl -fL --progress-bar -o "$TMP/cppref.zip" \
    "https://github.com/PeterFeicht/cppreference-doc/releases/download/v$V/html-book-$V.zip"
  if command -v unzip >/dev/null; then unzip -q "$TMP/cppref.zip" -d 6_reference/cppreference
  elif [ -n "$PY" ]; then "$PY" -m zipfile -e "$TMP/cppref.zip" 6_reference/cppreference
  else echo "!! need unzip or python3 to extract $TMP/cppref.zip"; exit 1; fi
  rm -rf "$TMP"
fi

echo "== 4/4 Searchable text of the PDFs"
if command -v pdftotext >/dev/null; then
  n=0
  for f in 4_course/slides/*.pdf 4_course/subjects/*.pdf; do
    [ -e "$f" ] || continue
    pdftotext -layout "$f" "4_course/text/$(basename "${f%.pdf}").txt" && n=$((n + 1))
  done
  echo "   $n PDFs converted"
else
  echo "   pdftotext not found (sudo apt install poppler-utils): find.sh will not search inside the PDFs"
fi

[ -n "$(ls 4_course/slides/*.pdf 2>/dev/null)" ] || echo "Note: no slides yet. Get them from Hippocampus, put them in 4_course/slides/, run this again."
echo "== Done. Open START_HERE.html"
