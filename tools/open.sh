#!/usr/bin/env bash
# Start the search server (if the index exists) and open the kit + search page.
# Uses the portable Firefox unpacked by setup.sh when present, else the PC's browser.
set -u
K="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PORT=8090
PY="$(command -v python3 || command -v python || true)"
URLS=("$K/START_HERE.html")

if [ -n "$PY" ] && [ -f "$K/8_search/search.db" ]; then
  if ! "$PY" -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:$PORT/', timeout=1)" 2>/dev/null; then
    echo "== Starting search on http://127.0.0.1:$PORT"
    nohup "$PY" "$K/tools/search/serve.py" --port "$PORT" --no-browser > "${TMPDIR:-/tmp}/pac-search.log" 2>&1 &
    for _ in $(seq 1 30); do
      "$PY" -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:$PORT/', timeout=1)" 2>/dev/null && break
      sleep 0.3
    done
  fi
  URLS+=("http://127.0.0.1:$PORT/")
else
  echo "   (no search index or no python3: search page skipped; bash tools/find.sh still works)"
fi

if [ -x "$K/firefox/firefox" ]; then
  echo "== Opening portable Firefox"
  # no --no-remote: if our Firefox (this profile) is still open, the pages go to it as new tabs
  nohup "$K/firefox/firefox" --profile "$K/ffprofile" "${URLS[@]}" > /dev/null 2>&1 &
else
  for u in "${URLS[@]}"; do xdg-open "$u" > /dev/null 2>&1 & done
fi
echo "== Kit: ${URLS[0]}"
[ "${#URLS[@]}" -gt 1 ] && echo "== Search: ${URLS[1]}   (terminal: bash $K/tools/search.sh \"words\")"
exit 0
