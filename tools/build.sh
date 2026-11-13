#!/usr/bin/env bash
# Configure + build a CMake project in ./build (Release by default).
#   bash build.sh [project_dir] [Debug|Release|Sanitize]
# Sanitize = Debug + AddressSanitizer/UBSan: crashes point at the exact line.
set -e
DIR="${1:-.}"; MODE="${2:-Release}"
cd "$DIR"
if [ ! -f CMakeLists.txt ]; then echo "No CMakeLists.txt in $(pwd)"; exit 1; fi
FLAGS=()
case "$MODE" in
  Sanitize) FLAGS=(-DCMAKE_BUILD_TYPE=Debug "-DCMAKE_CXX_FLAGS=-g -fsanitize=address,undefined -fno-omit-frame-pointer") ;;
  *)        FLAGS=(-DCMAKE_BUILD_TYPE="$MODE") ;;
esac
mkdir -p build && cd build
cmake "${FLAGS[@]}" .. && make -j"$(nproc 2>/dev/null || echo 2)"
echo; echo "Built in $(pwd). Executables:"; find . -maxdepth 1 -type f -perm -u+x -printf '  ./%f\n' 2>/dev/null || ls
