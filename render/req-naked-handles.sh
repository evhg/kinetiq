#!/usr/bin/env bash
# req-naked-handles.sh (2026-11-05, the Mac render node): answers two cloud requests in STATUS-mac.md:
#   "2026-11-04T22:30:22Z REQUEST K11+k789-naked-handles": K11's Naked handles read as a pale grey matte sleeve
#     flaring into a collar; re-render K11-single (both feels) and K11-pair (command, pace) whole at 5120-class with
#     their cameras and crops, check the other k789 Naked twins (K07, K08, K09) and re-render any that shows it.
#   "2026-11-05T01:03:59Z REQUEST K08-naked-pace-handle": a stair-stepped white streak down the Pace Naked handle
#     and a bracket highlight above the Q; re-render the K08 Naked twin whole.
# Causes and fix (shots/k789_lib.py bare_handle_lights, naked_neck_hd; Naked twins only, grip-on renders unchanged):
#   the bare-handle card was seen in glossy rays (it lit alternate 8 mm tapes of the Pace fibre lobe = the staircase,
#   and mirrored in the butt's flare = the bright band read as a collar); the face's band card (Band*, K09 FaceSheen)
#   reached the neck and mirrored in the flare = the bracket. Now the card is diffuse only, K01's two grip hairlines
#   draw the corners, the band cards no longer reach Naked necks, and the bare handle gets the hero's HD weave.
# All whole renders (no patch). Masters: stills/K11, stills/K07-K08, stills/K09; STATUS line per item, DONE per request.
#   nohup caffeinate -dimsu render/req-naked-handles.sh >> ~/kinetiq-render/out/logs/queue-mac.log 2>&1 &
if [ "${BASH_VERSINFO[0]}" -lt 5 ] && [ -x /opt/homebrew/bin/bash ]; then exec /opt/homebrew/bin/bash "$0" "$@"; fi
export KQ_RENDER_OUT=${KQ_RENDER_OUT:-$HOME/kinetiq-render/out}
export KQ_LOCK=${KQ_LOCK:-$HOME/kinetiq-render/render.lock}
export RENDER_ROOT=${RENDER_ROOT:-$(cd "$(dirname "$0")" && pwd)}
export KQ_DEVICE=${KQ_DEVICE:-METAL}
export KQ_NO_EXPORT=1
QNAME=queue-mac
. "$(cd "$(dirname "$0")" && pwd)/queue_lib.sh"
DEVNAME="M3Max-$KQ_DEVICE"
V=$F/v5k
NG="env KQ_NOGRIP=1"
NG15="env KQ_NOGRIP=1 KQ_EDGE_MM=1.5"
R1=K11+k789-naked-handles R1T=2026-11-04T22:30:22Z
R2=K08-naked-pace-handle R2T=2026-11-05T01:03:59Z
FIX="k789 Naked fix 2026-11-05: bare-handle card diffuse only (it drew the Pace staircase and the flare band), K01's two grip hairlines on the corners, face band cards off the Naked neck (the bracket on the flare), the hero's HD weave on the bare handle"
hm() { printf '%dh%02dm' $(($1 / 3600)) $(($1 % 3600 / 60)); }
st() {   # st <marker> <line>
  done_mark "$1" && return 0
  if "$KIT/status_push.sh" "$2" >> "$LOGD/status.log" 2>&1; then mark "$1"; log "STATUS $1 ok: ${2:0:160}"
  else log "ERROR $1 (see $LOGD/status.log)"; return 1; fi
}
need() { local f; for f in "$@"; do [ -f "$f" ] || { log "REQ-FAIL $f missing"; return 1; }; done; }
log "REQ-START $R1 + $R2 device $KQ_DEVICE free $(free_mb) MB"
# yesterday's K07 / K08 Naked 5120 masters (before the fix) out of the way, once, so still() renders them again
OLD=$V/pre-naked-fix-20261104
if ! done_mark "naked-fix moved old"; then
  mkdir -p "$OLD"
  for f in "$V"/K07-lineup-five-nogrip* "$V"/K08-feel-pair-nogrip*; do [ -e "$f" ] && mv "$f" "$OLD"/; done
  mark "naked-fix moved old"
fi

# --- K08 (request 2) first: one still, both feels, 5120 like its grip-on twin (queue-nov3b p5f)
t0=$(date +%s)
still K08n-fix "$V/K08-feel-pair-nogrip.png" - -- $NG $PY shots/K08-feel-pair.py --w 5120 --h 2880 --spp 96 --crops --out final/v5k/K08-feel-pair-nogrip
need "$V/K08-feel-pair-nogrip.png" || exit 1
masters "m-fix-k08n" stills/K07-K08 "K08 Naked 5120x2880 whole re-render, Pace handle streak/bracket fixed ($FIX; request $R2)" "$V"/K08-feel-pair-nogrip{.png,_masks.json}
done_mark "m-fix-k08n" || exit 1
st "status fix-k08n" "$(date -u +%FT%TZ) $R2 stills/K07-K08/K08-feel-pair-nogrip{.png,_masks.json} $(hm $(( $(date +%s) - t0 ))) $DEVNAME K08 Naked (left Command, right Pace) whole 5120x2880 spp 96 --crops, same camera/crops; the streak and bracket came from the scene's lights, not a patch: $FIX; render time this run" || exit 1
st "done $R2" "$(date -u +%FT%TZ) DONE $R2 (request $R2T): stills/K07-K08/K08-feel-pair-nogrip.png" || exit 1

# --- K11 (request 1): single both feels, pair both weaves, 5120 x 2880 (16:9: same framing as the 3200 masters)
t0=$(date +%s)
still K11sn-fix "$V/K11-single-nogrip.png" - -- $NG15 $PY shots/K11-single.py --w 5120 --h 2880 --spp 256 --out final/v5k/K11-single-nogrip
still K11snp-fix "$V/K11-single-nogrip-pace.png" - -- $NG15 $PY shots/K11-single.py --feel pace --w 5120 --h 2880 --spp 256 --out final/v5k/K11-single-nogrip-pace
still K11pn-fix "$V/K11-pair-nogrip-command.png" - -- $NG15 $PY shots/K11-pair.py --weave command --w 5120 --h 2880 --spp 256 --out final/v5k/K11-pair-nogrip-command
still K11pnp-fix "$V/K11-pair-nogrip-pace.png" - -- $NG15 $PY shots/K11-pair.py --weave pace --w 5120 --h 2880 --spp 256 --out final/v5k/K11-pair-nogrip-pace
need "$V"/K11-single-nogrip{,-pace}.png "$V"/K11-pair-nogrip-{command,pace}.png || exit 1
masters "m-fix-k11n" stills/K11 "K11 Naked twins 5120x2880 whole re-render: single both feels, pair command/pace ($FIX; request $R1)" "$V"/K11-single-nogrip{,-pace}.png "$V"/K11-pair-nogrip-{command,pace}.png
done_mark "m-fix-k11n" || exit 1
st "status fix-k11n" "$(date -u +%FT%TZ) $R1:K11 stills/K11/K11-single-nogrip{,-pace}.png,stills/K11/K11-pair-nogrip-{command,pace}.png $(hm $(( $(date +%s) - t0 ))) $DEVNAME K11 Naked single (Command, Pace) and pair (command, pace) whole 5120x2880 spp 256, KQ_EDGE_MM=1.5, same cameras/framing (crops are fractions: K11 card x 0.275 w 0.45); export ids K11-nogrip-single{,-pace}, K11-nogrip-{command,pace}; $FIX; render time this run" || exit 1

# --- K07 (request 1, check): its Pace rackets showed the same staircase and bracket, Command a bright flare band
t0=$(date +%s)
still K07n-fix "$V/K07-lineup-five-nogrip.png" - -- $NG $PY shots/K07-lineup-five.py --w 5120 --h 2880 --spp 112 --seq --out final/v5k/K07-lineup-five-nogrip
need "$V/K07-lineup-five-nogrip.png" || exit 1
masters "m-fix-k07n" stills/K07-K08 "K07 Naked 5120x2880 whole re-render ($FIX; request $R1)" "$V/K07-lineup-five-nogrip.png"
done_mark "m-fix-k07n" || exit 1
st "status fix-k07n" "$(date -u +%FT%TZ) $R1:K07 stills/K07-K08/K07-lineup-five-nogrip.png $(hm $(( $(date +%s) - t0 ))) $DEVNAME K07 Naked whole 5120x2880 spp 112 (checked against K01 Naked: Pace staircase/bracket and the Command flare band, fixed); $FIX; render time this run" || exit 1

# --- K09 (request 1, check): its handles read as a grey sleeve, Pace with crossed lines on the flare; its own sizes
t0=$(date +%s)
G=K09-case-three
still K09gn-fix "$F/$G-gallery-nogrip.png" - -- $NG15 $PY shots/K09-case-three.py --variant gallery --w 2400 --h 1800 --spp 160 --out final/$G-gallery-nogrip
still K09cn-fix "$F/$G-card-nogrip.png" - -- $NG15 $PY shots/K09-case-three.py --variant card --hover-mix --w 1440 --h 1800 --spp 160 --out final/$G-card-nogrip
still K09gnp-fix "$F/$G-gallery-nogrip-pace.png" - -- $NG15 $PY shots/K09-case-three.py --feel pace --variant gallery --w 2400 --h 1800 --spp 160 --out final/$G-gallery-nogrip-pace
still K09cnp-fix "$F/$G-card-nogrip-pace.png" - -- $NG15 $PY shots/K09-case-three.py --feel pace --variant card --hover-mix --w 1440 --h 1800 --spp 160 --out final/$G-card-nogrip-pace
need "$F/$G"-{gallery,card}-nogrip{,-pace}.png || exit 1
k09=$(ls "$F/$G"-*nogrip*.png)
masters "m-fix-k09n" stills/K09 "K09 Naked gallery 2400x1800 and card 1440x1800, both feels, whole re-render ($FIX; request $R1)" $k09
done_mark "m-fix-k09n" || exit 1
st "status fix-k09n" "$(date -u +%FT%TZ) $R1:K09 $(for f in $k09; do printf 'stills/K09/%s,' "$(basename "$f")"; done | sed 's/,$//') $(hm $(( $(date +%s) - t0 ))) $DEVNAME K09 Naked gallery 2400x1800 and card 1440x1800 --hover-mix, both feels, spp 160, KQ_EDGE_MM=1.5, the grip-on twins' sizes/cameras (was a grey sleeve; Pace crossed lines on the flare); $FIX; render time this run" || exit 1
st "done $R1" "$(date -u +%FT%TZ) DONE $R1 (request $R1T): K11 stills/K11/K11-{single-nogrip{,-pace},pair-nogrip-{command,pace}}.png; checked K07, K08, K09 against K01 Naked and re-rendered all three (stills/K07-K08, stills/K09)" || exit 1
log "REQ-DONE $R1 + $R2 free $(free_mb) MB"
