#!/usr/bin/env bash
# Offline full-text search over the kit, cppreference and Stack Overflow.
#   bash tools/search.sh                      start the search page (browser)
#   bash tools/search.sh --port 8091 --no-browser
#   bash tools/search.sh "pop_back"           top 10 results in the terminal
# First time: python3 tools/search/build_index.py   (builds 8_search/search.db)
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY=""
for c in python3 python; do
  if command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys; sys.exit(sys.version_info < (3, 8))' >/dev/null 2>&1; then PY="$c"; break; fi
done
if [ -z "$PY" ]; then echo "python3 (3.8+) not found" >&2; exit 1; fi
if [ ! -f "$HERE/8_search/search.db" ]; then
  echo "No index yet. Build it with:  $PY \"$HERE/tools/search/build_index.py\"" >&2; exit 1
fi
if [ $# -eq 0 ] || [[ "$1" == --* ]]; then
  exec "$PY" "$HERE/tools/search/serve.py" "$@"
fi
exec "$PY" "$HERE/tools/search/engine.py" "$@"
