#!/usr/bin/env bash
# req-full-weave.sh (2026-11-07, the Mac render node): cloud REQUEST full-weave (folds in pace-naked-weave): every racket
# image once with the full-weave canon (fw-lib.sh), in the page's order: K01, K02, K05, K08 + K11, then the rest. Each
# group is its own resumable script (fw-<group>.sh, read fresh when its turn comes, so later groups can be written while
# earlier ones render); the runner stops at the first group that fails. PUSH=0 renders only.
#   nohup caffeinate -dimsu render/req-full-weave.sh >> ~/kinetiq-render/out/logs/queue-mac.log 2>&1 &
if [ "${BASH_VERSINFO[0]}" -lt 5 ] && [ -x /opt/homebrew/bin/bash ]; then exec /opt/homebrew/bin/bash "$0" "$@"; fi
KIT=$(cd "$(dirname "$0")" && pwd)
GROUPS_=${FW_GROUPS:-"k01 k02 k05 k08k11 rest"}
echo "$(date -u +%FT%TZ) FW-RUN groups: $GROUPS_ push ${PUSH:-1}"
for g in $GROUPS_; do
  s="$KIT/fw-$g.sh"
  [ -f "$s" ] || { echo "$(date -u +%FT%TZ) FW-STOP: $s not written yet"; exit 2; }
  /opt/homebrew/bin/bash "$s" || { echo "$(date -u +%FT%TZ) FW-STOP: $g failed (exit $?)"; exit 1; }
done
echo "$(date -u +%FT%TZ) FW-RUN done"
