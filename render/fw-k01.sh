#!/usr/bin/env bash
# fw-k01.sh: full-weave pass, K01 (Command, Pace, and their Naked twins): 5120 beam base/full/finale, 2160x3840 hero
# portrait, both swivels each (36 frames, yaw 0..35, frame 0 = the -full still), the queue-mac p2 recipe.
. "$(cd "$(dirname "$0")" && pwd)/fw-lib.sh"
P1C="0.20 0.82 0.48 0.95"   # K01 portrait region
D1C="0.27 0.73 0.19 1.0"    # K01 desktop region
PACE="--feel pace --set P_FOLLOW=0.85"
log "FW-START K01 device $KQ_DEVICE free $(free_mb) MB push $PUSH"
# k01v <tag> <still feel args> <seq feel args> <naked 0|1> <what> <seq stem>
k01v() {
  local tag=$1 sfa=$2 qfa=$3 naked=$4 what=$5 sq=$6
  done_mark "fw status k01 $tag" && return 0
  local t0=$(date +%s) ng=() nf_=() beam=K01-hero-beam${tag:+-$tag}-v5k phone=K01-hero-frame-phone${tag:+-$tag}-v5k
  # Naked: no butt flare (as K05; cloud review 2026-11-07: the flare mirrored the beam-lit floor as a band above the Q)
  [ "$naked" = 1 ] && { ng=(--set NOGRIP=1); nf_=(env KQ_NAKED_FLARE=0); }
  aside "k01 $tag" "$F/$beam"-{base,full,finale}.png "$F/$phone"-{base,full}.png "$F/passes/$beam" "$F/passes/$phone" "$S/$sq-phone" "$S/$sq-desktop"
  done_mark "fw unseq k01 $tag" || { unseq "$sq-phone" "$sq-desktop"; mark "fw unseq k01 $tag"; }
  still "fw-$beam" "$F/$beam-finale.png" "$F/passes/$beam" -- "${nf_[@]}" $PY shots/K01-hero-beam.py $sfa "${ng[@]}" --w 5120 --h 2880 --spp 64 --out "final/$beam"
  still "fw-$phone" "$F/$phone-full.png" "$F/passes/$phone" -- "${nf_[@]}" $PY shots/K01-hero-frame.py $sfa "${ng[@]}" --w 2160 --h 3840 --spp 48 --out "final/$phone"
  need "$F/$beam"-{base,full,finale}.png "$F/$phone"-{base,full}.png || return 1
  seq "$sq-phone" 36 $P1C "$F/$phone-full.png" -- "${nf_[@]}" $PY shots/K01-hero-frame.py $qfa "${ng[@]}" --w 2160 --h 3840 --spp 24 --seq 36 --yaw-range 0 35 --crop $P1C --out "seq4/$sq-phone"
  seq "$sq-desktop" 36 $D1C "$F/$beam-full.png" -- "${nf_[@]}" $PY shots/K01-hero-beam.py $qfa "${ng[@]}" --w 5120 --h 2880 --spp 16 --seq 36 --yaw-range 0 35 --crop $D1C --out "seq4/$sq-desktop"
  [ "$(nf "$sq-phone")" -ge 36 ] && [ "$(nf "$sq-desktop")" -ge 36 ] || { log "FW-FAIL K01 $tag swivels incomplete"; return 1; }
  echo "k01-$tag $(( $(date +%s) - t0 ))" >> "$LOGD/full-weave.times"
  [ "$PUSH" = 1 ] || { log "PUSH=0: K01 $tag rendered, not pushed"; return 0; }
  masters "fw m k01 $tag" stills/K01 "K01 $what, $R ($CANON): 5120 beam base/full/finale, 2160 portrait" "$F/$beam"-{base,full,finale}.png "$F/$phone"-{base,full}.png
  done_mark "fw m k01 $tag" || return 1
  seq_masters "$sq-phone" $P1C
  seq_masters "$sq-desktop" $D1C
  done_mark "seqmasters $sq-phone" && done_mark "seqmasters $sq-desktop" || return 1
  local nk=""
  [ "$naked" = 1 ] && nk="; Naked without the butt flare (KQ_NAKED_FLARE=0, as K05: the flare mirrored the beam-lit floor as a band above the Q), the butt off the grip strips"
  local tt=$(awk -v k="k01-$tag" '$1==k{v=$2}END{print v+0}' "$LOGD/full-weave.times")
  st "fw status k01 $tag" "$(date -u +%FT%TZ) $R:K01${tag:+-$tag} stills/K01/$beam-{base,full,finale}.png,stills/K01/$phone-{base,full}.png,sequences/$sq-phone,sequences/$sq-desktop $(hm $tt) $DEVNAME K01 $what, the queue-mac p2 recipe (beam 5120 spp 64, portrait 2160x3840 spp 48, swivels 36 frames, phone spp 24, desktop spp 16, frame 0 = the -full still) with the $CANON$nk; render time this run"
}
k01v ""          "--feel command" "--feel command" 0 "Command grip"  K01-swivel-command
k01v pace        "--feel pace"    "$PACE"          0 "Pace grip"     K01-swivel-pace
k01v nogrip      "--feel command" "--feel command" 1 "Command Naked" K01-swivel-nogrip-command
k01v nogrip-pace "--feel pace"    "$PACE"          1 "Pace Naked (the handle card re-aimed every frame, the grip strips at 2x the yaw)" K01-swivel-nogrip-pace
log "FW-DONE K01"
