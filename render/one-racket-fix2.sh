#!/opt/homebrew/bin/bash
# one-racket-fix2.sh (2026-11-14, the Mac render node): cloud REVIEW 2026-11-13T19:20Z on cmdlift (mac/exports@d2ffbf73):
# K09 approved; re-render with the union on and re-export as one set: K11 single and pair (+ Naked), K07, K08 (+ Naked),
# Pace versions the same.
#   KQ_ONE_RACKET_UNION=lg_wall   the Command wall card reaches the whole racket (the left wall fell black)
#   KQ_ONE_RACKET_ASIS=lg_streak  the glossy-only diagonal streak keeps its face/back links (on the round Naked handle it
#                                 drew a seam line and a glint at the throat join)
#   KQ_ONE_RACKET_KEEP=holes,throat,bridgewall  those parts keep their authored links (Pace bores caught the widened rim
#                                 strips as silver beads, the Pace bridge a white bar; "exclude the bore surfaces")
# Previews previews/wf/k11-sc, k11-sp2, k07-row, k08-feels. Runs fw-cmdlift.sh (K11 Command, K08, K07; K09 kept) and
# fw-pacefix.sh (K11 Pace; K09 Pace kept). Previous files move to pre-fix2-20261114. Not while one-racket.sh runs.
set -u
cd "$(dirname "$0")"
export KQ_RENDER_OUT=${KQ_RENDER_OUT:-$HOME/kinetiq-render/out}
export FW_R=one-racket FW_RT=2026-11-13T19:20:23Z
export FW_OLD=$KQ_RENDER_OUT/out/final/pre-fix2-20261114
export FW_CANON="one-racket canon (one racket, one material, one light: every light that reaches the racket reaches all of it; whole-frame renders only), with the cloud review 19:20Z: the wall card reaches the whole racket, the face's glossy streak stays on the face, the bores, throat and bridge wall keep their own light"
export KQ_ONE_RACKET_UNION=lg_wall KQ_ONE_RACKET_ASIS=lg_streak KQ_ONE_RACKET_KEEP=holes,throat,bridgewall
mkdir -p "$FW_OLD"
DONE=$KQ_RENDER_OUT/logs/queue-nov3.done
L=$KQ_RENDER_OUT/logs/one-racket.log
CL=$KQ_RENDER_OUT/logs/one-racket.cleared
log() { echo "$(date -u +%FT%TZ) $*" >> "$L"; }
if ! grep -qxF fix2 "$CL"; then
  cp "$DONE" "$DONE.pre-fix2"
  n0=$(wc -l < "$DONE")
  grep -vE '^(cl (aside|m|status) K(11|08|07)-|pf (aside|m|status) K11-)' "$DONE" > "$DONE.tmp"; mv "$DONE.tmp" "$DONE"
  echo fix2 >> "$CL"; log "cleared fix2: $((n0 - $(wc -l < "$DONE"))) markers"
fi
rc=0
for s in fw-cmdlift.sh fw-pacefix.sh; do
  log "START fix2 $s"
  ./$s >> "$L" 2>&1; r=$?; [ $r = 0 ] || rc=1
  log "END fix2 $s rc=$r"
done
exit $rc
