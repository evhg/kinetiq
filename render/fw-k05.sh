#!/usr/bin/env bash
# fw-k05.sh: full-weave pass, K05 (laser scan, top-down) v7c rig at 5760x3240 spp 96, the four (Command, Pace, Naked
# twins; desktop + phone from one master each), the req-nov6.sh recipe; the 16-bit masters split in two halves (over
# GitHub's 100 MB limit, split_master.py). No handle card on K05 (seen from straight above it mirrors as a silver bar).
. "$(cd "$(dirname "$0")" && pwd)/fw-lib.sh"
W57=$F/w5760
args() { grep -v '^#' "$1" | tr '\n' ' '; }
A=$(args "$KIT/notes/k05-v7.args")
AP=$(args "$KIT/notes/k05-v7-pace.args")
log "FW-START K05 device $KQ_DEVICE free $(free_mb) MB push $PUSH"
done_mark "fw status k05" && { log "FW-SKIP K05 (done)"; exit 0; }
t0=$(date +%s)
aside k05 "$W57"/K05-laser-scan{,-pace,-nogrip,-nogrip-pace}{,-phone,-master,-master-a,-master-b}.png
still fw-K05c "$W57/K05-laser-scan.png" - -- $PY shots/K05-laser-scan.py $A --w 5760 --h 3240 --spp 96 --out final/w5760/K05-laser-scan
still fw-K05cn "$W57/K05-laser-scan-nogrip.png" - -- $NGF $PY shots/K05-laser-scan.py $A --w 5760 --h 3240 --spp 96 --out final/w5760/K05-laser-scan-nogrip
still fw-K05cp "$W57/K05-laser-scan-pace.png" - -- $PY shots/K05-laser-scan.py $AP --feel pace --w 5760 --h 3240 --spp 96 --out final/w5760/K05-laser-scan-pace
still fw-K05cnp "$W57/K05-laser-scan-nogrip-pace.png" - -- $NGF $PY shots/K05-laser-scan.py $AP --feel pace --w 5760 --h 3240 --spp 96 --out final/w5760/K05-laser-scan-nogrip-pace
need "$W57"/K05-laser-scan{,-pace,-nogrip,-nogrip-pace}{,-phone,-master}.png || exit 1
for v in "" -pace -nogrip -nogrip-pace; do
  m="$W57/K05-laser-scan$v-master.png"
  [ -f "${m%.png}-a.png" ] && [ -f "${m%.png}-b.png" ] || $PY split_master.py "$m" >> "$LOGD/full-weave.log" 2>&1 || { log "FW-FAIL split $m"; exit 1; }
done
echo "k05 $(( $(date +%s) - t0 ))" >> "$LOGD/full-weave.times"
[ "$PUSH" = 1 ] || { log "PUSH=0: K05 rendered, not pushed"; exit 0; }
masters "fw m k05" stills/K05 "K05 v7c 5760x3240, $R ($CANON): Command, Pace, Naked twins, desktop + phone, 16-bit masters in -a/-b halves" \
  "$W57"/K05-laser-scan{,-pace,-nogrip,-nogrip-pace}{,-phone,-master-a,-master-b}.png
done_mark "fw m k05" || exit 1
tt=$(awk '$1=="k05"{v=$2}END{print v+0}' "$LOGD/full-weave.times")
TL=$($PY "$KIT/k05_throat_luma.py" "$W57/K05-laser-scan.png" 2>/dev/null)
st "fw status k05" "$(date -u +%FT%TZ) $R:K05 stills/K05/K05-laser-scan{,-pace,-nogrip,-nogrip-pace}{,-phone,-master-a,-master-b}.png $(hm $tt) $DEVNAME K05 v7c 5760x3240 spp 96 (the req-nov6 rig and args, Naked without flare), desktop + phone from one master each, masters split losslessly in -a (rows 0-1799) / -b halves, with the $CANON; no handle card on K05 (from straight above the card mirrors as a silver bar); K05-throat folded in (Command only, notes/k05-v7.args): lw_card2, a soft diffuse-only spot from the handle side, lifts the wedge between the throat, the neck and the first holes: ${TL:-luma not measured} (display luma at 2560; v7c 124 against 157, neck 96); the laser tapers to 15 % over the last 3.5 mm before each hole lip so its pink halo stays off the lip; render time this run"
log "FW-DONE K05"
