#!/bin/bash
# queue-swivels.sh (2026-11-02): the K01 and K02 swivels re-rendered in the NEW canon (HD weave, 1.0 mm edge), the K01
# Pace stills with the owner-note-7 weave light, and the grip-off swivels. Resumable: frames and stills on disk are
# skipped, so killing it (by PID) and starting it again loses at most the frame in progress.
#
#   setsid nohup render/queue-swivels.sh > $KQ_RENDER_OUT/logs/queue-swivels.log 2>&1 &
#   ONLY="a b" render/queue-swivels.sh ...     # run only these items (a..h, see JOBS below)
#
# One Blender at a time: every frame (and every still) takes the shared lock for itself (flock $LOCK), then waits
# PAUSE s, so other shots can slip in between frames. Each sequence renders frame 0 (at the matching still's samples,
# --spp0, so the frame the page swaps in over the still matches it), then the last frame, then checks that the --crop
# region holds everything that moves (seq_cropcheck.py; a FAIL skips the rest of that sequence), then the rest in order.
#
# Disk: a frame starts only with at least MIN_START_MB free (else the queue waits, polling every minute, up to
# MAX_WAIT_MIN, then exits 3); while a frame renders a watchdog kills it and exits the queue (3) if free space drops
# under STOP_MB. Log lines: FRAME <name> <index> <seconds> s free <MB> MB; JOB-DONE; STILL; STOP-DISK; ALL-DONE.
set -u
KIT=$(cd "$(dirname "$0")" && pwd)
cd "$KIT"
export KQ_RENDER_OUT=${KQ_RENDER_OUT:-/home/user/kinetiq-render-out}
PY=$KQ_RENDER_OUT/bpyenv/bin/python
OUT=$KQ_RENDER_OUT/out
LOCK=${KQ_LOCK:-/home/user/kinetiq/render/render.lock}   # the lock every render agent on this machine shares
MIN_START_MB=${MIN_START_MB:-2560}
STOP_MB=${STOP_MB:-1536}
MAX_WAIT_MIN=${MAX_WAIT_MIN:-360}
PAUSE=${PAUSE:-5}
ONLY=${ONLY:-}

log() { echo "$(date -u +%FT%TZ) $*"; }
free_mb() { df -Pm / | awk 'NR==2{print $4}'; }

wait_disk() {
  local waited=0
  while [ "$(free_mb)" -lt "$MIN_START_MB" ]; do
    [ $((waited % 10)) -eq 0 ] && log "WAIT-DISK free $(free_mb) MB < $MIN_START_MB MB (waited $waited min)"
    if [ "$waited" -ge "$MAX_WAIT_MIN" ]; then log "STOP-DISK gave up waiting for space"; exit 3; fi
    sleep 60; waited=$((waited + 1))
  done
}

# run_locked <label> <cmd...>: one render under the lock, with the disk watchdog. Output goes to logs/queue-swivels/
run_locked() {
  local label=$1; shift
  mkdir -p "$KQ_RENDER_OUT/logs/queue-swivels"
  local blog="$KQ_RENDER_OUT/logs/queue-swivels/$label.log"
  setsid flock "$LOCK" "$@" >> "$blog" 2>&1 &
  local pid=$!
  while kill -0 "$pid" 2>/dev/null; do
    if [ "$(free_mb)" -lt "$STOP_MB" ]; then
      log "STOP-DISK free $(free_mb) MB < $STOP_MB MB during $label: killing it (process group $pid)"
      kill -TERM -- "-$pid" 2>/dev/null; sleep 5; kill -KILL -- "-$pid" 2>/dev/null
      exit 3
    fi
    sleep 10
  done
  wait "$pid"
  local rc=$?
  [ $rc -ne 0 ] && log "ERROR $label exit $rc (see $blog)"
  return $rc
}

want() { [ -z "$ONLY" ] || [[ " $ONLY " == *" $1 "* ]]; }

# seq <item> <name> <frames> <crop x0 x1 y0 y1> <check dirs (under out/), space-separated> -- <script and args>
# The script args must hold --seq, --crop and --out; the queue adds --only i.
seq_job() {
  local item=$1 name=$2 n=$3 cx0=$4 cx1=$5 cy0=$6 cy1=$7 dirs=$8; shift 9
  want "$item" || return 0
  local first=${dirs%% *}
  local t0=$(date +%s) done=0 crop_ok=1
  log "JOB-START $item $name ($n frames) $*"
  local order="0 $((n - 1)) $(seq 1 $((n - 2)))"
  for i in $order; do
    local f=$(printf "f%03d.png" "$i") have=1
    for d in $dirs; do [ -f "$OUT/$d/$f" ] || have=0; done
    if [ $have -eq 0 ]; then
      if [ $crop_ok -eq 0 ]; then break; fi
      wait_disk
      local t1=$(date +%s)
      run_locked "$name" $PY "$@" --only "$i" || { log "SKIP-JOB $name after an error at frame $i"; return 1; }
      [ -f "$OUT/$first/$f" ] || { log "SKIP-JOB $name: frame $i missing after its render"; return 1; }
      log "FRAME $name $i $(( $(date +%s) - t1 )) s free $(free_mb) MB"
      done=$((done + 1))
      sleep "$PAUSE"
    fi
    if [ "$i" -eq $((n - 1)) ]; then
      python3 "$KIT/seq_cropcheck.py" "$OUT/$first" "$i" "$cx0" "$cx1" "$cy0" "$cy1" | while read -r l; do log "$l"; done
      if [ "${PIPESTATUS[0]}" -eq 2 ]; then
        log "CROP-FAIL $name: something moves at the region's edge; skipping the rest of this sequence"
        crop_ok=0
      fi
    fi
  done
  log "JOB-DONE $item $name: $done frames rendered in $(( $(date +%s) - t0 )) s; $(ls "$OUT/$first" | grep -c '^f[0-9]*\.png$') of $n on disk"
}

# still <item> <label> <expected png under out/> -- <script and args>
still_job() {
  local item=$1 label=$2 expect=$3; shift 4
  want "$item" || return 0
  if [ -f "$OUT/$expect" ]; then log "STILL-SKIP $label ($expect on disk)"; return 0; fi
  wait_disk
  local t1=$(date +%s)
  run_locked "$label" $PY "$@" || { log "SKIP-STILL $label after an error"; return 1; }
  log "STILL $label $(( $(date +%s) - t1 )) s free $(free_mb) MB"
  sleep "$PAUSE"
}

log "QUEUE-START kit $KIT lock $LOCK free $(free_mb) MB (start >= $MIN_START_MB, stop < $STOP_MB)"
P1="0.20 0.82 0.48 0.95"   # K01 portrait region (racket box over the turn: x 0.35-0.65, y 0.51-0.81)
D1="0.27 0.73 0.19 1.0"    # K01 desktop region (x 0.41-0.59, y 0.27-0.81; the floor shadow runs to the bottom)
K2="0.09 0.92 0.20 0.86"   # K02 region
PACE="--feel pace --set P_FOLLOW=0.85"   # the Pace swivel: the face cards follow 85 % of the turn (README)

# a) K01 Command portrait  b) K01 Command desktop  c) K02 Command (2560 + its rotated phone frames)
seq_job a K01-swivel-command-phone 36 $P1 "seq3/K01-swivel-command-phone" -- shots/K01-hero-frame.py --feel command --w 2160 --h 3840 --spp 24 --spp0 48 --seq 36 --yaw-range 0 35 --crop $P1 --out seq3/K01-swivel-command-phone
seq_job b K01-swivel-command-desktop 36 $D1 "seq3/K01-swivel-command-desktop" -- shots/K01-hero-beam.py --feel command --w 2560 --h 1440 --spp 24 --spp0 128 --seq 36 --yaw-range 0 35 --crop $D1 --out seq3/K01-swivel-command-desktop
seq_job c K02-swivel-command 60 $K2 "seq3/K02-swivel-command-desktop seq3/K02-swivel-command-phone" -- shots/K02-edge-line.py --feel command --w 2560 --h 1440 --spp 32 --spp0 128 --seq 60 --range 0 35 --phone --crop $K2 --out seq3/K02-swivel-command
# d) the K01 Pace stills with the note-7 weave light (k01_lib defaults), new names (-n7) so the old ones stay; the
#    grip-off Pace stills too, so the grip-off Pace swivels' frame 0 has a still to register with
still_job d K01-beam-pace-n7 final/K01-hero-beam-pace-n7-full.png -- shots/K01-hero-beam.py --feel pace --w 2560 --h 1440 --spp 128 --out final/K01-hero-beam-pace-n7
still_job d K01-phone-pace-n7 final/K01-hero-frame-phone-pace-n7-full.png -- shots/K01-hero-frame.py --feel pace --w 2160 --h 3840 --spp 48 --out final/K01-hero-frame-phone-pace-n7
still_job d K01-beam-nogrip-pace-n7 final/K01-hero-beam-nogrip-pace-n7-full.png -- shots/K01-hero-beam.py --feel pace --set NOGRIP=1 --variants base,full --w 2560 --h 1440 --spp 128 --out final/K01-hero-beam-nogrip-pace-n7
still_job d K01-phone-nogrip-pace-n7 final/K01-hero-frame-phone-nogrip-pace-n7-full.png -- shots/K01-hero-frame.py --feel pace --set NOGRIP=1 --w 2160 --h 3840 --spp 48 --out final/K01-hero-frame-phone-nogrip-pace-n7
# e) f) K01 Pace swivels  g) K02 Pace
seq_job e K01-swivel-pace-phone 36 $P1 "seq3/K01-swivel-pace-phone" -- shots/K01-hero-frame.py $PACE --w 2160 --h 3840 --spp 24 --spp0 48 --seq 36 --yaw-range 0 35 --crop $P1 --out seq3/K01-swivel-pace-phone
seq_job f K01-swivel-pace-desktop 36 $D1 "seq3/K01-swivel-pace-desktop" -- shots/K01-hero-beam.py $PACE --w 2560 --h 1440 --spp 24 --spp0 128 --seq 36 --yaw-range 0 35 --crop $D1 --out seq3/K01-swivel-pace-desktop
seq_job g K02-swivel-pace 45 $K2 "seq3/K02-swivel-pace-desktop seq3/K02-swivel-pace-phone" -- shots/K02-edge-line.py --feel pace --w 2560 --h 1440 --spp 32 --spp0 128 --seq 45 --range 0 35 --phone --crop $K2 --out seq3/K02-swivel-pace
# h) grip-off swivels (the site looks for K01-swivel-nogrip-<feel>-<layout>)
seq_job h K01-swivel-nogrip-command-phone 36 $P1 "seq3/K01-swivel-nogrip-command-phone" -- shots/K01-hero-frame.py --feel command --set NOGRIP=1 --w 2160 --h 3840 --spp 24 --spp0 48 --seq 36 --yaw-range 0 35 --crop $P1 --out seq3/K01-swivel-nogrip-command-phone
seq_job h K01-swivel-nogrip-command-desktop 36 $D1 "seq3/K01-swivel-nogrip-command-desktop" -- shots/K01-hero-beam.py --feel command --set NOGRIP=1 --w 2560 --h 1440 --spp 24 --spp0 128 --seq 36 --yaw-range 0 35 --crop $D1 --out seq3/K01-swivel-nogrip-command-desktop
seq_job h K01-swivel-nogrip-pace-phone 36 $P1 "seq3/K01-swivel-nogrip-pace-phone" -- shots/K01-hero-frame.py $PACE --set NOGRIP=1 --w 2160 --h 3840 --spp 24 --spp0 48 --seq 36 --yaw-range 0 35 --crop $P1 --out seq3/K01-swivel-nogrip-pace-phone
seq_job h K01-swivel-nogrip-pace-desktop 36 $D1 "seq3/K01-swivel-nogrip-pace-desktop" -- shots/K01-hero-beam.py $PACE --set NOGRIP=1 --w 2560 --h 1440 --spp 24 --spp0 128 --seq 36 --yaw-range 0 35 --crop $D1 --out seq3/K01-swivel-nogrip-pace-desktop
log "ALL-DONE free $(free_mb) MB"
