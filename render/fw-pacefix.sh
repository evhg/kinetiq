#!/usr/bin/env bash
# fw-pacefix.sh (2026-11-11, the Mac render node): cloud REQUEST pace-dark-fix, OK'd 09:12Z on the 09:09Z PREVIEW (with the
# grip twins' fix: a broad dim front card on the overgrip, the cap lit by the grip's own light). The Pace items only:
# command-dark-lift (09:25Z) HOLDs every Command render, so K08 and K07 (Command and Pace in one frame) wait for it too.
# K11 single and pair, K09 gallery and card; grip and Naked; base and full (K09 card + hover). Same cameras, crops and
# spp as the k04-language masters. One STATUS line per item. Resumable (markers "pf ..."); the previous files go to
# $F/pre-pacefix once.
. "$(cd "$(dirname "$0")" && pwd)/fw-lib.sh"
R=${FW_R:-pace-dark-fix}
OLDF=${FW_OLD:-$F/pre-pacefix}
mkdir -p "$OLDF"
NAKED="the Naked twin (canon Naked, no butt flare)"
NGK="KQ_NOGRIP=1 KQ_NAKED_FLARE=0 KQ_PACE_HANDLE=1"
FIX="the pace-dark-fix as OK'd 09:12Z: (a) a broad soft graded card along each Pace racket (glossy rays only, never seen, 20 deg off the face's mirror direction, falling from the crown to 25 % at the Q end): dark grey from crown to Q end, never black; the cool outline strips x 0.22, a soft rim; (b) the 12K tapes' fibre lobe less anisotropic (0.90 -> 0.60), roughness 0.16, coat 0.04, the old weave card x 0.6: grey to black tiles with a sheen; (c) the bore glow in a thin band inside each lip: copper rings round dark holes; (d) no throat glow"
GFIX="the grip fix (09:12Z): a broad dim front card on the overgrip alone (charcoal bands down the handle, still black) and the satin cap lit by the grip's own soft card (its highlight at the grip's level)"
log "PF-START device $KQ_DEVICE free $(free_mb) MB push $PUSH"
aside_f() { local m="pf aside $1"; shift; done_mark "$m" && return 0; local f; for f in "$@"; do [ -e "$f" ] && mv "$f" "$OLDF"/; done; mark "$m"; }
# k11 <stem> <what> <env or -> <extra text> <args...>
k11() {
  local stem=$1 what=$2 ev=$3 fx=$4; shift 4
  done_mark "pf status $stem" && return 0
  aside_f "$stem" "$V/$stem"-{base,full}{,_card}.png "$V/$stem.exr"
  local t0=$(date +%s) envs=()
  [ "$ev" != "-" ] && envs=(env $ev)
  still "pf-$stem" "$V/$stem-full_card.png" - -- "${envs[@]}" $PY shots/K11-dark.py "$@" --w 5120 --h 2880 --spp 256 --out "final/v5k/$stem"
  need "$V/$stem"-{base,full}{,_card}.png || return 1
  local tt=$(( $(date +%s) - t0 ))
  [ "$PUSH" = 1 ] || { log "PUSH=0: $stem rendered, not pushed"; return 0; }
  masters "pf m $stem" stills/K11 "K11 $what, $R base + full, 5120x2880 + card" "$V/$stem"-{base,full}{,_card}.png
  done_mark "pf m $stem" || return 1
  st "pf status $stem" "$(date -u +%FT%TZ) $R:$stem stills/K11/$stem-{base,full}{,_card}.png $(hm $tt) $DEVNAME K11 $what, re-rendered with $FIX$fx; same camera and card crop, 5120x2880 spp 256, base + full from one render; with the $CANON; render time this run"
}
# k9 <stem> <variant> <w> <h> <what> <env or ->
k9() {
  local stem=$1 var=$2 w=$3 h=$4 what=$5 ev=$6
  done_mark "pf status $stem" && return 0
  local files=("$V/$stem"-{base,full}.png)
  [ "$var" = card ] && files+=("$V/$stem"-hover-{base,full}.png)
  aside_f "$stem" "${files[@]}" "$V/$stem.exr" "$V/${stem}_lg.exr"
  local t0=$(date +%s) envs=()
  [ "$ev" != "-" ] && envs=(env $ev)
  still "pf-$stem" "$V/$stem-full.png" - -- "${envs[@]}" $PY shots/K09-dark.py --variant "$var" --feel pace --w "$w" --h "$h" --spp 160 --out "final/v5k/$stem" --set "GRIP_W=0.30,GRIP_E=1"
  need "${files[@]}" || return 1
  local tt=$(( $(date +%s) - t0 ))
  [ "$PUSH" = 1 ] || { log "PUSH=0: $stem rendered, not pushed"; return 0; }
  masters "pf m $stem" stills/K09 "K09 $what, $R base + full, ${w}x$h" "${files[@]}"
  done_mark "pf m $stem" || return 1
  local list=$(for f in "${files[@]}"; do printf '%s/%s,' stills/K09 "$(basename "$f")"; done | sed 's/,$//')
  st "pf status $stem" "$(date -u +%FT%TZ) $R:$stem $list $(hm $tt) $DEVNAME K09 $what, re-rendered with $FIX (in the case: the graded card 20 W at -20 deg, the lip glow x 0.35, seen almost down the bores); ${w}x$h spp 160, same camera and frame, base + full$( [ "$var" = card ] && echo ' + hover' ) from one render; with the $CANON; render time this run"
}
k11 K11-single-pace        "single Pace, grip"              -           "; $GFIX"                     --mode single --feel pace || exit 1
k11 K11-single-nogrip-pace "single Pace, $NAKED"            KQ_NOGRIP=1 ""                            --mode single --feel pace || exit 1
k11 K11-pair-pace          "First 500 pair, Pace, grip"     -           "; $GFIX; 027/500 on both"    --mode pair --weave pace  || exit 1
k11 K11-pair-nogrip-pace   "First 500 pair, Pace, $NAKED"   KQ_NOGRIP=1 "; 027/500 on both"           --mode pair --weave pace  || exit 1
G=K09-case-three
k9 "$G-gallery-pace"        gallery 2400 1800 "case of three, gallery 4:3, Pace, grip"   -      || exit 1
k9 "$G-card-pace"           card    1440 1800 "case of three, card 4:5, Pace, grip"      -      || exit 1
k9 "$G-gallery-nogrip-pace" gallery 2400 1800 "case of three, gallery 4:3, Pace, $NAKED" "$NGK" || exit 1
k9 "$G-card-nogrip-pace"    card    1440 1800 "case of three, card 4:5, Pace, $NAKED"    "$NGK" || exit 1
log "PF-DONE"
