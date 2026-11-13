#!/opt/homebrew/bin/bash
# one-racket-wallfix.sh (2026-11-14, the Mac render node): cloud REVIEW 2026-11-13T18:59Z on the first one-racket
# exports: K06 and K10 NOT approved, "add one soft fill (or raise an existing one) that reaches the WHOLE racket, face,
# rim, walls and neck alike, not a wall-only link". Face mode had dropped each shot's wall light (K06 RkWall / RkWallW,
# K10 lg_side / lg_side2: they lit 3-5 of the racket's parts); KQ_ONE_RACKET_UNION now gives each of them the whole
# racket instead (preview previews/wf/a-k06*, a-k10*: K10 Command right wall mean 56 -> 80, old 81; Pace 15 -> 34, old 34).
# Re-renders K06 and K10 (grip and Naked, both feels) through fw-rest.sh: K16 and K12 keep their markers and are skipped
# (the union names no light of theirs). The previous one-racket files move to pre-wallfix-20261114, not over the
# pre-one-racket originals. Run only while one-racket.sh is not running (both rewrite queue-nov3.done).
set -u
cd "$(dirname "$0")"
export KQ_RENDER_OUT=${KQ_RENDER_OUT:-$HOME/kinetiq-render/out}
export FW_R=one-racket FW_RT=2026-11-13T18:59:00Z
export FW_OLD=$KQ_RENDER_OUT/out/final/pre-wallfix-20261114
export FW_CANON="one-racket canon (one racket, one material, one light: every light that reaches the racket reaches all of it, no face/neck link boundary; whole-frame renders only), with the wall fill of the cloud review 18:59Z (the shot's soft wall card now reaches the whole racket, face, rim, walls and neck alike)"
export KQ_ONE_RACKET_UNION=RkWall,lg_side
mkdir -p "$FW_OLD"
DONE=$KQ_RENDER_OUT/logs/queue-nov3.done
L=$KQ_RENDER_OUT/logs/one-racket.log
CL=$KQ_RENDER_OUT/logs/one-racket.cleared
log() { echo "$(date -u +%FT%TZ) $*" >> "$L"; }
if ! grep -qxF wallfix "$CL"; then
  cp "$DONE" "$DONE.pre-wallfix"
  n0=$(wc -l < "$DONE")
  grep -vE '^fw (aside|m|status) (k06|k10)$' "$DONE" > "$DONE.tmp"; mv "$DONE.tmp" "$DONE"
  echo wallfix >> "$CL"; log "cleared wallfix: $((n0 - $(wc -l < "$DONE"))) markers"
fi
log "START wallfix (fw-rest.sh, union $KQ_ONE_RACKET_UNION)"
./fw-rest.sh >> "$L" 2>&1; rc=$?
log "END wallfix rc=$rc"
exit $rc
