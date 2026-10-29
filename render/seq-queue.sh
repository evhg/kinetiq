#!/bin/bash
# Swivel finals queue (2026-10-29): one frame per lock acquisition, then a 5 s pause so other agents' jobs get the lock.
# Each line of the job file: <script> <args...>  (a --seq render; frames on disk are skipped by render_seq itself).
# Usage: render/seq-queue.sh <jobfile> (one job a line: <frames> <out dir under $KQ_RENDER_OUT/out> <script and args>); each job: frame 0, then the last frame, then the rest in order.
cd /home/user/kinetiq/render
export KQ_RENDER_OUT=/home/user/kinetiq-render-out
PY=$KQ_RENDER_OUT/bpyenv/bin/python
while read -r n outdir args; do
  [ -z "$n" ] && continue
  for i in 0 $((n-1)) $(seq 1 $((n-2))); do
    [ -f "$KQ_RENDER_OUT/out/$outdir/f$(printf %03d $i).png" ] && continue
    flock render.lock $PY $args --only $i
    sleep 5
  done
  echo "JOB-DONE $outdir"
done < "$1"
echo ALL-DONE
