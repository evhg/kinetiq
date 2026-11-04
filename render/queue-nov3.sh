#!/bin/bash
# queue-nov3.sh (owner feedback 2026-11-03): Naked (100 % carbon butt), 5K hero, the light-sweep swivels. Resumable:
# every item checks its output on disk (and a done marker for exports) and skips what is there, so after a container
# restart just start it again (notes/queue-nov3.md):
#
#   cd /home/user/kinetiq && setsid nohup render/queue-nov3.sh >> /home/user/kinetiq-render-out/logs/queue-nov3.log 2>&1 &
#   ONLY="p1a p1b" render/queue-nov3.sh ...    # only these items
#
# One Blender at a time: every render (each still, each swivel frame) takes the shared lock (flock $LOCK) for itself and
# pauses PAUSE s after, so a preview elsewhere can slip in. Disk guard as queue-swivels.sh (MIN_START_MB / STOP_MB).
# Log lines: ITEM-START/ITEM-DONE <item>, STILL <label> <s>, FRAME <name> <i> <s>, PATCH <name> RING ..., EXPORT ...,
# MASTERS ..., SKIP/ERROR ..., ALL-DONE. Per-render Blender output: logs/queue-nov3/<label>.log.
set -u
KIT=$(cd "$(dirname "$0")" && pwd)
cd "$KIT"
export KQ_RENDER_OUT=${KQ_RENDER_OUT:-/home/user/kinetiq-render-out}
PY=$KQ_RENDER_OUT/bpyenv/bin/python
OUT=$KQ_RENDER_OUT/out
F=$OUT/final
S=$OUT/seq4
LOGD=$KQ_RENDER_OUT/logs/queue-nov3
DONE=$KQ_RENDER_OUT/logs/queue-nov3.done      # one line per finished export / masters push (resume markers)
LOCK=${KQ_LOCK:-/home/user/kinetiq/render/render.lock}
MIN_START_MB=${MIN_START_MB:-3072}
STOP_MB=${STOP_MB:-1536}
MAX_WAIT_MIN=${MAX_WAIT_MIN:-360}
PAUSE=${PAUSE:-4}
ONLY=${ONLY:-}
mkdir -p "$LOGD" "$S"
touch "$DONE"

log() { echo "$(date -u +%FT%TZ) $*"; }
free_mb() { df -Pm / | awk 'NR==2{print $4}'; }
want() { [ -z "$ONLY" ] || [[ " $ONLY " == *" $1 "* ]]; }
done_mark() { grep -qxF "$1" "$DONE"; }
mark() { echo "$1" >> "$DONE"; }

wait_disk() {
  local waited=0
  while [ "$(free_mb)" -lt "$MIN_START_MB" ]; do
    [ $((waited % 10)) -eq 0 ] && log "WAIT-DISK free $(free_mb) MB < $MIN_START_MB MB (waited $waited min)"
    if [ "$waited" -ge "$MAX_WAIT_MIN" ]; then log "STOP-DISK gave up waiting for space"; exit 3; fi
    sleep 60; waited=$((waited + 1))
  done
}

# run_locked <label> <cmd...> (env assignments go in front via `env`)
run_locked() {
  local label=$1; shift
  local blog="$LOGD/$label.log"
  setsid flock "$LOCK" "$@" >> "$blog" 2>&1 &
  local pid=$!
  while kill -0 "$pid" 2>/dev/null; do
    if [ "$(free_mb)" -lt "$STOP_MB" ]; then
      log "STOP-DISK free $(free_mb) MB < $STOP_MB MB during $label: killing it"
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

# still <label> <expected png> <passes prefix to delete after, or -> -- <env/cmd...>
still() {
  local label=$1 expect=$2 passes=$3; shift 4
  if [ -f "$expect" ]; then log "STILL-SKIP $label (on disk)"; return 0; fi
  wait_disk
  local t1=$(date +%s)
  run_locked "$label" "$@" || { log "SKIP-STILL $label after an error"; return 1; }
  [ -f "$expect" ] || { log "SKIP-STILL $label: $expect missing after its render"; return 1; }
  [ "$passes" != "-" ] && rm -rf "$passes"*
  log "STILL $label $(( $(date +%s) - t1 )) s free $(free_mb) MB"
  sleep "$PAUSE"
}

# seq <name> <frames> <crop x0 x1 y0 y1> <frame-0 still> -- <cmd...>  (cmd holds --seq, --crop, --out seq4/<name>)
# Frame 0 is the still's own "full" variant (the same scene at t = 0), copied, so the page's swap is exact; then the
# last frame and the crop check, then the rest in order.
seq() {
  local name=$1 n=$2 cx0=$3 cx1=$4 cy0=$5 cy1=$6 f0=$7; shift 8
  local d=$S/$name t0=$(date +%s) did=0
  mkdir -p "$d"
  if [ ! -f "$d/f000.png" ]; then
    [ -f "$f0" ] || { log "SKIP-SEQ $name: no frame-0 still $f0"; return 1; }
    cp "$f0" "$d/f000.png"
  fi
  log "SEQ-START $name ($n frames) $*"
  for i in $((n - 1)) $(command seq 1 $((n - 2))); do
    local f=$(printf "f%03d.png" "$i")
    if [ ! -f "$d/$f" ]; then
      wait_disk
      local t1=$(date +%s)
      run_locked "$name" "$@" --only "$i" || { log "SKIP-SEQ $name after an error at frame $i"; return 1; }
      [ -f "$d/$f" ] || { log "SKIP-SEQ $name: frame $i missing after its render"; return 1; }
      log "FRAME $name $i $(( $(date +%s) - t1 )) s free $(free_mb) MB"
      did=$((did + 1))
      sleep "$PAUSE"
    fi
    if [ "$i" -eq $((n - 1)) ]; then
      python3 "$KIT/seq_cropcheck.py" "$d" "$i" "$cx0" "$cx1" "$cy0" "$cy1" | while read -r l; do log "cropcheck $name $l"; done
      [ "${PIPESTATUS[0]}" -eq 2 ] && { log "CROP-FAIL $name: something moves at the region's edge; stopping this sequence"; return 1; }
    fi
  done
  log "SEQ-DONE $name: $did frames rendered in $(( $(date +%s) - t0 )) s; $(ls "$d" | grep -c '^f[0-9]*\.png$') of $n on disk"
}

export_stills() {   # export_stills <marker> "<msg>" <ids...>
  local m=$1 msg=$2; shift 2
  done_mark "$m" && return 0
  if "$KIT/export_push.sh" stills "$msg" "$@" >> "$LOGD/export.log" 2>&1; then mark "$m"; log "EXPORT $m ok"; else log "ERROR export $m (see $LOGD/export.log)"; fi
}

export_seq() {      # export_seq <marker> "<msg>" <names...>
  local m=$1 msg=$2; shift 2
  done_mark "$m" && return 0
  if "$KIT/export_push.sh" seq "$msg" "$S" "$@" >> "$LOGD/export.log" 2>&1; then mark "$m"; log "EXPORT $m ok"; else log "ERROR export $m (see $LOGD/export.log)"; fi
}

masters() {         # masters <marker> <repo dir> "<msg>" <files...>
  local m=$1 dir=$2 msg=$3; shift 3
  done_mark "$m" && return 0
  if "$KIT/masters_push.sh" "$dir" "$msg" "$@" >> "$LOGD/masters.log" 2>&1; then mark "$m"; log "MASTERS $m ok"; else log "ERROR masters $m (see $LOGD/masters.log)"; fi
}

seq_masters() {     # seq_masters <name> <crop x0 x1 y0 y1>: region-only masters pushed, then frames 1.. deleted here
  local name=$1; shift
  local m="seqmasters $name"
  done_mark "$m" && return 0
  local tmp=$KQ_RENDER_OUT/tmp-seqm/$name
  $PY "$KIT/seq_masters.py" "$S/$name" "$tmp" "$@" >> "$LOGD/masters.log" 2>&1 || { log "ERROR seq_masters $name"; return 1; }
  if "$KIT/masters_push.sh" "sequences/$name" "$name: light-sweep swivel (2026-11-03), f000 whole + region crops" "$tmp"/* >> "$LOGD/masters.log" 2>&1; then
    mark "$m"; rm -rf "$tmp"
    find "$S/$name" -maxdepth 1 -name 'f[0-9]*.png' ! -name f000.png -delete
    log "MASTERS $m ok; frames 1.. deleted locally (f000 kept)"
  else log "ERROR masters $m"; fi
}

# patch <label> <final names (comma list)> -- <env/cmd...> (the shot's own final command with --out patch/<x>):
# renders only the cap region (KQ_BORDER_AUTO=1) and pastes it into each final master; a refused paste (the comp is
# not local) re-renders the whole still into final instead (the same command with --out final/<x>).
patch() {
  local label=$1 names=$2; shift 3
  local m="patch $label"
  done_mark "$m" && return 0
  rm -rf "$OUT/_border" "$OUT/patch/$label"; mkdir -p "$OUT/patch"
  local marker=$KQ_RENDER_OUT/logs/.patch-start; touch "$marker"
  wait_disk
  local t1=$(date +%s)
  run_locked "patch-$label" env KQ_BORDER_AUTO=1 "$@" || { log "SKIP-PATCH $label after an error"; return 1; }
  # the union of every border this run wrote
  local bj=$OUT/patch/$label.border.json
  python3 - "$bj" $(find "$OUT" -name '*.border.json' -newer "$marker" ! -path "$bj") <<'EOF'
import json, sys
out, fs = sys.argv[1], sys.argv[2:]
bs = [json.load(open(f))["border"] for f in fs]
b = [min(x[0] for x in bs), max(x[1] for x in bs), min(x[2] for x in bs), max(x[3] for x in bs)]
json.dump(dict(border=b), open(out, "w")); print("union of", len(fs), b)
EOF
  local refused=0
  IFS=, read -ra NA <<< "$names"
  for nm in "${NA[@]}"; do
    local res
    res=$($PY "$KIT/patch_paste.py" -- "$OUT/patch/$nm" "$F/$nm" "$bj" 2>&1 | grep -E "RING|REFUSED|PASTED|MISMATCH|Error" | tr '\n' ' ')
    log "PATCH $label $nm $res"
    [[ "$res" == *PASTED* ]] || refused=1
  done
  log "PATCH-TIME $label $(( $(date +%s) - t1 )) s"
  if [ $refused -eq 1 ]; then
    log "PATCH-FALLBACK $label: full re-render into final"
    local args=() a
    for a in "$@"; do args+=("${a/patch\//final/}"); done
    run_locked "full-$label" "${args[@]}" || { log "SKIP full $label"; return 1; }
  fi
  mark "$m"
  sleep "$PAUSE"
}

log "QUEUE-START kit $KIT lock $LOCK free $(free_mb) MB"
NG="env KQ_NOGRIP=1"
NG15="env KQ_NOGRIP=1 KQ_EDGE_MM=1.5"
P1C="0.20 0.82 0.48 0.95"   # K01 portrait region (as queue-swivels.sh)
D1C="0.27 0.73 0.19 1.0"    # K01 desktop region
PACE="--feel pace --set P_FOLLOW=0.85"

# ---------------------------------------------------------------- P1: Naked
if want p1a; then  # K01 Naked hero stills: 5K beam (base, full, finale) and the 2160 portrait, both feels
  log "ITEM-START p1a"
  still K01-beam-nogrip-v5k "$F/K01-hero-beam-nogrip-v5k-full.png" "$F/passes/K01-hero-beam-nogrip-v5k" -- $PY shots/K01-hero-beam.py --feel command --set NOGRIP=1 --w 5120 --h 2880 --spp 64 --out final/K01-hero-beam-nogrip-v5k
  still K01-phone-nogrip-v5k "$F/K01-hero-frame-phone-nogrip-v5k-full.png" "$F/passes/K01-hero-frame-phone-nogrip-v5k" -- $PY shots/K01-hero-frame.py --feel command --set NOGRIP=1 --w 2160 --h 3840 --spp 48 --out final/K01-hero-frame-phone-nogrip-v5k
  if [ -f "$F/K01-hero-beam-nogrip-v5k-full.png" ] && [ -f "$F/K01-hero-frame-phone-nogrip-v5k-full.png" ]; then
    masters "m-k01-nogrip-c" stills/K01 "K01 Naked (carbon butt) Command: 5120 beam base/full/finale, 2160 portrait (2026-11-03)" "$F"/K01-hero-beam-nogrip-v5k-{base,full,finale}.png "$F"/K01-hero-frame-phone-nogrip-v5k-{base,full}.png
    export_stills "x-k01-nogrip-c" "K01 Naked in Command (owner, 3 Nov: 100 % carbon): the butt is the shell's white 3K carbon with the Q engraved, no black cap; desktop master 5120 x 2880 (5K screens), portrait 2160" K01-nogrip-base K01-nogrip-full K01-nogrip-finale K01-nogrip-hero-base-phone K01-nogrip-hero-full-phone
  fi
  still K01-beam-nogrip-pace-v5k "$F/K01-hero-beam-nogrip-pace-v5k-full.png" "$F/passes/K01-hero-beam-nogrip-pace-v5k" -- $PY shots/K01-hero-beam.py --feel pace --set NOGRIP=1 --w 5120 --h 2880 --spp 64 --out final/K01-hero-beam-nogrip-pace-v5k
  still K01-phone-nogrip-pace-v5k "$F/K01-hero-frame-phone-nogrip-pace-v5k-full.png" "$F/passes/K01-hero-frame-phone-nogrip-pace-v5k" -- $PY shots/K01-hero-frame.py --feel pace --set NOGRIP=1 --w 2160 --h 3840 --spp 48 --out final/K01-hero-frame-phone-nogrip-pace-v5k
  if [ -f "$F/K01-hero-beam-nogrip-pace-v5k-full.png" ] && [ -f "$F/K01-hero-frame-phone-nogrip-pace-v5k-full.png" ]; then
    masters "m-k01-nogrip-p" stills/K01 "K01 Naked (carbon butt) Pace: 5120 beam base/full/finale, 2160 portrait (2026-11-03)" "$F"/K01-hero-beam-nogrip-pace-v5k-{base,full,finale}.png "$F"/K01-hero-frame-phone-nogrip-pace-v5k-{base,full}.png
    export_stills "x-k01-nogrip-p" "K01 Naked in Pace: the butt is the shell's black 12K carbon with the Q engraved; desktop master 5120 x 2880, portrait 2160" K01-nogrip-base-pace K01-nogrip-full-pace K01-nogrip-finale-pace K01-nogrip-hero-base-phone-pace K01-nogrip-hero-full-phone-pace
  fi
  log "ITEM-DONE p1a"
fi

if want p1b; then  # the other twins: the cap region re-rendered Naked and pasted (else a full re-render)
  log "ITEM-START p1b"
  if [ -f "$OUT/patch/K08-feel-pair-nogrip.png" ] && ! done_mark "patch K08"; then   # rendered whole during the kit test
    cp "$OUT/patch/K08-feel-pair-nogrip.png" "$F/K08-feel-pair-nogrip.png"; mark "patch K08"; log "PATCH K08 whole render copied to final"
  fi
  patch K02c K02-edge-line-nogrip.png -- $NG15 $PY shots/K02-edge-line.py --w 2560 --h 1440 --spp 128 --set HD=0 --out patch/K02-edge-line-nogrip
  patch K02p K02-edge-line-nogrip-pace.png -- $NG15 $PY shots/K02-edge-line.py --feel pace --w 2560 --h 1440 --spp 128 --set HD=0 --out patch/K02-edge-line-nogrip-pace
  patch K12c K12-sweet-spot-nogrip-base.png,K12-sweet-spot-nogrip-full.png -- $NG $PY shots/K12-sweet-spot.py --set FIELD_INSET=C.FACE_INSET --w 3200 --h 1800 --spp 160 --out patch/K12-sweet-spot-nogrip
  patch K11sc K11-single-nogrip.png -- $NG15 $PY shots/K11-single.py --w 3200 --h 1800 --spp 256 --out patch/K11-single-nogrip
  patch K11sp K11-single-nogrip-pace.png -- $NG15 $PY shots/K11-single.py --feel pace --w 3200 --h 1800 --spp 256 --out patch/K11-single-nogrip-pace
  patch K11pc K11-pair-nogrip-command.png -- $NG15 $PY shots/K11-pair.py --weave command --w 3200 --h 1800 --spp 256 --out patch/K11-pair-nogrip-command
  patch K11pp K11-pair-nogrip-pace.png -- $NG15 $PY shots/K11-pair.py --weave pace --w 3200 --h 1800 --spp 256 --out patch/K11-pair-nogrip-pace
  patch K06c K06-mould-nogrip-base.png,K06-mould-nogrip-full.png -- $NG15 $PY shots/K06-mould.py --w 3200 --h 1800 --spp 160 --out patch/K06-mould-nogrip
  patch K06p K06-mould-nogrip-pace-base.png,K06-mould-nogrip-pace-full.png -- $NG15 $PY shots/K06-mould.py --feel pace --w 3200 --h 1800 --spp 160 --out patch/K06-mould-nogrip-pace
  patch K07 K07-lineup-five-nogrip.png -- $NG15 $PY shots/K07-lineup-five.py --w 2560 --h 1440 --spp 160 --seq --out patch/K07-lineup-five-nogrip
  masters "m-twins" stills/twins-naked "Naked twins (carbon butt, 2026-11-03): K02, K06, K07, K08, K11, K12" $(ls "$F"/K02-edge-line-nogrip*.png "$F"/K06-mould-nogrip-*base.png "$F"/K06-mould-nogrip-*full.png "$F"/K07-lineup-five-nogrip.png "$F"/K08-feel-pair-nogrip.png "$F"/K11-*-nogrip*.png "$F"/K12-sweet-spot-nogrip-base.png 2>/dev/null | grep -v "_card\|_view")
  export_stills "x-twins" "Naked twins (owner, 3 Nov: 100 % carbon): the butt is the shell's carbon with the Q engraved, no black cap, in K02, K06, K07, K08, K11 and K12" K02-nogrip K02-nogrip-pace K06-nogrip-base K06-nogrip-full K06-nogrip-base-pace K06-nogrip-full-pace K07-nogrip K08-nogrip K11-nogrip-command K11-nogrip-pace K11-nogrip-command-pace K11-nogrip-single K11-nogrip-single-pace K12-nogrip-base
  log "ITEM-DONE p1b"
fi

if want p1c; then  # the missing twins K09 and K10 (whole renders; K05 comes with its new master, P3)
  log "ITEM-START p1c"
  still K09g-nogrip "$F/K09-case-three-gallery-nogrip.v3.done" - -- sh -c "$NG15 $PY shots/K09-case-three.py --variant gallery --w 2400 --h 1800 --spp 160 --out final/K09-case-three-gallery-nogrip && touch $F/K09-case-three-gallery-nogrip.v3.done"
  still K09c-nogrip "$F/K09-case-three-card-nogrip.png" - -- $NG15 $PY shots/K09-case-three.py --variant card --hover-mix --w 1440 --h 1800 --spp 160 --out final/K09-case-three-card-nogrip
  still K09gp-nogrip "$F/K09-case-three-gallery-nogrip-pace.png" - -- $NG15 $PY shots/K09-case-three.py --feel pace --variant gallery --w 2400 --h 1800 --spp 160 --out final/K09-case-three-gallery-nogrip-pace
  still K09cp-nogrip "$F/K09-case-three-card-nogrip-pace.png" - -- $NG15 $PY shots/K09-case-three.py --feel pace --variant card --hover-mix --w 1440 --h 1800 --spp 160 --out final/K09-case-three-card-nogrip-pace
  still K10-nogrip "$F/K10-throat-serial-nogrip.png" - -- $NG15 $PY shots/K10-throat-serial.py --w 3200 --h 1800 --spp 256 --noise 0.008 --out final/K10-throat-serial-nogrip
  still K10p-nogrip "$F/K10-throat-serial-nogrip-pace.png" - -- $NG15 $PY shots/K10-throat-serial.py --feel pace --w 3200 --h 1800 --spp 256 --noise 0.008 --out final/K10-throat-serial-nogrip-pace
  masters "m-k09k10" stills/twins-naked "Naked twins K09 (gallery, card) and K10, both feels (2026-11-03)" $(ls "$F"/K09-case-three-*nogrip*.png "$F"/K10-throat-serial-nogrip*.png 2>/dev/null)
  export_stills "x-k09k10" "Naked twins K09 (case of three, gallery and card) and K10 (throat), both feels: carbon butts, no overgrip" K09-nogrip K09-nogrip-card K09-nogrip-pace K09-nogrip-card-pace K10-nogrip K10-nogrip-pace
  log "ITEM-DONE p1c"
fi

# ---------------------------------------------------------------- P2: the light-sweep swivels (Command first)
if want p2a; then  # Command, grip: 5K beam stills + portrait still (the sweep scene at t = 0), then both swivels
  log "ITEM-START p2a"
  still K01-beam-v5k "$F/K01-hero-beam-v5k-full.png" "$F/passes/K01-hero-beam-v5k" -- $PY shots/K01-hero-beam.py --feel command --w 5120 --h 2880 --spp 64 --out final/K01-hero-beam-v5k
  still K01-phone-v5k "$F/K01-hero-frame-phone-v5k-full.png" "$F/passes/K01-hero-frame-phone-v5k" -- $PY shots/K01-hero-frame.py --feel command --w 2160 --h 3840 --spp 48 --out final/K01-hero-frame-phone-v5k
  seq K01-swivel-command-phone 36 $P1C "$F/K01-hero-frame-phone-v5k-full.png" -- $PY shots/K01-hero-frame.py --feel command --w 2160 --h 3840 --spp 24 --seq 36 --yaw-range 0 35 --crop $P1C --out seq4/K01-swivel-command-phone
  seq K01-swivel-command-desktop 36 $D1C "$F/K01-hero-beam-v5k-full.png" -- $PY shots/K01-hero-beam.py --feel command --w 5120 --h 2880 --spp 16 --seq 36 --yaw-range 0 35 --crop $D1C --out seq4/K01-swivel-command-desktop
  if [ "$(ls $S/K01-swivel-command-phone | grep -c '^f[0-9]*\.png$')" -ge 36 ] && [ "$(ls $S/K01-swivel-command-desktop | grep -c '^f[0-9]*\.png$')" -ge 36 ]; then
    masters "m-k01-c" stills/K01 "K01 Command 5120 beam + 2160 portrait, light-sweep scene (2026-11-03)" "$F"/K01-hero-beam-v5k-{base,full,finale}.png "$F"/K01-hero-frame-phone-v5k-{base,full}.png
    export_stills "x-k01-c" "K01 Command: desktop master 5120 x 2880 (5K screens), portrait re-rendered in the light-sweep scene (frame 0 of the new swivel)" K01-base K01-full K01-finale K01-hero-base-phone K01-hero-full-phone
    export_seq "xs-k01-c" "K01 swivel, Command: the light sweep (a soft band crosses the face and frame as it turns), desktop to 5120 wide" K01-swivel-command-phone K01-swivel-command-desktop
    seq_masters K01-swivel-command-phone $P1C
    seq_masters K01-swivel-command-desktop $D1C
  fi
  log "ITEM-DONE p2a"
fi

if want p2b; then  # Command, Naked swivels (frame 0 = the p1a stills)
  log "ITEM-START p2b"
  seq K01-swivel-nogrip-command-phone 36 $P1C "$F/K01-hero-frame-phone-nogrip-v5k-full.png" -- $PY shots/K01-hero-frame.py --feel command --set NOGRIP=1 --w 2160 --h 3840 --spp 24 --seq 36 --yaw-range 0 35 --crop $P1C --out seq4/K01-swivel-nogrip-command-phone
  seq K01-swivel-nogrip-command-desktop 36 $D1C "$F/K01-hero-beam-nogrip-v5k-full.png" -- $PY shots/K01-hero-beam.py --feel command --set NOGRIP=1 --w 5120 --h 2880 --spp 16 --seq 36 --yaw-range 0 35 --crop $D1C --out seq4/K01-swivel-nogrip-command-desktop
  if [ "$(ls $S/K01-swivel-nogrip-command-phone | grep -c '^f[0-9]*\.png$')" -ge 36 ] && [ "$(ls $S/K01-swivel-nogrip-command-desktop | grep -c '^f[0-9]*\.png$')" -ge 36 ]; then
    export_seq "xs-k01-nc" "K01 Naked swivel, Command (the site's K01-swivel-nogrip): the carbon butt turning, with the light sweep; desktop to 5120 wide" K01-swivel-nogrip-command-phone K01-swivel-nogrip-command-desktop
    seq_masters K01-swivel-nogrip-command-phone $P1C
    seq_masters K01-swivel-nogrip-command-desktop $D1C
  fi
  log "ITEM-DONE p2b"
fi

if want p2c; then  # Pace, grip: stills (note-7 weave) + swivels (the cards follow 85 % of the turn)
  log "ITEM-START p2c"
  still K01-beam-pace-v5k "$F/K01-hero-beam-pace-v5k-full.png" "$F/passes/K01-hero-beam-pace-v5k" -- $PY shots/K01-hero-beam.py --feel pace --w 5120 --h 2880 --spp 64 --out final/K01-hero-beam-pace-v5k
  still K01-phone-pace-v5k "$F/K01-hero-frame-phone-pace-v5k-full.png" "$F/passes/K01-hero-frame-phone-pace-v5k" -- $PY shots/K01-hero-frame.py --feel pace --w 2160 --h 3840 --spp 48 --out final/K01-hero-frame-phone-pace-v5k
  seq K01-swivel-pace-phone 36 $P1C "$F/K01-hero-frame-phone-pace-v5k-full.png" -- $PY shots/K01-hero-frame.py $PACE --w 2160 --h 3840 --spp 24 --seq 36 --yaw-range 0 35 --crop $P1C --out seq4/K01-swivel-pace-phone
  seq K01-swivel-pace-desktop 36 $D1C "$F/K01-hero-beam-pace-v5k-full.png" -- $PY shots/K01-hero-beam.py $PACE --w 5120 --h 2880 --spp 16 --seq 36 --yaw-range 0 35 --crop $D1C --out seq4/K01-swivel-pace-desktop
  if [ "$(ls $S/K01-swivel-pace-phone | grep -c '^f[0-9]*\.png$')" -ge 36 ] && [ "$(ls $S/K01-swivel-pace-desktop | grep -c '^f[0-9]*\.png$')" -ge 36 ]; then
    masters "m-k01-p" stills/K01 "K01 Pace 5120 beam + 2160 portrait, light-sweep scene, note-7 weave (2026-11-03)" "$F"/K01-hero-beam-pace-v5k-{base,full,finale}.png "$F"/K01-hero-frame-phone-pace-v5k-{base,full}.png
    export_stills "x-k01-p" "K01 Pace: desktop master 5120 x 2880, portrait re-rendered in the light-sweep scene with the note-7 12K weave" K01-base-pace K01-full-pace K01-finale-pace K01-hero-base-phone-pace K01-hero-full-phone-pace
    export_seq "xs-k01-p" "K01 swivel, Pace: the light sweep across the black 12K, desktop to 5120 wide" K01-swivel-pace-phone K01-swivel-pace-desktop
    seq_masters K01-swivel-pace-phone $P1C
    seq_masters K01-swivel-pace-desktop $D1C
  fi
  log "ITEM-DONE p2c"
fi

if want p2d; then  # Pace, Naked swivels
  log "ITEM-START p2d"
  seq K01-swivel-nogrip-pace-phone 36 $P1C "$F/K01-hero-frame-phone-nogrip-pace-v5k-full.png" -- $PY shots/K01-hero-frame.py $PACE --set NOGRIP=1 --w 2160 --h 3840 --spp 24 --seq 36 --yaw-range 0 35 --crop $P1C --out seq4/K01-swivel-nogrip-pace-phone
  seq K01-swivel-nogrip-pace-desktop 36 $D1C "$F/K01-hero-beam-nogrip-pace-v5k-full.png" -- $PY shots/K01-hero-beam.py $PACE --set NOGRIP=1 --w 5120 --h 2880 --spp 16 --seq 36 --yaw-range 0 35 --crop $D1C --out seq4/K01-swivel-nogrip-pace-desktop
  if [ "$(ls $S/K01-swivel-nogrip-pace-phone | grep -c '^f[0-9]*\.png$')" -ge 36 ] && [ "$(ls $S/K01-swivel-nogrip-pace-desktop | grep -c '^f[0-9]*\.png$')" -ge 36 ]; then
    export_seq "xs-k01-np" "K01 Naked swivel, Pace: the black 12K carbon butt turning, with the light sweep; desktop to 5120 wide" K01-swivel-nogrip-pace-phone K01-swivel-nogrip-pace-desktop
    seq_masters K01-swivel-nogrip-pace-phone $P1C
    seq_masters K01-swivel-nogrip-pace-desktop $D1C
  fi
  log "ITEM-DONE p2d"
fi

log "ALL-DONE free $(free_mb) MB"
