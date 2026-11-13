#!/usr/bin/env bash
# test_snippets.sh - compile and run every *.cpp in 2_snippets, report PASS/FAIL.
# Usage:  bash tools/test_snippets.sh        (from the kit folder, or from anywhere)
# Env:    CXX=clang++ bash tools/test_snippets.sh   to use another compiler
# Exit code: 0 if everything passes, 1 otherwise.

# Locate the kit folder from this script's own path.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SNIPPETS_DIR="$SCRIPT_DIR/../2_snippets"

CXX="${CXX:-g++}"
FLAGS="-std=c++17 -Wall -Wextra -O2"

if ! command -v "$CXX" >/dev/null 2>&1; then
    echo "Compiler '$CXX' not found in PATH."
    exit 2
fi
if [ ! -d "$SNIPPETS_DIR" ]; then
    echo "Snippets folder not found: $SNIPPETS_DIR"
    exit 2
fi

# Run with a time limit if 'timeout' exists, plain otherwise.
run_limited() {
    if command -v timeout >/dev/null 2>&1; then
        timeout 10 "$@"
    else
        "$@"
    fi
}

TMP="$(mktemp -d 2>/dev/null || echo "/tmp/snip_test_$$")"
mkdir -p "$TMP"
trap 'rm -rf "$TMP"' EXIT

pass=0
fail=0
failed_names=""

for src in "$SNIPPETS_DIR"/*.cpp; do
    [ -e "$src" ] || continue
    name="$(basename "$src" .cpp)"
    exe="$TMP/$name"

    # Compile. Warnings count as failures too: any compiler output means "not clean".
    # shellcheck disable=SC2086
    if ! "$CXX" $FLAGS "$src" -o "$exe" >"$TMP/$name.build.log" 2>&1; then
        echo "FAIL  $name  (compile error)"
        sed 's/^/      /' "$TMP/$name.build.log" | head -n 20
        fail=$((fail + 1))
        failed_names="$failed_names $name"
        continue
    fi
    if [ -s "$TMP/$name.build.log" ]; then
        echo "FAIL  $name  (warnings)"
        sed 's/^/      /' "$TMP/$name.build.log" | head -n 20
        fail=$((fail + 1))
        failed_names="$failed_names $name"
        continue
    fi

    # Run (exe may need the .exe suffix on MinGW; the shell resolves it either way)
    run_limited "$exe" >"$TMP/$name.out" 2>&1
    rc=$?
    if [ $rc -eq 0 ]; then
        echo "PASS  $name"
        pass=$((pass + 1))
    elif [ $rc -eq 124 ]; then
        echo "FAIL  $name  (timeout > 10 s)"
        fail=$((fail + 1))
        failed_names="$failed_names $name"
    else
        echo "FAIL  $name  (exit code $rc)"
        tail -n 10 "$TMP/$name.out" | sed 's/^/      /'
        fail=$((fail + 1))
        failed_names="$failed_names $name"
    fi
done

echo "----------------------------------------"
echo "Summary: $pass passed, $fail failed"
if [ $fail -ne 0 ]; then
    echo "Failed:$failed_names"
    exit 1
fi
exit 0
