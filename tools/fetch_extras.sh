#!/usr/bin/env bash
# Fetch everything that is NOT in the public repository (needs internet, run once, safe to re-run):
#   - Kermorgant's course repo          -> 5_repo/ecn_arpro
#   - the exam subjects from that repo   -> 4_course/subjects/
#   - offline cppreference (HTML book)   -> 6_reference/cppreference/
#   - searchable text of every PDF       -> 4_course/text/   (needs pdftotext: sudo apt install poppler-utils)
#   - top 5,000 Stack Overflow [c++] Q&As -> 7_stackoverflow/   (public API, CC BY-SA)
#   - full-text search index              -> 8_search/search.db
#   - portable Firefox ESR for Linux      -> 9_browser/          (skip these three with --small)
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

# ---- the big package: Stack Overflow, search index, portable Firefox (skip with --small)
if [ "${1:-}" != "--small" ]; then
  echo "== 5/7 Stack Overflow: top 5,000 [c++] Q&As via the public API (~100 requests, cached, CC BY-SA)"
  "$PY" tools/search/fetch_stackoverflow.py || echo "   (Stack Overflow fetch failed; search works without it)"

  echo "== 6/7 Search index"
  "$PY" tools/search/build_index.py

  echo "== 7/7 Portable Firefox ESR for Linux (~86 MB, SHA512-checked)"
  if ls 9_browser/firefox-*.tar.xz >/dev/null 2>&1; then
    echo "   already there"
  else
    mkdir -p 9_browser
    url="$(curl -sSIL -o /dev/null -w '%{url_effective}' 'https://download.mozilla.org/?product=firefox-esr-latest-ssl&os=linux64&lang=en-US')"
    f="$(basename "$url")"; ver="${f#firefox-}"; ver="${ver%.tar.*}"
    curl -fL --progress-bar -o "9_browser/$f" "$url"
    curl -fsSL -o 9_browser/SHA512SUMS "https://download-installer.cdn.mozilla.net/pub/firefox/releases/$ver/SHA512SUMS"
    want="$(grep " linux-x86_64/en-US/$f\$" 9_browser/SHA512SUMS | cut -d' ' -f1)"
    got="$(sha512sum "9_browser/$f" | cut -d' ' -f1)"
    if [ -n "$want" ] && [ "$want" = "$got" ]; then echo "   SHA512 OK ($f)"; else echo "!! checksum mismatch: deleting $f"; rm -f "9_browser/$f"; fi
  fi
fi
echo "== Done. Copy the folder to a drive; on the exam PC: bash tools/setup.sh"
