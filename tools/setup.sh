#!/usr/bin/env bash
# One-shot setup on a school Linux PC. No admin rights needed.
#   In Dolphin: open the drive's Post-Apo-C-plus-plus folder, Shift+F4 (terminal here), then:
#     bash tools/setup.sh            copy, unpack, start search, open the kit
#     bash tools/setup.sh --no-open  copy and unpack only
# Safe to run twice.
set -u
USB="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK="$HOME/Post-Apo-C-plus-plus"
OPEN=1; [ "${1:-}" = "--no-open" ] && OPEN=0
echo "== Drive: $USB"

if [ "$USB" != "$WORK" ]; then
  echo "== Copying the kit to $WORK"
  mkdir -p "$WORK"
  for d in 1_cheatsheet 2_snippets 3_solved_exams 4_course 5_repo site_src tools START_HERE.html README.md; do
    [ -e "$USB/$d" ] && cp -r "$USB/$d" "$WORK/"
  done
  # search index: copy to local disk (fast queries); big read-only data: link from the drive
  if [ -d "$USB/8_search" ]; then
    echo "== Copying the search index"
    cp -r "$USB/8_search" "$WORK/"
  fi
  for d in 6_reference 7_stackoverflow; do
    [ -e "$USB/$d" ] || continue
    rm -rf "${WORK:?}/$d" 2>/dev/null
    ln -s "$USB/$d" "$WORK/$d" 2>/dev/null || echo "   (could not link $d; it stays on the drive)"
  done
fi

# portable Firefox: unpack once into the home folder (drives are often mounted no-exec)
FF=""
TAR="$(ls "$USB"/9_browser/firefox-*.tar.xz 2>/dev/null | head -1)"
if [ -n "$TAR" ]; then
  if [ ! -x "$WORK/firefox/firefox" ]; then
    echo "== Unpacking Firefox (about 20 s)"
    tar -xJf "$TAR" -C "$WORK" || echo "   (unpacking failed: the PC's own browser will be used)"
  fi
  if [ -x "$WORK/firefox/firefox" ]; then
    FF="$WORK/firefox/firefox"
    PROFILE="$WORK/ffprofile"
    mkdir -p "$PROFILE"
    cat > "$PROFILE/user.js" <<'EOF'
user_pref("browser.shell.checkDefaultBrowser", false);
user_pref("browser.aboutwelcome.enabled", false);
user_pref("browser.startup.homepage_override.mstone", "ignore");
user_pref("startup.homepage_welcome_url", "");
user_pref("datareporting.policy.dataSubmissionEnabled", false);
user_pref("toolkit.telemetry.reportingpolicy.firstRun", false);
user_pref("app.update.auto", false);
user_pref("browser.tabs.warnOnClose", false);
EOF
  fi
fi

[ "$OPEN" = 1 ] || { echo "== Done. Start later with: bash $WORK/tools/open.sh"; exit 0; }
bash "$WORK/tools/open.sh"
