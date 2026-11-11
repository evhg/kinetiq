#!/usr/bin/env bash
# fw-cmdlift.sh (2026-11-11, the Mac render node): cloud REQUEST command-dark-lift, OK'd 09:58Z on the PREVIEW (with the
# hole fix: a thin warm ring just inside each lip, about half strength on Command, dark centres as in the K01 hero). Every
# held whole-racket Command item: K11 single and pair, K08 and K07 (Command and Pace in one frame: Pace with the
# pace-dark-fix and the Kdark_row -20 deg graded card), K09 Command; grip and Naked; base and full. Same cameras, crops
# and spp as the k04-language masters. One STATUS line per item. Resumable (markers "cl ..."); the previous files go to
# $F/pre-cmdlift once.
. "$(cd "$(dirname "$0")" && pwd)/fw-lib.sh"
R=command-dark-lift
OLDF=$F/pre-cmdlift
mkdir -p "$OLDF"
NAKED="the Naked twin (canon Naked, no butt flare)"
NGK="KQ_NOGRIP=1 KQ_NAKED_FLARE=0 KQ_PACE_HANDLE=1"
LIFT="the command-dark-lift as OK'd 09:58Z: the white 3K face reads white across its whole width (key x 0.3, sheen x 0.4, a broad soft diffuse-only fill card toward the shaded half and one soft diagonal glossy-only sheen streak at the face's mirror direction, each linked to the Command racket alone; the shade side a soft light grey); the bore glow a thin warm ring just inside each lip at half strength, dark centres; no throat glow"
PFX="the Pace racket(s) with the pace-dark-fix as OK'd 09:12Z (the graded card here -20 deg off the mirror direction, the 12K tapes less anisotropic, copper lip rings, no throat glow)"
log "CL-START device $KQ_DEVICE free $(free_mb) MB push $PUSH"
aside_f() { local m="cl aside $1"; shift; done_mark "$m" && return 0; local f; for f in "$@"; do [ -e "$f" ] && mv "$f" "$OLDF"/; done; mark "$m"; }
k11() {
  local stem=$1 what=$2 ev=$3 fx=$4; shift 4
  done_mark "cl status $stem" && return 0
  aside_f "$stem" "$V/$stem"-{base,full}{,_card}.png "$V/$stem.exr"
  local t0=$(date +%s) envs=()
  [ "$ev" != "-" ] && envs=(env $ev)
  still "cl-$stem" "$V/$stem-full_card.png" - -- "${envs[@]}" $PY shots/K11-dark.py "$@" --w 5120 --h 2880 --spp 256 --out "final/v5k/$stem"
  need "$V/$stem"-{base,full}{,_card}.png || return 1
  local tt=$(( $(date +%s) - t0 ))
  [ "$PUSH" = 1 ] || { log "PUSH=0: $stem rendered, not pushed"; return 0; }
  masters "cl m $stem" stills/K11 "K11 $what, $R base + full, 5120x2880 + card" "$V/$stem"-{base,full}{,_card}.png
  done_mark "cl m $stem" || return 1
  st "cl status $stem" "$(date -u +%FT%TZ) $R:$stem stills/K11/$stem-{base,full}{,_card}.png $(hm $tt) $DEVNAME K11 $what, re-rendered with $LIFT$fx; turned 25 deg as in the PREVIEW; same card crop, 5120x2880 spp 256, base + full from one render; with the $CANON; render time this run"
}
row() {
  local stem=$1 mode=$2 what=$3 ev=$4; shift 4
  local sfx=("$@")
  done_mark "cl status $stem" && return 0
  local files=("$V/$stem"-{base,full}.png) s
  for s in "${sfx[@]}"; do files+=("$V/$stem"-{base,full}"$s".png); done
  aside_f "$stem" "${files[@]}" "$V/$stem.exr"
  local t0=$(date +%s) envs=()
  [ "$ev" != "-" ] && envs=(env $ev)
  still "cl-$stem" "$V/$stem-full.png" - -- "${envs[@]}" $PY shots/Kdark_row.py --mode "$mode" --w 5120 --h 2880 --spp 160 --out "final/v5k/$stem"
  need "${files[@]}" || return 1
  local tt=$(( $(date +%s) - t0 ))
  [ "$PUSH" = 1 ] || { log "PUSH=0: $stem rendered, not pushed"; return 0; }
  masters "cl m $stem" stills/K07-K08 "$what, $R + pace-dark-fix base + full, 5120x2880" "${files[@]}"
  done_mark "cl m $stem" || return 1
  local list=$(for f in "${files[@]}"; do printf '%s/%s,' stills/K07-K08 "$(basename "$f")"; done | sed 's/,$//')
  st "cl status $stem" "$(date -u +%FT%TZ) $R:$stem $list $(hm $tt) $DEVNAME $what, re-rendered: the Command racket(s) with $LIFT (the fill mirrored for a racket keyed from its other side); $PFX; every racket its own light set linked to it alone; same camera and crops, 5120x2880 spp 160, base + full from one render; with the $CANON; render time this run"
}
k9() {
  local stem=$1 var=$2 w=$3 h=$4 what=$5 ev=$6
  done_mark "cl status $stem" && return 0
  local files=("$V/$stem"-{base,full}.png)
  [ "$var" = card ] && files+=("$V/$stem"-hover-{base,full}.png)
  aside_f "$stem" "${files[@]}" "$V/$stem.exr" "$V/${stem}_lg.exr"
  local t0=$(date +%s) envs=()
  [ "$ev" != "-" ] && envs=(env $ev)
  still "cl-$stem" "$V/$stem-full.png" - -- "${envs[@]}" $PY shots/K09-dark.py --variant "$var" --feel command --w "$w" --h "$h" --spp 160 --out "final/v5k/$stem" --set "GRIP_W=0.30,GRIP_E=1"
  need "${files[@]}" || return 1
  local tt=$(( $(date +%s) - t0 ))
  [ "$PUSH" = 1 ] || { log "PUSH=0: $stem rendered, not pushed"; return 0; }
  masters "cl m $stem" stills/K09 "K09 $what, $R base + full, ${w}x$h" "${files[@]}"
  done_mark "cl m $stem" || return 1
  local list=$(for f in "${files[@]}"; do printf '%s/%s,' stills/K09 "$(basename "$f")"; done | sed 's/,$//')
  st "cl status $stem" "$(date -u +%FT%TZ) $R:$stem $list $(hm $tt) $DEVNAME K09 $what, re-rendered with $LIFT (in the case: the rake per racket unchanged, the fill and streak in its key group); ${w}x$h spp 160, same camera and frame, base + full$( [ "$var" = card ] && echo ' + hover' ) from one render; with the $CANON; render time this run"
}
k11 K11-single                "single Command, grip"            -           ""                   --mode single --feel command  || exit 1
k11 K11-single-nogrip         "single Command, $NAKED"          KQ_NOGRIP=1 ""                   --mode single --feel command  || exit 1
k11 K11-pair-command          "First 500 pair, Command, grip"   -           "; 027/500 on both"  --mode pair --weave command   || exit 1
k11 K11-pair-nogrip-command   "First 500 pair, Command, $NAKED" KQ_NOGRIP=1 "; 027/500 on both"  --mode pair --weave command   || exit 1
row K08-feel-pair         feels "K08 the two feels (Command KQ-000427 left, Pace KQ-000428 right), grip" -           _left _right || exit 1
row K08-feel-pair-nogrip  feels "K08 the two feels, $NAKED"                                          KQ_NOGRIP=1 _left _right || exit 1
row K07-lineup-five        row  "K07 the Identical lineup (five canon rackets, Command / Pace alternating), grip" - || exit 1
row K07-lineup-five-nogrip row  "K07 the Identical lineup, $NAKED"                                    KQ_NOGRIP=1 || exit 1
G=K09-case-three
k9 "$G-gallery"        gallery 2400 1800 "case of three, gallery 4:3, Command, grip"   -      || exit 1
k9 "$G-card"           card    1440 1800 "case of three, card 4:5, Command, grip"      -      || exit 1
k9 "$G-gallery-nogrip" gallery 2400 1800 "case of three, gallery 4:3, Command, $NAKED" "$NGK" || exit 1
k9 "$G-card-nogrip"    card    1440 1800 "case of three, card 4:5, Command, $NAKED"    "$NGK" || exit 1
log "CL-DONE"
