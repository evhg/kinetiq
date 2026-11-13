#!/opt/homebrew/bin/bash
# one-racket.sh (2026-11-14, the Mac render node): cloud REQUEST one-racket 2026-11-13T13:07Z, approved 14:12Z ("hold
# its re-render batch until AFTER these three sequences, then run it as planned"). Re-renders every still and swivel
# that shows a neck or handle under the one-racket canon (kq_canon.one_racket(): one material, one light, whole-frame
# renders), both feels, grip and Naked, by running the full-weave / dark-look scripts again under the tag one-racket:
#   K05 (fw-k05.sh); K16, K06, K10, K12 (fw-rest.sh; K07 and K09 are held there and come from the dark-look scripts);
#   K11 single and pair, K08, K07, K09 Command (fw-cmdlift.sh) and Pace (fw-pacefix.sh); K02 (fw-k02.sh); K01 (fw-k01.sh).
# Each group's old resume markers are cleared once (queue-nov3.done backed up first as .pre-oneracket), so its scripts
# move the previous files to $FW_OLD and render, push masters and post one STATUS line per item as before.
# Resumable: run it again and finished groups/items are skipped. Exports (mac_export.sh) follow by hand per group.
# one-racket.env (optional, next to this script) is sourced before K01 (the Naked Pace handle card settings).
set -u
cd "$(dirname "$0")"
export KQ_RENDER_OUT=${KQ_RENDER_OUT:-$HOME/kinetiq-render/out}
export FW_R=one-racket FW_RT=2026-11-13T14:12:05Z
export FW_OLD=$KQ_RENDER_OUT/out/final/pre-oneracket-20261114
export FW_CANON="one-racket canon (one racket, one material, one light: every light that reaches the racket reaches all of it, no face/neck link boundary; one weave at the face's tile from the face down the neck to the butt; whole-frame renders only)"
mkdir -p "$FW_OLD"
DONE=$KQ_RENDER_OUT/logs/queue-nov3.done
L=$KQ_RENDER_OUT/logs/one-racket.log
CL=$KQ_RENDER_OUT/logs/one-racket.cleared
touch "$CL"
log() { echo "$(date -u +%FT%TZ) $*" >> "$L"; }
clear_once() {   # clear_once <group> <ERE of that group's markers>
  grep -qxF "$1" "$CL" && return 0
  [ -f "$DONE.pre-oneracket" ] || cp "$DONE" "$DONE.pre-oneracket"
  local n0=$(wc -l < "$DONE")
  grep -vE "$2" "$DONE" > "$DONE.tmp"; mv "$DONE.tmp" "$DONE"
  echo "$1" >> "$CL"; log "cleared $1: $((n0 - $(wc -l < "$DONE"))) markers"
}
run() { log "START $1"; ./"$1" >> "$L" 2>&1; local rc=$?; log "END $1 rc=$rc"; return 0; }
ONLY_G=${1:-all}
want() { [ "$ONLY_G" = all ] || [[ " $ONLY_G " == *" $1 "* ]]; }

log "ONE-RACKET start (groups: $ONLY_G)"
want k05 && { clear_once k05 '^fw (aside|m|status) k05$'; run fw-k05.sh; }
want rest && { clear_once rest '^fw (aside|m|status) (k16|k06|k10|k12)$'; run fw-rest.sh; }
want cmdlift && { clear_once cmdlift '^cl (aside|m|status) '; run fw-cmdlift.sh; }
want pacefix && { clear_once pacefix '^pf (aside|m|status) '; run fw-pacefix.sh; }
want k02 && { clear_once k02 '^fw (aside|unseq|m|status) k02 (c|p|nc|np)$'; run fw-k02.sh; }
if want k01; then
  clear_once k01 '^fw (aside|unseq|m|status) k01( .*)?$'
  [ -f one-racket.env ] && . ./one-racket.env
  run fw-k01.sh
fi
log "ONE-RACKET end"
