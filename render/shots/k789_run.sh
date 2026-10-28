#!/bin/bash
# usage: k789_run.sh <shot.py> <out-name-under-out/> [args...]; runs one Blender render, logs, fillchecks
# (recovered 2026-10-28; paths now from KQ_RENDER_OUT, see kqpaths.py)
cd "$(dirname "$0")/.."
OUTROOT="${KQ_RENDER_OUT:-/home/user/kinetiq-render-out}"
PY="${KQ_PY:-$OUTROOT/bpyenv/bin/python}"
shot=$1; out=$2; shift 2
log=$OUTROOT/out/${out}.log
mkdir -p $(dirname $log)
start=$(date +%s)
"$PY" shots/$shot --out $out "$@" > $log 2>&1
echo "exit $? in $(( $(date +%s) - start )) s" >> $log
grep -E "Error|error|Traceback|framing|rendered|exit" $log | grep -v "^Fra" | tail -8
[ -f $OUTROOT/out/${out}.png ] && "$PY" fillcheck.py $OUTROOT/out/${out}.png
