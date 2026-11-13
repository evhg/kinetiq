#!/usr/bin/env bash
# one-racket-k07.sh (2026-11-14, the Mac render node): cloud REVIEW 2026-11-13T22:00Z: K07 approval withdrawn: the trio's
# second (Pace) racket's left wall showed an isolated patch of bright white zigzag tows (the widened rim strip). Re-render
# K07 base + full, grip and Naked, with KQ_ONE_RACKET_KEEP adding "pace:wall" (the Pace walls back to their authored dark,
# as K11 Pace and K08; the Command walls keep the lg_wall union of fix2). Own marker file (logs/k07keep.done), so it can
# run beside one-racket.sh / fw-k01.sh; one render at a time through render.lock as always. Previous files move to
# pre-k07keep-20261114. Run after K02 has rendered (cloud: "without delaying K02").
export KQ_RENDER_OUT=${KQ_RENDER_OUT:-$HOME/kinetiq-render/out}
export FW_R=one-racket FW_RT=2026-11-13T22:00:39Z
export FW_OLD=$KQ_RENDER_OUT/out/final/pre-k07keep-20261114
export FW_CANON="one-racket canon (one racket, one material, one light; whole-frame renders only), with the cloud reviews 19:20Z and 22:00Z: the Command wall card reaches the whole racket, the face's glossy streak stays on the face, the bores, throat and bridge keep their own light, and the Pace walls keep their own dark"
export KQ_ONE_RACKET_UNION=lg_wall KQ_ONE_RACKET_ASIS=lg_streak KQ_ONE_RACKET_KEEP=holes,throat,bridgewall,pace:wall
# fw-cmdlift.sh (2026-11-11, the Mac render node): cloud REQUEST command-dark-lift, OK'd 09:58Z on the PREVIEW (with the
# hole fix: a thin warm ring just inside each lip, about half strength on Command, dark centres as in the K01 hero). Every
# held whole-racket Command item: K11 single and pair, K08 and K07 (Command and Pace in one frame: Pace with the
# pace-dark-fix and the Kdark_row -20 deg graded card), K09 Command; grip and Naked; base and full. Same cameras, crops
# and spp as the k04-language masters. One STATUS line per item. Resumable (markers "cl ..."); the previous files go to
# $F/pre-cmdlift once.
. "$(cd "$(dirname "$0")" && pwd)/fw-lib.sh"
R=${FW_R:-command-dark-lift}
OLDF=${FW_OLD:-$F/pre-cmdlift}
mkdir -p "$OLDF"
NAKED="the Naked twin (canon Naked, no butt flare)"
NGK="KQ_NOGRIP=1 KQ_NAKED_FLARE=0 KQ_PACE_HANDLE=1"
LIFT="the command-dark-lift as OK'd 09:58Z: the white 3K face reads white across its whole width (key x 0.3, sheen x 0.4, a broad soft diffuse-only fill card toward the shaded half and one soft diagonal glossy-only sheen streak at the face's mirror direction, each linked to the Command racket alone; the shade side a soft light grey); the bore glow a thin warm ring just inside each lip at half strength, dark centres; no throat glow"
PFX="the Pace racket(s) with the pace-dark-fix as OK'd 09:12Z (the graded card here -20 deg off the mirror direction, the 12K tapes less anisotropic, copper lip rings, no throat glow)"
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
DONE=$KQ_RENDER_OUT/logs/k07keep.done; touch "$DONE"
log "K07KEEP-START device $KQ_DEVICE free $(free_mb) MB push $PUSH"
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
row K07-lineup-five        row  "K07 the Identical lineup (five canon rackets, Command / Pace alternating), grip" - || exit 1
row K07-lineup-five-nogrip row  "K07 the Identical lineup, $NAKED"                                    KQ_NOGRIP=1 || exit 1
log "K07KEEP-DONE"
