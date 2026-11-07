#!/usr/bin/env bash
# fw-k04lang.sh (2026-11-07, the Mac render node): cloud REQUEST k04-language (owner: "make the whole racket renders look
# more like the moulded holes graphic including the animation"), OK'd on PREVIEW2 at 16:10Z: every K11 variant in K04's
# language (shots/K11-dark.py: near-black field, low raking key from the crown, coat crescents, 90 mm three-quarter
# camera; base = the raking light only, full = base + the 2700 K bore / throat / edge glow, one render), the full-weave
# canon, 5120x2880 spp 256 as today's K11, each with its 4:5 card crop (x 0.275 w 0.45). One STATUS line per variant.
# Runs beside the full-weave pass (each render takes the render lock in turn). Resumable (markers "k4l ...").
. "$(cd "$(dirname "$0")" && pwd)/fw-lib.sh"
R4=k04-language
NAKED="the Naked twin (canon Naked, no butt flare)"
log "K4L-START device $KQ_DEVICE free $(free_mb) MB push $PUSH"
# k11 <stem> <what> <env or -> <args...>
k11() {
  local stem=$1 what=$2 ev=$3; shift 3
  done_mark "k4l status $stem" && return 0
  local t0=$(date +%s) envs=()
  [ "$ev" != "-" ] && envs=(env $ev)
  still "k4l-$stem" "$V/$stem-full_card.png" - -- "${envs[@]}" $PY shots/K11-dark.py "$@" --w 5120 --h 2880 --spp 256 --out "final/v5k/$stem"
  need "$V/$stem"-{base,full}{,_card}.png || return 1
  local tt=$(( $(date +%s) - t0 ))
  echo "k4l-$stem $tt" >> "$LOGD/full-weave.times"
  [ "$PUSH" = 1 ] || { log "PUSH=0: $stem rendered, not pushed"; return 0; }
  masters "k4l m $stem" stills/K11 "K11 $what, $R4 base + full, 5120x2880 + card" "$V/$stem"-{base,full}{,_card}.png
  done_mark "k4l m $stem" || return 1
  st "k4l status $stem" "$(date -u +%FT%TZ) $R4:$stem stills/K11/$stem-{base,full}{,_card}.png $(hm $tt) $DEVNAME K11 $what in K04's language (shots/K11-dark.py, PREVIEW2 as OK'd 16:10Z; Pace: the back strips continuous on the neck, the handle's sides and the Q end), 5120x2880 spp 256, card crop x 0.275 w 0.45 (2304x2880, 4:5); base = the raking light only, full = base + the 2700 K glow in the bores and the throat and the warm edge line, one render, pixel-registered; with the $CANON; render time this run"
}
k11 K11-single                 "single Command, grip"            -           --mode single --feel command  || exit 1
k11 K11-single-nogrip          "single Command, $NAKED"          KQ_NOGRIP=1 --mode single --feel command  || exit 1
k11 K11-single-pace            "single Pace, grip"               -           --mode single --feel pace     || exit 1
k11 K11-single-nogrip-pace     "single Pace, $NAKED"             KQ_NOGRIP=1 --mode single --feel pace     || exit 1
k11 K11-pair-command           "First 500 pair, Command, grip"   -           --mode pair --weave command   || exit 1
k11 K11-pair-nogrip-command    "First 500 pair, Command, $NAKED" KQ_NOGRIP=1 --mode pair --weave command   || exit 1
k11 K11-pair-pace              "First 500 pair, Pace, grip"      -           --mode pair --weave pace      || exit 1
k11 K11-pair-nogrip-pace       "First 500 pair, Pace, $NAKED"    KQ_NOGRIP=1 --mode pair --weave pace      || exit 1
k11 K11-pair-mix               "pair, Command front and Pace behind, grip"   -           --mode pair --weave mix || exit 1
k11 K11-pair-nogrip-mix        "pair, Command front and Pace behind, $NAKED" KQ_NOGRIP=1 --mode pair --weave mix || exit 1
log "K4L-DONE K11"
