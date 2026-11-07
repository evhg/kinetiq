#!/usr/bin/env bash
# fw-k04fix.sh (2026-11-07, the Mac render node): cloud REQUEST k04-language-fix (21:51Z, before the rest of the
# full-weave pass): (1) every grip-on render of the k04-language batch again with the canon neutral-black overgrip
# (K11-dark GRIP_DARK: no key / sheen / strip reaches the overgrip; a thin back strip and a faint side strip linked to it
# alone draw its silhouette and helical wrap; the cap keeps its light, satin black with the Q); (2) the First 500 pair
# with its set number 027/500 on both throats (K11-dark PAIR_SET), grip and Naked. Same cameras, crops, base and full;
# K11-pair-mix skipped (not used); the Naked singles, K08 and K07 Naked twins unchanged. One STATUS line per item.
# Resumable (markers "k4f ..."); the previous files go to $F/pre-k04fix once.
. "$(cd "$(dirname "$0")" && pwd)/fw-lib.sh"
R4=k04-language-fix
OLDF=$F/pre-k04fix
mkdir -p "$OLDF"
NAKED="the Naked twin (canon Naked, no butt flare)"
FIXTXT="the canon neutral-black overgrip (no key, sheen or strip on it; a thin back strip and a faint side strip linked to it alone draw its silhouette and helical wrap; the cap satin black with the Q)"
log "K4F-START device $KQ_DEVICE free $(free_mb) MB push $PUSH"
aside_f() { local m="k4f aside $1"; shift; done_mark "$m" && return 0; local f; for f in "$@"; do [ -e "$f" ] && mv "$f" "$OLDF"/; done; mark "$m"; }
# k11 <stem> <what> <env or -> <what changed> <args...>
k11() {
  local stem=$1 what=$2 ev=$3 fx=$4; shift 4
  done_mark "k4f status $stem" && return 0
  aside_f "$stem" "$V/$stem"-{base,full}{,_card}.png "$V/$stem.exr"
  local t0=$(date +%s) envs=()
  [ "$ev" != "-" ] && envs=(env $ev)
  still "k4f-$stem" "$V/$stem-full_card.png" - -- "${envs[@]}" $PY shots/K11-dark.py "$@" --w 5120 --h 2880 --spp 256 --out "final/v5k/$stem"
  need "$V/$stem"-{base,full}{,_card}.png || return 1
  local tt=$(( $(date +%s) - t0 ))
  echo "k4f-$stem $tt" >> "$LOGD/full-weave.times"
  [ "$PUSH" = 1 ] || { log "PUSH=0: $stem rendered, not pushed"; return 0; }
  masters "k4f m $stem" stills/K11 "K11 $what, $R4 base + full, 5120x2880 + card" "$V/$stem"-{base,full}{,_card}.png
  done_mark "k4f m $stem" || return 1
  st "k4f status $stem" "$(date -u +%FT%TZ) $R4:$stem stills/K11/$stem-{base,full}{,_card}.png $(hm $tt) $DEVNAME K11 $what, k04-language as OK'd 16:10Z, re-rendered with $fx; same camera and card crop (x 0.275 w 0.45), 5120x2880 spp 256, base + full from one render; with the $CANON; render time this run"
}
# row <stem> <mode> <what> <env or -> [extra suffixes]
row() {
  local stem=$1 mode=$2 what=$3 ev=$4; shift 4
  local sfx=("$@")
  done_mark "k4f status $stem" && return 0
  local files=("$V/$stem"-{base,full}.png)
  local s; for s in "${sfx[@]}"; do files+=("$V/$stem"-{base,full}"$s".png); done
  aside_f "$stem" "${files[@]}" "$V/$stem.exr"
  local t0=$(date +%s) envs=()
  [ "$ev" != "-" ] && envs=(env $ev)
  still "k4f-$stem" "$V/$stem-full.png" - -- "${envs[@]}" $PY shots/Kdark_row.py --mode "$mode" --w 5120 --h 2880 --spp 160 --out "final/v5k/$stem"
  need "${files[@]}" || return 1
  local tt=$(( $(date +%s) - t0 ))
  echo "k4f-$stem $tt" >> "$LOGD/full-weave.times"
  [ "$PUSH" = 1 ] || { log "PUSH=0: $stem rendered, not pushed"; return 0; }
  masters "k4f m $stem" stills/K07-K08 "$what, $R4 base + full, 5120x2880" "${files[@]}"
  done_mark "k4f m $stem" || return 1
  local list=$(for f in "${files[@]}"; do printf '%s/%s,' stills/K07-K08 "$(basename "$f")"; done | sed 's/,$//')
  st "k4f status $stem" "$(date -u +%FT%TZ) $R4:$stem $list $(hm $tt) $DEVNAME $what, k04-language as OK'd (16:10Z, K07 16:41Z), re-rendered with $FIXTXT; same camera, 5120x2880 spp 160, base + full from one render; with the $CANON; render time this run"
}
SETTXT="027/500 on both throats (canon: a First 500 set shows its set number)"
k11 K11-single              "single Command, grip"                -           "$FIXTXT"                    --mode single --feel command || exit 1
k11 K11-single-pace         "single Pace, grip"                   -           "$FIXTXT"                    --mode single --feel pace    || exit 1
k11 K11-pair-command        "First 500 pair, Command, grip"       -           "$FIXTXT and $SETTXT"        --mode pair --weave command  || exit 1
k11 K11-pair-pace           "First 500 pair, Pace, grip"          -           "$FIXTXT and $SETTXT"        --mode pair --weave pace     || exit 1
k11 K11-pair-nogrip-command "First 500 pair, Command, $NAKED"     KQ_NOGRIP=1 "$SETTXT"                    --mode pair --weave command  || exit 1
k11 K11-pair-nogrip-pace    "First 500 pair, Pace, $NAKED"        KQ_NOGRIP=1 "$SETTXT"                    --mode pair --weave pace     || exit 1
row K08-feel-pair   feels "K08 the two feels (Command KQ-000427 left, Pace KQ-000428 right), grip" - _left _right || exit 1
row K07-lineup-five row   "K07 the Identical lineup (KQ-000427..431), grip"                          - || exit 1
log "K4F-DONE"
