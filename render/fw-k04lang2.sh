#!/usr/bin/env bash
# fw-k04lang2.sh (2026-11-07, the Mac render node): cloud REQUEST k04-language, OK'd 16:10Z, second half: K08 (the two
# feels) and K07 (the Identical lineup) in K11-dark's K04 language (shots/Kdark_row.py: K11-dark's materials, glow,
# field and compositing; every racket its own light set, linked to it alone), grip and Naked, base and full from one
# render, 5120x2880 spp 160; K08 also writes its page crops (_left x .025 w .40, _right x .575 w .40). One STATUS line
# per item. Runs after fw-k04lang.sh (K11) beside the full-weave pass. Resumable (markers "k4l ...").
. "$(cd "$(dirname "$0")" && pwd)/fw-lib.sh"
R4=k04-language
log "K4L2-START device $KQ_DEVICE free $(free_mb) MB push $PUSH"
# row <stem> <mode> <masters dir> <what> <env or -> [extra suffixes]
row() {
  local stem=$1 mode=$2 dir=$3 what=$4 ev=$5; shift 5
  local sfx=("$@")
  done_mark "k4l status $stem" && return 0
  local t0=$(date +%s) envs=()
  [ "$ev" != "-" ] && envs=(env $ev)
  still "k4l-$stem" "$V/$stem-full.png" - -- "${envs[@]}" $PY shots/Kdark_row.py --mode "$mode" --w 5120 --h 2880 --spp 160 --out "final/v5k/$stem"
  local files=("$V/$stem"-{base,full}.png)
  local s; for s in "${sfx[@]}"; do files+=("$V/$stem"-{base,full}"$s".png); done
  need "${files[@]}" || return 1
  local tt=$(( $(date +%s) - t0 ))
  echo "k4l-$stem $tt" >> "$LOGD/full-weave.times"
  [ "$PUSH" = 1 ] || { log "PUSH=0: $stem rendered, not pushed"; return 0; }
  masters "k4l m $stem" "$dir" "$what, $R4 base + full, 5120x2880" "${files[@]}"
  done_mark "k4l m $stem" || return 1
  local list=$(for f in "${files[@]}"; do printf '%s/%s,' "$dir" "$(basename "$f")"; done | sed 's/,$//')
  st "k4l status $stem" "$(date -u +%FT%TZ) $R4:$stem $list $(hm $tt) $DEVNAME $what in K04's language (shots/Kdark_row.py: K11-dark's look, PREVIEW2 as OK'd 16:10Z; every racket its own light set linked to it alone), 5120x2880 spp 160; base = the raking light only, full = base + the 2700 K glow in the bores and the throat and the warm edge line, one render, pixel-registered; with the $CANON; render time this run"
}
row K08-feel-pair        feels stills/K07-K08 "K08 the two feels (Command KQ-000427 left, Pace KQ-000428 right, turned toward each other, each whole inside its page crop), grip" - _left _right || exit 1
row K08-feel-pair-nogrip feels stills/K07-K08 "K08 the two feels, the Naked twins (canon Naked, no butt flare)" KQ_NOGRIP=1 _left _right || exit 1
row K07-lineup-five        row stills/K07-K08 "K07 the Identical lineup (five canon rackets, Command / Pace alternating, KQ-000427..431, the same three-quarter turn, the middle three inside the trio crop x .24 w .52 h .92; replaces the shafts-of-light set: no --seq frames in this language), grip" - || exit 1
row K07-lineup-five-nogrip row stills/K07-K08 "K07 the Identical lineup, the Naked twins (canon Naked, no butt flare)" KQ_NOGRIP=1 || exit 1
log "K4L2-DONE K07 K08"
