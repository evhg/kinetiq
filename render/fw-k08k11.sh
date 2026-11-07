#!/usr/bin/env bash
# fw-k08k11.sh: full-weave pass, K08 (the two feels, left Command, right Pace; grip and Naked, 5120 spp 96 --crops) and
# K11 (single both feels, pair both weaves; grip and Naked, 5120 spp 256), the queue-nov3b / req-naked-handles recipes.
# Naked twins: the handle card on (KQ_PACE_HANDLE=1: k789 render_main, PH_K789, Pace necks only; the butt left out).
. "$(cd "$(dirname "$0")" && pwd)/fw-lib.sh"
NGH="env KQ_NOGRIP=1 KQ_PACE_HANDLE=1"
NG15H="env KQ_NOGRIP=1 KQ_EDGE_MM=1.5 KQ_PACE_HANDLE=1"
log "FW-START K08 K11 device $KQ_DEVICE free $(free_mb) MB push $PUSH"
# ---- K08
if ! held k08 && ! done_mark "fw status k08"; then
  t0=$(date +%s)
  aside k08 "$V"/K08-feel-pair{,-nogrip}{.png,_left.png,_right.png,_masks.json}
  still fw-K08 "$V/K08-feel-pair.png" - -- $PY shots/K08-feel-pair.py --w 5120 --h 2880 --spp 96 --crops --out final/v5k/K08-feel-pair
  still fw-K08n "$V/K08-feel-pair-nogrip.png" - -- $NGH $PY shots/K08-feel-pair.py --w 5120 --h 2880 --spp 96 --crops --out final/v5k/K08-feel-pair-nogrip
  need "$V"/K08-feel-pair{,-nogrip}.png || exit 1
  echo "k08 $(( $(date +%s) - t0 ))" >> "$LOGD/full-weave.times"
  if [ "$PUSH" = 1 ]; then
    masters "fw m k08" stills/K07-K08 "K08 5120x2880 grip and Naked, $R ($CANON)" "$V"/K08-feel-pair{,-nogrip}{.png,_masks.json}
    done_mark "fw m k08" || exit 1
    tt=$(awk '$1=="k08"{v=$2}END{print v+0}' "$LOGD/full-weave.times")
    st "fw status k08" "$(date -u +%FT%TZ) $R:K08 stills/K07-K08/K08-feel-pair{,-nogrip}{.png,_masks.json} $(hm $tt) $DEVNAME K08 grip and Naked (left Command, right Pace) whole 5120x2880 spp 96 --crops, same camera and crops, with the $CANON; render time this run"
  fi
fi
# ---- K11
if ! held k11 && ! done_mark "fw status k11"; then
  t0=$(date +%s)
  aside k11 "$V"/K11-{single,single-pace,single-nogrip,single-nogrip-pace,pair-command,pair-pace,pair-nogrip-command,pair-nogrip-pace}{.png,_card.png,_view.png,_masks.json}
  still fw-K11s   "$V/K11-single.png"              - -- $PY shots/K11-single.py --w 5120 --h 2880 --spp 256 --out final/v5k/K11-single
  still fw-K11sp  "$V/K11-single-pace.png"         - -- $PY shots/K11-single.py --feel pace --w 5120 --h 2880 --spp 256 --out final/v5k/K11-single-pace
  still fw-K11sn  "$V/K11-single-nogrip.png"       - -- $NG15H $PY shots/K11-single.py --w 5120 --h 2880 --spp 256 --out final/v5k/K11-single-nogrip
  still fw-K11snp "$V/K11-single-nogrip-pace.png"  - -- $NG15H $PY shots/K11-single.py --feel pace --w 5120 --h 2880 --spp 256 --out final/v5k/K11-single-nogrip-pace
  still fw-K11pc  "$V/K11-pair-command.png"        - -- $PY shots/K11-pair.py --weave command --w 5120 --h 2880 --spp 256 --out final/v5k/K11-pair-command
  still fw-K11pp  "$V/K11-pair-pace.png"           - -- $PY shots/K11-pair.py --weave pace --w 5120 --h 2880 --spp 256 --out final/v5k/K11-pair-pace
  still fw-K11pnc "$V/K11-pair-nogrip-command.png" - -- $NG15H $PY shots/K11-pair.py --weave command --w 5120 --h 2880 --spp 256 --out final/v5k/K11-pair-nogrip-command
  still fw-K11pnp "$V/K11-pair-nogrip-pace.png"    - -- $NG15H $PY shots/K11-pair.py --weave pace --w 5120 --h 2880 --spp 256 --out final/v5k/K11-pair-nogrip-pace
  K11F=$(for s in single single-pace single-nogrip single-nogrip-pace pair-command pair-pace pair-nogrip-command pair-nogrip-pace; do echo "$V/K11-$s.png"; done)
  need $K11F || exit 1
  echo "k11 $(( $(date +%s) - t0 ))" >> "$LOGD/full-weave.times"
  if [ "$PUSH" = 1 ]; then
    masters "fw m k11" stills/K11 "K11 5120x2880 single (both feels) and pair (both weaves), grip and Naked, $R ($CANON)" $K11F $(ls "$V"/K11-*_masks.json "$V"/K11-*_card.png "$V"/K11-*_view.png 2>/dev/null)
    done_mark "fw m k11" || exit 1
    tt=$(awk '$1=="k11"{v=$2}END{print v+0}' "$LOGD/full-weave.times")
    st "fw status k11" "$(date -u +%FT%TZ) $R:K11 stills/K11/K11-{single,single-pace,single-nogrip,single-nogrip-pace,pair-command,pair-pace,pair-nogrip-command,pair-nogrip-pace}.png (+ _card, _view, _masks) $(hm $tt) $DEVNAME K11 single (Command, Pace) and pair (command, pace weave), grip and Naked, whole 5120x2880 spp 256 (Naked KQ_EDGE_MM 1.5 as before), same cameras and framing, with the $CANON; the grip twins now at 5120 too; render time this run"
  fi
fi
log "FW-DONE K08 K11"
