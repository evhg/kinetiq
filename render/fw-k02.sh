#!/usr/bin/env bash
# fw-k02.sh: full-weave pass, K02 (Unibody edge view): the four stills at 5120 spp 96 and their swivels (Command 60
# frames, Pace 45; --phone writes the phone frames from the same render), the queue-nov3b p5g recipe. No handle card on
# K02 (its edge view already shows the handle's tiles; the card brightened the top edge, preview 2026-11-07).
. "$(cd "$(dirname "$0")" && pwd)/fw-lib.sh"
K2C="0.09 0.92 0.20 0.86"
log "FW-START K02 device $KQ_DEVICE free $(free_mb) MB push $PUSH"
k02seq() {   # k02seq <name> <frames> <env/cmd...> (cmd has --seq, --phone, --crop, --out seq4/<name>)
  local name=$1 n=$2; shift 2
  local d=$S/$name-desktop t0=$(date +%s) did=0
  done_mark "seqmasters $name-desktop" && { log "SEQ-SKIP $name (masters pushed)"; return 0; }
  log "SEQ-START $name ($n frames)"
  for i in 0 $((n - 1)) $(command seq 1 $((n - 2))); do
    local f=$(printf "f%03d.png" "$i")
    [ -f "$d/$f" ] && [ -f "$S/$name-phone/$f" ] && continue
    wait_disk
    local t1=$(date +%s)
    run_locked "$name" "$@" --only "$i" || { log "SKIP-SEQ $name after an error at frame $i"; return 1; }
    [ -f "$d/$f" ] || { log "SKIP-SEQ $name: frame $i missing"; return 1; }
    log "FRAME $name $i $(( $(date +%s) - t1 )) s free $(free_mb) MB"
    did=$((did + 1)); sleep "$PAUSE"
    if [ "$i" -eq $((n - 1)) ]; then
      python3 "$KIT/seq_cropcheck.py" "$d" "$i" $K2C | while read -r l; do log "cropcheck $name $l"; done
      [ "${PIPESTATUS[0]}" -eq 2 ] && { log "CROP-FAIL $name"; return 1; }
    fi
  done
  log "SEQ-DONE $name: $did frames in $(( $(date +%s) - t0 )) s"
}
# k02v <tag> <still stem> <seq name> <frames> <feel args> <env prefix or -> <what>
k02v() {
  local tag=$1 stem=$2 name=$3 n=$4 fa=$5 en=$6 what=$7
  done_mark "fw status k02 $tag" && return 0
  local t0=$(date +%s) E=()
  [ "$en" != "-" ] && E=(env $en)
  aside "k02 $tag" "$V/$stem.png" "$S/$name-desktop" "$S/$name-phone"
  done_mark "fw unseq k02 $tag" || { unseq "$name-desktop"; mark "fw unseq k02 $tag"; }
  still "fw-$stem" "$V/$stem.png" - -- "${E[@]}" $PY shots/K02-edge-line.py $fa --w 5120 --h 2880 --spp 96 --out final/v5k/$stem
  need "$V/$stem.png" || return 1
  k02seq "$name" "$n" "${E[@]}" $PY shots/K02-edge-line.py $fa --w 5120 --h 2880 --spp 24 --spp0 96 --seq "$n" --range 0 35 --phone --crop $K2C --out "seq4/$name" || return 1
  [ "$(nf "$name-desktop")" -ge "$n" ] && [ "$(nf "$name-phone")" -ge "$n" ] || { log "FW-FAIL K02 $tag swivel incomplete"; return 1; }
  echo "k02-$tag $(( $(date +%s) - t0 ))" >> "$LOGD/full-weave.times"
  [ "$PUSH" = 1 ] || { log "PUSH=0: K02 $tag rendered, not pushed"; return 0; }
  masters "fw m k02 $tag" stills/K02 "K02 $what, $R ($CANON): 5120" "$V/$stem.png"
  done_mark "fw m k02 $tag" || return 1
  seq_masters "$name-desktop" $K2C
  done_mark "seqmasters $name-desktop" || return 1
  local tt=$(awk -v k="k02-$tag" '$1==k{v=$2}END{print v+0}' "$LOGD/full-weave.times")
  st "fw status k02 $tag" "$(date -u +%FT%TZ) $R:K02-$tag stills/K02/$stem.png,sequences/$name-desktop $(hm $tt) $DEVNAME K02 $what 5120x2880 spp 96, swivel $n frames (spp 24, frame 0 at spp 96; phone frames from the same renders in seq4/$name-phone), the queue-nov3b p5g recipe, with the $CANON; render time this run"
}
k02v c  K02-edge-line              K02-swivel-command        60 "--feel command" -          "Command grip"
k02v p  K02-edge-line-pace         K02-swivel-pace           45 "--feel pace"    -          "Pace grip"
k02v nc K02-edge-line-nogrip       K02-swivel-nogrip-command 60 "--feel command" KQ_NOGRIP=1 "Command Naked"
k02v np K02-edge-line-nogrip-pace  K02-swivel-nogrip-pace    45 "--feel pace"    KQ_NOGRIP=1 "Pace Naked"
log "FW-DONE K02"
