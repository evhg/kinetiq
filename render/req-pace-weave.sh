#!/usr/bin/env bash
# req-pace-weave.sh (2026-11-06, the Mac render node): cloud REQUEST pace-naked-weave (2026-11-06T12:15:33Z, owner: "make
# the Pace weave visible on the handle too"). With light, not material: k789_lib.pace_handle_weave() adds a soft graded
# card to every Pace Naked racket, placed above the handle's own mirror direction as the face's weave cards sit above
# the face's (the coat cannot see it, the 12K fibre lobes can: alternate tapes light up down to the Q band), linked to
# the neck only (its top strip at the face junction split off and left out: it drew a line that read as a joint). It
# turns with the racket, so a swivel's frame 0 is still the still. Per camera: K01 12 deg (PH_UP), k789 20 deg up and
# 30 deg round the handle (PH_K789); the rest is tuned and added here one shot at a time (STATUS NOTE 12:58).
# Items: K01 Naked Pace stills (beam base/full/finale 5120, phone 2160x3840) and its two swivels (36 frames each, the
# p2d recipe), pushed to stills/K01 and sequences/; one STATUS line per item. PUSH=0 renders only.
#   nohup caffeinate -dimsu render/req-pace-weave.sh >> ~/kinetiq-render/out/logs/queue-mac.log 2>&1 &
if [ "${BASH_VERSINFO[0]}" -lt 5 ] && [ -x /opt/homebrew/bin/bash ]; then exec /opt/homebrew/bin/bash "$0" "$@"; fi
export KQ_RENDER_OUT=${KQ_RENDER_OUT:-$HOME/kinetiq-render/out}
export KQ_LOCK=${KQ_LOCK:-$HOME/kinetiq-render/render.lock}
export RENDER_ROOT=${RENDER_ROOT:-$(cd "$(dirname "$0")" && pwd)}
export KQ_DEVICE=${KQ_DEVICE:-METAL}
export KQ_NO_EXPORT=1
QNAME=queue-mac
. "$(cd "$(dirname "$0")" && pwd)/queue_lib.sh"
DEVNAME="M3Max-$KQ_DEVICE"
PUSH=${PUSH:-1}
R=pace-naked-weave RT=2026-11-06T12:15:33Z
P1C="0.20 0.82 0.48 0.95"   # K01 portrait region (queue-mac.sh)
D1C="0.27 0.73 0.19 1.0"    # K01 desktop region
PACE="--feel pace --set P_FOLLOW=0.85"
RIG="handle weave card (k789_lib.pace_handle_weave: a soft graded 2.2 x 1.8 m card, strength 10, 6500 K, 1.4 m, above the handle's own mirror direction as the face's weave cards sit above the face's, linked to the neck only, the neck's junction strip left out; it turns with the racket), material, samples, seeds, denoiser and every other light unchanged, K01's two hairlines kept"
hm() { printf '%dh%02dm' $(($1 / 3600)) $(($1 % 3600 / 60)); }
st() {   # st <marker> <line>
  done_mark "$1" && return 0
  if "$KIT/status_push.sh" "$2" >> "$LOGD/status.log" 2>&1; then mark "$1"; log "STATUS $1 ok: ${2:0:160}"
  else log "ERROR $1 (see $LOGD/status.log)"; return 1; fi
}
log "REQ-START $R device $KQ_DEVICE free $(free_mb) MB push $PUSH"

# ---------------------------------------------------------------- K01 (stills + swivels, the p2d recipe)
beam=K01-hero-beam-nogrip-pace-v5k phone=K01-hero-frame-phone-nogrip-pace-v5k sq=K01-swivel-nogrip-pace
OLD=$F/pre-weave-20261106
if ! done_mark "weave k01 moved old"; then   # the p2d stills and swivels (4 Nov) aside, once; their seqmasters markers off
  mkdir -p "$OLD"
  for f in "$F/$beam"-{base,full,finale}.png "$F/$phone"-{base,full}.png; do [ -e "$f" ] && mv "$f" "$OLD"/; done
  for n in phone desktop; do [ -d "$S/$sq-$n" ] && mv "$S/$sq-$n" "$OLD/"; done
  sed -i '' "/^seqmasters $sq-phone\$/d; /^seqmasters $sq-desktop\$/d" "$DONE"
  mark "weave k01 moved old"
fi
t0=$(date +%s)
still "K01-beam-weave" "$F/$beam-finale.png" "$F/passes/$beam" -- $PY shots/K01-hero-beam.py --feel pace --set NOGRIP=1 --w 5120 --h 2880 --spp 64 --out "final/$beam"
still "K01-phone-weave" "$F/$phone-full.png" "$F/passes/$phone" -- $PY shots/K01-hero-frame.py --feel pace --set NOGRIP=1 --w 2160 --h 3840 --spp 48 --out "final/$phone"
[ -f "$F/$beam-finale.png" ] && [ -f "$F/$phone-full.png" ] || { log "REQ-FAIL K01 stills missing"; exit 1; }
seq "$sq-phone" 36 $P1C "$F/$phone-full.png" -- $PY shots/K01-hero-frame.py $PACE --set NOGRIP=1 --w 2160 --h 3840 --spp 24 --seq 36 --yaw-range 0 35 --crop $P1C --out "seq4/$sq-phone"
seq "$sq-desktop" 36 $D1C "$F/$beam-full.png" -- $PY shots/K01-hero-beam.py $PACE --set NOGRIP=1 --w 5120 --h 2880 --spp 16 --seq 36 --yaw-range 0 35 --crop $D1C --out "seq4/$sq-desktop"
n_ok() { ls "$S/$1" 2>/dev/null | grep -c '^f[0-9]*\.png$'; }
[ "$(n_ok "$sq-phone")" -ge 36 ] && [ "$(n_ok "$sq-desktop")" -ge 36 ] || { log "REQ-FAIL K01 swivels incomplete"; exit 1; }
echo "k01 $(( $(date +%s) - t0 ))" >> "$LOGD/req-pace-weave.times"
log "REQ-RENDERS-DONE K01 free $(free_mb) MB"
[ "$PUSH" = 1 ] || { log "PUSH=0: stop before pushing"; exit 0; }
masters "m-weave-k01" stills/K01 "K01 Naked Pace: the handle weave card (request $R), 5120 beam base/full/finale, 2160 portrait" "$F/$beam"-{base,full,finale}.png "$F/$phone"-{base,full}.png
done_mark "m-weave-k01" || exit 1
seq_masters "$sq-phone" $P1C
seq_masters "$sq-desktop" $D1C
done_mark "seqmasters $sq-phone" && done_mark "seqmasters $sq-desktop" || exit 1
tt=$(awk '$1=="k01"{v=$2}END{print v+0}' "$LOGD/req-pace-weave.times")
st "status weave-k01" "$(date -u +%FT%TZ) $R:K01 stills/K01/$beam-{base,full,finale}.png,stills/K01/$phone-{base,full}.png,sequences/$sq-phone,sequences/$sq-desktop $(hm $tt) $DEVNAME K01 Naked Pace, the p2d recipe (beam 5120 spp 64, portrait 2160x3840 spp 48, swivels 36 frames each, P_FOLLOW 0.85, frame 0 = the -full still) with the $RIG; mean handle luma 12.6 -> 39.3 at 2560 (the preview); face unchanged (mean |dLuma| 0.6); render time this run" || exit 1
log "REQ-ITEM-DONE K01 $R"
