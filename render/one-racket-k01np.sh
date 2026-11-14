#!/opt/homebrew/bin/bash
# one-racket-k01np.sh (2026-11-14, the Mac render node): cloud REVIEW 2026-11-14T05:47Z on K01 (mac/exports@6e1d51dc):
# the Naked Pace face read far brighter than Pace grip's (base 17.6 vs 56.3 luma) because KQ_ONE_RACKET_UNION=PaceHandle_
# widened the handle card onto the whole racket. The card now keeps its authored link, the handle only
# (KQ_ONE_RACKET_ASIS=PaceHandle_; one-racket.env): preview previews/wf/k01np-*, face within 0.2 luma of Pace grip,
# the handle keeps its 12K tiles. Re-renders the K01 Naked Pace variant (beam base/full/finale, phone portrait base/full,
# both swivels); the previous files move to pre-k01np-20261114. Then one-racket-k01export.sh nogrip-pace.
set -u
cd "$(dirname "$0")"
export KQ_RENDER_OUT=${KQ_RENDER_OUT:-$HOME/kinetiq-render/out}
export FW_R=one-racket FW_RT=2026-11-14T05:47:33Z
export FW_OLD=$KQ_RENDER_OUT/out/final/pre-k01np-20261114
export FW_CANON="one-racket canon (one racket, one material, one light; whole-frame renders only), with the cloud review 05:47Z: the Naked Pace handle card lights the handle only"
mkdir -p "$FW_OLD"
DONE=$KQ_RENDER_OUT/logs/queue-nov3.done
L=$KQ_RENDER_OUT/logs/one-racket.log
CL=$KQ_RENDER_OUT/logs/one-racket.cleared
log() { echo "$(date -u +%FT%TZ) $*" >> "$L"; }
if ! grep -qxF k01np "$CL"; then
  cp "$DONE" "$DONE.pre-k01np"
  n0=$(wc -l < "$DONE")
  grep -vE '^fw (aside|unseq|m|status) k01 nogrip-pace$' "$DONE" > "$DONE.tmp"; mv "$DONE.tmp" "$DONE"
  echo k01np >> "$CL"; log "cleared k01np: $((n0 - $(wc -l < "$DONE"))) markers"
fi
. ./one-racket.env
log "START k01np fw-k01.sh (ASIS=${KQ_ONE_RACKET_ASIS:-} UNION=${KQ_ONE_RACKET_UNION:-} PH_ROLL=${KQ_PH_ROLL:-})"
./fw-k01.sh >> "$L" 2>&1; rc=$?
log "END k01np fw-k01.sh rc=$rc"
exit $rc
