#!/usr/bin/env bash
# fw-gripedge.sh (2026-11-08, the Mac render node): cloud REQUEST grip-edge (07:39Z, on Release 13 live): the black
# overgrips of the dark-look renders drew a bright white jagged line down one side (K11-dark grip_dark's thin back
# strip catching the helical wrap's edges as a staircase). Now: no back strip (GRIP_RIM_S 0), the side strip broad and
# dim (35 x 70 cm, 1.5 W): the wrap reads as soft charcoal bands, the far side falls dark, the cap keeps its satin
# highlight; K09's GripStrip widened to a soft sheen (GRIP_W 0.30). Grip twins only (the Naked twins have no overgrip),
# same cameras, crops, spp, base and full. One STATUS line per item. Resumable (markers "ge ..."); the previous files go
# to $F/pre-gripedge once.
. "$(cd "$(dirname "$0")" && pwd)/fw-lib.sh"
R=grip-edge
OLDF=$F/pre-gripedge
mkdir -p "$OLDF"
K9SET="GRIP_W=${GE_K9W:-0.30},GRIP_E=${GE_K9E:-1}"
FIX="the overgrip's silhouette soft (grip-edge: no back strip, a broad dim side strip, 35 x 70 cm at 1.5 W, linked to the overgrip alone: the wrap as soft charcoal bands, nothing brighter than the face's shade, the far side falling dark; the cap's satin highlight kept)"
log "GE-START device $KQ_DEVICE free $(free_mb) MB push $PUSH"
aside_f() { local m="ge aside $1"; shift; done_mark "$m" && return 0; local f; for f in "$@"; do [ -e "$f" ] && mv "$f" "$OLDF"/; done; mark "$m"; }
# k11 <stem> <what> <args...>
k11() {
  local stem=$1 what=$2; shift 2
  done_mark "ge status $stem" && return 0
  aside_f "$stem" "$V/$stem"-{base,full}{,_card}.png "$V/$stem.exr"
  local t0=$(date +%s)
  still "ge-$stem" "$V/$stem-full_card.png" - -- $PY shots/K11-dark.py "$@" --w 5120 --h 2880 --spp 256 --out "final/v5k/$stem"
  need "$V/$stem"-{base,full}{,_card}.png || return 1
  local tt=$(( $(date +%s) - t0 ))
  [ "$PUSH" = 1 ] || { log "PUSH=0: $stem rendered, not pushed"; return 0; }
  masters "ge m $stem" stills/K11 "K11 $what, $R base + full, 5120x2880 + card" "$V/$stem"-{base,full}{,_card}.png
  done_mark "ge m $stem" || return 1
  st "ge status $stem" "$(date -u +%FT%TZ) $R:$stem stills/K11/$stem-{base,full}{,_card}.png $(hm $tt) $DEVNAME K11 $what, the k04-language-fix render again with $FIX; same camera and card crop, 5120x2880 spp 256, base + full from one render; with the $CANON; render time this run"
}
# row <stem> <mode> <what> [extra suffixes]
row() {
  local stem=$1 mode=$2 what=$3; shift 3
  local sfx=("$@")
  done_mark "ge status $stem" && return 0
  local files=("$V/$stem"-{base,full}.png)
  local s; for s in "${sfx[@]}"; do files+=("$V/$stem"-{base,full}"$s".png); done
  aside_f "$stem" "${files[@]}" "$V/$stem.exr"
  local t0=$(date +%s)
  still "ge-$stem" "$V/$stem-full.png" - -- $PY shots/Kdark_row.py --mode "$mode" --w 5120 --h 2880 --spp 160 --out "final/v5k/$stem"
  need "${files[@]}" || return 1
  local tt=$(( $(date +%s) - t0 ))
  [ "$PUSH" = 1 ] || { log "PUSH=0: $stem rendered, not pushed"; return 0; }
  masters "ge m $stem" stills/K07-K08 "$what, $R base + full, 5120x2880" "${files[@]}"
  done_mark "ge m $stem" || return 1
  local list=$(for f in "${files[@]}"; do printf '%s/%s,' stills/K07-K08 "$(basename "$f")"; done | sed 's/,$//')
  st "ge status $stem" "$(date -u +%FT%TZ) $R:$stem $list $(hm $tt) $DEVNAME $what, the k04-language-fix render again with $FIX; same camera, 5120x2880 spp 160, base + full from one render; with the $CANON; render time this run"
}
# k9 <stem> <variant> <feel> <w> <h> <what>
k9() {
  local stem=$1 var=$2 fe=$3 w=$4 h=$5 what=$6
  done_mark "ge status $stem" && return 0
  local files=("$V/$stem"-{base,full}.png)
  [ "$var" = card ] && files+=("$V/$stem"-hover-{base,full}.png)
  aside_f "$stem" "${files[@]}" "$V/$stem.exr"
  local t0=$(date +%s)
  still "ge-$stem" "$V/$stem-full.png" - -- $PY shots/K09-dark.py --variant "$var" --feel "$fe" --w "$w" --h "$h" --spp 160 --out "final/v5k/$stem" --set "$K9SET"
  need "${files[@]}" || return 1
  local tt=$(( $(date +%s) - t0 ))
  [ "$PUSH" = 1 ] || { log "PUSH=0: $stem rendered, not pushed"; return 0; }
  masters "ge m $stem" stills/K09 "K09 $what, $R base + full, ${w}x$h" "${files[@]}"
  done_mark "ge m $stem" || return 1
  local list=$(for f in "${files[@]}"; do printf '%s/%s,' stills/K09 "$(basename "$f")"; done | sed 's/,$//')
  st "ge status $stem" "$(date -u +%FT%TZ) $R:$stem $list $(hm $tt) $DEVNAME K09 $what, the k09-dark render again with the overgrips' GripStrip widened ($K9SET: a soft sheen along each wrap instead of a row of bright dashes); ${w}x$h spp 160, same camera and frame, base + full$( [ "$var" = card ] && echo ' + hover' ) from one render; with the $CANON; render time this run"
}
k11 K11-single       "single Command, grip"          --mode single --feel command || exit 1
k11 K11-single-pace  "single Pace, grip"             --mode single --feel pace    || exit 1
k11 K11-pair-command "First 500 pair, Command, grip" --mode pair --weave command  || exit 1
k11 K11-pair-pace    "First 500 pair, Pace, grip"    --mode pair --weave pace     || exit 1
row K08-feel-pair   feels "K08 the two feels (Command KQ-000427 left, Pace KQ-000428 right), grip" _left _right || exit 1
row K07-lineup-five row   "K07 the Identical lineup (KQ-000427..431), grip" || exit 1
G=K09-case-three
k9 "$G-gallery"      gallery command 2400 1800 "case of three, gallery 4:3, Command, grip" || exit 1
k9 "$G-card"         card    command 1440 1800 "case of three, card 4:5, Command, grip"    || exit 1
k9 "$G-gallery-pace" gallery pace    2400 1800 "case of three, gallery 4:3, Pace, grip"    || exit 1
k9 "$G-card-pace"    card    pace    1440 1800 "case of three, card 4:5, Pace, grip"       || exit 1
log "GE-DONE"
