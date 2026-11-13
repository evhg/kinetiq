#!/opt/homebrew/bin/bash
# one-racket-k02fix.sh (2026-11-14, the Mac render node): cloud REVIEW 2026-11-13T20:37Z on K02 (mac/exports@f0c229b1):
# keep the lit side wall and neck, but the ring fill must not light the bores, the throat's inner wall or the bridge
# (fw-k02.sh now sets KQ_ONE_RACKET_KEEP=holes,throat,bridgewall). Re-renders all four K02 stills and swivels (Command
# 60 frames, Pace 45; grip and Naked); the previous one-racket K02 files move to pre-k02fix-20261114, not over the
# pre-one-racket originals. Not while one-racket.sh runs. Then one-racket-k02export.sh ships all eight sequences together.
set -u
cd "$(dirname "$0")"
export KQ_RENDER_OUT=${KQ_RENDER_OUT:-$HOME/kinetiq-render/out}
export FW_R=one-racket FW_RT=2026-11-13T20:37:51Z
export FW_OLD=$KQ_RENDER_OUT/out/final/pre-k02fix-20261114
export FW_CANON="one-racket canon (one racket, one material, one light; whole-frame renders only), with the cloud reviews 18:59Z and 20:37Z: the ring fill reaches the whole racket, the bores, throat and bridge keep their own light (dark holes falling to black)"
mkdir -p "$FW_OLD"
DONE=$KQ_RENDER_OUT/logs/queue-nov3.done
L=$KQ_RENDER_OUT/logs/one-racket.log
CL=$KQ_RENDER_OUT/logs/one-racket.cleared
log() { echo "$(date -u +%FT%TZ) $*" >> "$L"; }
if ! grep -qxF k02fix "$CL"; then
  cp "$DONE" "$DONE.pre-k02fix"
  n0=$(wc -l < "$DONE")
  grep -vE '^fw (aside|unseq|m|status) k02 (c|p|nc|np)$' "$DONE" > "$DONE.tmp"; mv "$DONE.tmp" "$DONE"
  echo k02fix >> "$CL"; log "cleared k02fix: $((n0 - $(wc -l < "$DONE"))) markers"
fi
log "START k02fix fw-k02.sh"
./fw-k02.sh >> "$L" 2>&1; rc=$?
log "END k02fix fw-k02.sh rc=$rc"
exit $rc
