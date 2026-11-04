#!/usr/bin/env bash
# queue_lib.sh (2026-11-03): the render queue's functions (still, seq, patch, export_stills, export_seq, masters,
# seq_masters), shared by queue-nov3b.sh and later queues; queue-nov3.sh carries its own copy (it was running when this
# was split out: never edit a running bash script). Source it after setting QNAME (log and marker names).
set -u
KIT=$(cd "$(dirname "$0")" && pwd)
cd "$KIT"
export KQ_RENDER_OUT=${KQ_RENDER_OUT:-/home/user/kinetiq-render-out}
PY=$KQ_RENDER_OUT/bpyenv/bin/python
if [ "$(uname -s)" = Darwin ]; then   # the Mac render node (2026-11-04, notes/mac-handoff.md)
  command -v setsid >/dev/null || PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/macos:$PATH"   # macOS has no setsid(1); flock: brew install flock
  PATH="$KQ_RENDER_OUT/bpyenv/bin:$PATH"   # python3 for the checks (numpy, Pillow) is the kit's venv
  KQ_DF_PATH=${KQ_DF_PATH:-$KQ_RENDER_OUT}   # / is the read-only system volume
  KQ_RETRY=${KQ_RETRY:-2}   # Metal kernel-compile aborts (run_locked)
fi
OUT=$KQ_RENDER_OUT/out
F=$OUT/final
S=$OUT/seq4
LOGD=$KQ_RENDER_OUT/logs/${QNAME:-queue-nov3}
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
free_mb() { df -Pm "${KQ_DF_PATH:-/}" | awk 'NR==2{print $4}'; }
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
# A render killed by a signal (exit >= 128: Blender 4.2.0's Metal kernel compile thread aborts now and then, NSException
# in MetalKernelPipeline::compile, 2026-11-04) is run again up to KQ_RETRY times (default 0; 2 on Darwin); a Python
# error (exit 1) is deterministic and is not retried.
run_locked() {
  local label=$1; shift
  local blog="$LOGD/$label.log" try=0 rc pid
  while :; do
    setsid flock "$LOCK" "$@" >> "$blog" 2>&1 &
    pid=$!
    while kill -0 "$pid" 2>/dev/null; do
      if [ "$(free_mb)" -lt "$STOP_MB" ]; then
        log "STOP-DISK free $(free_mb) MB < $STOP_MB MB during $label: killing it"
        kill -TERM -- "-$pid" 2>/dev/null; sleep 5; kill -KILL -- "-$pid" 2>/dev/null
        exit 3
      fi
      sleep 10
    done
    wait "$pid"
    rc=$?
    if [ $rc -ge 128 ] && [ $try -lt "${KQ_RETRY:-0}" ]; then
      try=$((try + 1)); log "RETRY $label after exit $rc ($try of $KQ_RETRY; see $blog)"; sleep 10; continue
    fi
    break
  done
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
  [ "${KQ_NO_EXPORT:-0}" = 1 ] && { log "EXPORT-SKIP $m (KQ_NO_EXPORT=1: the cloud exports)"; return 0; }
  if "$KIT/export_push.sh" stills "$msg" "$@" >> "$LOGD/export.log" 2>&1; then mark "$m"; log "EXPORT $m ok"; else log "ERROR export $m (see $LOGD/export.log)"; fi
}

export_seq() {      # export_seq <marker> "<msg>" <names...>
  local m=$1 msg=$2; shift 2
  done_mark "$m" && return 0
  [ "${KQ_NO_EXPORT:-0}" = 1 ] && { log "EXPORT-SKIP $m (KQ_NO_EXPORT=1: the cloud exports)"; return 0; }
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

