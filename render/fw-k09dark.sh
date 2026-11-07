#!/usr/bin/env bash
# fw-k09dark.sh (2026-11-07, the Mac render node): cloud REQUEST k04-language-fix (3) + k09-dark:REVIEW (22:20Z): K09
# (the One of Ten case of three) in K04's language, shots/K09-dark.py with the review's fixes (Command: the three
# per-racket crown rakes in front of the lid, all three white where lit; Pace: a thin cool outline on each edge radius
# and neck, the bore glow x 1.3; canon black overgrips), gallery 2400x1800 and card 1440x1800 at spp 160, grip and
# Naked, both feels, base and full from one render; the card also -hover-{base,full} (the lid group x 2.3, as the
# site's hover). One STATUS line per still. Runs beside the full-weave pass (the render lock takes turns). Resumable
# (markers "k9d ...").
. "$(cd "$(dirname "$0")" && pwd)/fw-lib.sh"
R4=k04-language-fix
NGK="KQ_NOGRIP=1 KQ_NAKED_FLARE=0 KQ_PACE_HANDLE=1"
log "K9D-START device $KQ_DEVICE free $(free_mb) MB push $PUSH"
# k9 <stem> <variant> <feel> <w> <h> <what> <env or ->
k9() {
  local stem=$1 var=$2 fe=$3 w=$4 h=$5 what=$6 ev=$7
  done_mark "k9d status $stem" && return 0
  local t0=$(date +%s) envs=()
  [ "$ev" != "-" ] && envs=(env $ev)
  local files=("$V/$stem"-{base,full}.png)
  [ "$var" = card ] && files+=("$V/$stem"-hover-{base,full}.png)
  still "k9d-$stem" "$V/$stem-full.png" - -- "${envs[@]}" $PY shots/K09-dark.py --variant "$var" --feel "$fe" --w "$w" --h "$h" --spp 160 --out "final/v5k/$stem"
  need "${files[@]}" || return 1
  local tt=$(( $(date +%s) - t0 ))
  echo "k9d-$stem $tt" >> "$LOGD/full-weave.times"
  [ "$PUSH" = 1 ] || { log "PUSH=0: $stem rendered, not pushed"; return 0; }
  masters "k9d m $stem" stills/K09 "K09 $what, k04-language base + full, ${w}x$h" "${files[@]}"
  done_mark "k9d m $stem" || return 1
  local list=$(for f in "${files[@]}"; do printf '%s/%s,' stills/K09 "$(basename "$f")"; done | sed 's/,$//')
  st "k9d status $stem" "$(date -u +%FT%TZ) $R4:$stem $list $(hm $tt) $DEVNAME K09 $what in K04's language (shots/K09-dark.py: the 22:18Z preview with the 22:20Z review's fixes: Command three identical crown rakes, each white where lit, falling to shade at the throat; Pace a thin cool outline on each edge radius and neck, glow x 1.3; canon black overgrips), ${w}x$h spp 160, the same camera and frame as K09; base = no glow, full = base + the 2700 K glow in the bores, the throat and the edge line, one render$( [ "$var" = card ] && echo '; -hover = the lid LED group x 2.3, as the site hover' ); with the $CANON; render time this run"
}
G=K09-case-three
for fe in command pace; do
  sfx=""; [ $fe = pace ] && sfx=-pace
  fn="Command"; [ $fe = pace ] && fn="Pace"
  k9 "$G-gallery$sfx"        gallery $fe 2400 1800 "case of three, gallery 4:3, $fn, grip"  -      || exit 1
  k9 "$G-card$sfx"           card    $fe 1440 1800 "case of three, card 4:5, $fn, grip"     -      || exit 1
  k9 "$G-gallery-nogrip$sfx" gallery $fe 2400 1800 "case of three, gallery 4:3, $fn, the Naked twins (canon Naked, no butt flare)" "$NGK" || exit 1
  k9 "$G-card-nogrip$sfx"    card    $fe 1440 1800 "case of three, card 4:5, $fn, the Naked twins (canon Naked, no butt flare)"    "$NGK" || exit 1
done
log "K9D-DONE"
