#!/usr/bin/env bash
# queue-mac.sh (2026-11-04): the Mac render node's queue (notes/mac-handoff.md section 3), on the M3 Max's Metal GPU.
#   p2b K01 Command Naked: stills re-rendered HERE (beam 5120 x 2880 spp 64 base/full/finale, portrait 2160 x 3840
#       spp 48), then its swivels (portrait 2160 spp 24, desktop 5120 spp 16, 36 frames, 0-35 deg): a still and its
#       swivel always come from the same machine and device, so frame 0 is the still the page shows.
#   p2c K01 Pace grip stills + swivels; p2d K01 Pace Naked stills + swivels (the commands of queue-nov3.sh p1a/p2c/p2d).
#   then queue-nov3b.sh item by item: p4, p3, p5a .. p5g.
# Masters go to the private evhg/kinetiq-masters (masters_push.sh, seq_masters); no exports here (KQ_NO_EXPORT=1: the
# cloud session exports, checks and releases). After each item one line goes to STATUS-mac.md at the root of the
# masters repo (status_push.sh): <UTC time> <item> <paths in the masters repo> <render time> <device> <notes>.
# Resumable like queue-nov3.sh: stills by their -full.png, frames by fNNN.png, pushes and status lines by their line in
# logs/queue-nov3.done. One Blender at a time (flock $KQ_LOCK). Run detached, awake, on power:
#   nohup caffeinate -dimsu render/queue-mac.sh >> ~/kinetiq-render/out/logs/queue-mac.log 2>&1 &
#   ONLY="p2b" ...  (items: p2b p2c p2d p4 p3 p5a p5b p5c p5d p5e p5f p5g)
# bash >= 4.4 (empty arrays under set -u); macOS /bin/bash is 3.2: re-run under Homebrew's bash
if [ "${BASH_VERSINFO[0]}" -lt 5 ] && [ -x /opt/homebrew/bin/bash ]; then exec /opt/homebrew/bin/bash "$0" "$@"; fi
export KQ_RENDER_OUT=${KQ_RENDER_OUT:-$HOME/kinetiq-render/out}
export KQ_LOCK=${KQ_LOCK:-$HOME/kinetiq-render/render.lock}
export RENDER_ROOT=${RENDER_ROOT:-$(cd "$(dirname "$0")" && pwd)}
export KQ_DEVICE=${KQ_DEVICE:-METAL}
export KQ_NO_EXPORT=1
QNAME=queue-mac
. "$(cd "$(dirname "$0")" && pwd)/queue_lib.sh"
DEVNAME="M3Max-$KQ_DEVICE"
MDATE=$(date -u +%F)

hm() { printf '%dh%02dm' $(($1 / 3600)) $(($1 % 3600 / 60)); }
# status <item> <seconds> <paths in the masters repo> <notes>: one STATUS-mac.md line, once per item
status() {
  local item=$1 secs=$2 paths=$3 notes=$4 m="status $1"
  done_mark "$m" && return 0
  local line
  line="$(date -u +%FT%TZ) $item $paths $(hm "$secs") $DEVNAME $notes"
  if "$KIT/status_push.sh" "$line" >> "$LOGD/status.log" 2>&1; then mark "$m"; log "STATUS $item ok: $line"
  else log "ERROR status $item (see $LOGD/status.log)"; fi
}
# all_done <marker...>: every masters push of an item went through (% stands for a space inside a marker)
all_done() { local x; for x in "$@"; do done_mark "${x//%/ }" || return 1; done; }
nframes() { ls "$S/$1" 2>/dev/null | grep -c '^f[0-9]*\.png$'; }

log "QUEUE-START (mac) kit $KIT device $KQ_DEVICE lock $LOCK free $(free_mb) MB"
P1C="0.20 0.82 0.48 0.95"   # K01 portrait region (queue-nov3.sh)
D1C="0.27 0.73 0.19 1.0"    # K01 desktop region
PACE="--feel pace --set P_FOLLOW=0.85"

# k01item <item> <tag> <still feel args> <seq feel args> <naked 0|1> <stills label> <seq stem>
#   tag: the out-name infix (nogrip, pace, nogrip-pace); seq stem: K01-swivel-<x> (-phone, -desktop)
k01item() {
  local item=$1 tag=$2 sfa=$3 qfa=$4 naked=$5 what=$6 sq=$7
  want "$item" || return 0
  done_mark "status $item" && { log "ITEM-SKIP $item (done: status pushed)"; return 0; }
  log "ITEM-START $item"
  local t0=$(date +%s) ng=() beam=K01-hero-beam-$tag-v5k phone=K01-hero-frame-phone-$tag-v5k
  [ "$naked" = 1 ] && ng=(--set NOGRIP=1)
  still "K01-beam-$tag-v5k" "$F/$beam-finale.png" "$F/passes/$beam" -- $PY shots/K01-hero-beam.py $sfa "${ng[@]}" --w 5120 --h 2880 --spp 64 --out "final/$beam"
  still "K01-phone-$tag-v5k" "$F/$phone-full.png" "$F/passes/$phone" -- $PY shots/K01-hero-frame.py $sfa "${ng[@]}" --w 2160 --h 3840 --spp 48 --out "final/$phone"
  [ -f "$F/$beam-finale.png" ] && [ -f "$F/$phone-full.png" ] || { log "ITEM-FAIL $item: stills missing"; return 1; }
  masters "m-mac-$beam" stills/K01 "K01 $what: 5120 beam base/full/finale, 2160 portrait, light-sweep scene ($MDATE, Mac M3 Max $KQ_DEVICE)" "$F/$beam"-{base,full,finale}.png "$F/$phone"-{base,full}.png
  done_mark "seqmasters $sq-phone" || seq "$sq-phone" 36 $P1C "$F/$phone-full.png" -- $PY shots/K01-hero-frame.py $qfa "${ng[@]}" --w 2160 --h 3840 --spp 24 --seq 36 --yaw-range 0 35 --crop $P1C --out "seq4/$sq-phone"
  done_mark "seqmasters $sq-desktop" || seq "$sq-desktop" 36 $D1C "$F/$beam-full.png" -- $PY shots/K01-hero-beam.py $qfa "${ng[@]}" --w 5120 --h 2880 --spp 16 --seq 36 --yaw-range 0 35 --crop $D1C --out "seq4/$sq-desktop"
  local n
  for n in phone desktop; do   # seq_masters returns at once when its marker is set
    local c=$P1C; [ $n = desktop ] && c=$D1C
    if done_mark "seqmasters $sq-$n" || [ "$(nframes "$sq-$n")" -ge 36 ]; then seq_masters "$sq-$n" $c; fi
  done
  if all_done "m-mac-$beam" "seqmasters $sq-phone" "seqmasters $sq-desktop"; then
    status "$item" $(( $(date +%s) - t0 )) "stills/K01/$beam-{base,full,finale}.png,stills/K01/$phone-{base,full}.png,sequences/$sq-phone,sequences/$sq-desktop" \
      "K01 $what: stills+swivels same device (frame 0 = the -full still); swivels in the seq_masters layout (f000 whole + region crops, crop.json); render time this run"
    log "ITEM-DONE $item"
  else log "ITEM-FAIL $item: a masters push is missing (see $LOGD/masters.log)"; fi
}

run_all() {
k01item p2b nogrip "--feel command" "--feel command" 1 "Command Naked" K01-swivel-nogrip-command
k01item p2c pace "--feel pace" "$PACE" 0 "Pace grip (note-7 weave, cards follow 85 %)" K01-swivel-pace
k01item p2d nogrip-pace "--feel pace" "$PACE" 1 "Pace Naked" K01-swivel-nogrip-pace

# queue-nov3b.sh items, one at a time (its own still/masters calls; exports skipped by KQ_NO_EXPORT)
nov3b() {   # nov3b <item> "<masters markers>" "<paths in the masters repo>" "<notes>"
  local item=$1 marks=$2 paths=$3 notes=$4
  want "$item" || return 0
  done_mark "status $item" && { log "ITEM-SKIP $item (done: status pushed)"; return 0; }
  local t0=$(date +%s)
  ONLY="$item" WAIT_FOR_NOV3=0 "$KIT/queue-nov3b.sh" >> "$KQ_RENDER_OUT/logs/queue-nov3b.log" 2>&1
  # shellcheck disable=SC2086
  if all_done $marks; then status "$item" $(( $(date +%s) - t0 )) "$paths" "$notes; render time this run"
  else log "ITEM-FAIL $item: masters not all pushed (markers: $marks; see logs/queue-nov3b.log)"; fi
}
nov3b p4 "m-k15" "stills/K15/K15-space{,-pace}-{base,full}.png" "K15 5120x2880 both feels, wrapped bores (KQ_HOLE_UV=cyl)"
nov3b p3 "m-k05" "stills/K05/K05-laser-scan*.png" "K05 v7 5120x2880 (notes/k05-v7*.args) Command, Pace, Naked twins, laser layer"
nov3b p5a "m-k14" "stills/K14/K14-edge{,-pace}.png" "K14 5120x2880 both feels"
nov3b p5b "m-k04" "stills/K04/K04-hole-macro{,-pace}-{base,full}.png" "K04 5120x2880 both feels"
nov3b p5c "m-k16" "stills/K16/K16-pair{,-pace}-{base,full}.png" "K16 pair 5120x2880 (halves 2560x2880) both feels"
nov3b p5d "m-k17" "stills/K17/K17-roughness{,-base,-pace,-pace-base}.png" "K17 5120x2880 both feels"
nov3b p5e "m-k06" "stills/K06/K06-mould*-{base,full}.png" "K06 5120x2880 grip and Naked, both feels"
nov3b p5f "m-k0708" "stills/K07-K08/K07-lineup-five{,-nogrip}.png,stills/K07-K08/K08-feel-pair{,-nogrip}.png" "K07 and K08 5120x2880 grip and Naked"
nov3b p5g "m-k02c m-k02p seqmasters%K02-swivel-command-desktop seqmasters%K02-swivel-nogrip-command-desktop seqmasters%K02-swivel-pace-desktop seqmasters%K02-swivel-nogrip-pace-desktop" "stills/K02/K02-edge-line{,-nogrip}{,-pace}.png,sequences/K02-swivel{,-nogrip}-{command,pace}-desktop" \
  "K02 5120 new canon grip and Naked, both feels, with its swivels (60 Command / 45 Pace frames; phone = desktop turned 90 deg)"

}
run_all
pending=$(for i in p2b p2c p2d p4 p3 p5a p5b p5c p5d p5e p5f p5g; do want $i && ! done_mark "status $i" && echo $i; done | tr '\n' ' ')
if [ -n "$pending" ]; then log "RETRY-PASS for: $pending(in 10 min)"; sleep 600; run_all; fi
log "ALL-DONE (mac) free $(free_mb) MB"
