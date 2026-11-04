#!/usr/bin/env bash
# req-k03-base.sh (2026-11-05, the Mac render node): answers the cloud's request in STATUS-mac.md
#   "REQUEST 2026-11-04T14:09:09Z K03-base": K03's base pass (the render without lg_shell, the baked 2700 K amber
#   hairline) in both feels, with the README final command unchanged (camera, k03s_rig, geometry: the SealedCoreTrace
#   registers), no k03s_line.py step. Pushes stills/K03/K03-section-cut{,-pace}-{base,full}.png (16-bit 3200 x 1800;
#   the fulls only so the cloud can check the base registers with the site's K03), then a STATUS line and a
#   "DONE K03-base" line. Resumable (stills on disk, markers in logs/queue-nov3.done). Run detached:
#   nohup caffeinate -dimsu render/req-k03-base.sh >> ~/kinetiq-render/out/logs/queue-mac.log 2>&1 &
if [ "${BASH_VERSINFO[0]}" -lt 5 ] && [ -x /opt/homebrew/bin/bash ]; then exec /opt/homebrew/bin/bash "$0" "$@"; fi
export KQ_RENDER_OUT=${KQ_RENDER_OUT:-$HOME/kinetiq-render/out}
export KQ_LOCK=${KQ_LOCK:-$HOME/kinetiq-render/render.lock}
export RENDER_ROOT=${RENDER_ROOT:-$(cd "$(dirname "$0")" && pwd)}
export KQ_DEVICE=${KQ_DEVICE:-METAL}
export KQ_NO_EXPORT=1
QNAME=queue-mac
. "$(cd "$(dirname "$0")" && pwd)/queue_lib.sh"
DEVNAME="M3Max-$KQ_DEVICE"
REQ=K03-base
st() {   # st <marker> <line>: one STATUS-mac.md line, once
  done_mark "$1" && return 0
  if "$KIT/status_push.sh" "$2" >> "$LOGD/status.log" 2>&1; then mark "$1"; log "STATUS $1 ok: $2"
  else log "ERROR $1 (see $LOGD/status.log)"; return 1; fi
}
log "REQ-START $REQ device $KQ_DEVICE free $(free_mb) MB"
t0=$(date +%s)
C=K03-section-cut
still "$C-v6" "$F/$C-base.png" - -- env PYTHONHASHSEED=0 $PY shots/K03-section-cut.py --w 3200 --h 1800 --spp 320 --both --out "final/$C"
still "$C-pace-v6" "$F/$C-pace-base.png" - -- env PYTHONHASHSEED=0 $PY shots/K03-section-cut.py --feel pace --w 3200 --h 1800 --spp 320 --both --out "final/$C-pace"
for x in "$C" "$C-pace"; do
  for v in base full; do [ -f "$F/$x-$v.png" ] || { log "REQ-FAIL $REQ: $F/$x-$v.png missing"; exit 1; }; done
done
[ "${PUSH:-1}" = 0 ] && { log "REQ-RENDERED $REQ (PUSH=0: not pushed) $(( $(date +%s) - t0 )) s"; exit 0; }
masters "m-mac-k03-base" stills/K03 "K03 base pass (no lg_shell hairline) + full, both feels, 3200x1800 spp 320, README final command, no k03s_line step (request $REQ, $(date -u +%F), Mac M3 Max $KQ_DEVICE)" \
  "$F/$C"-{base,full}.png "$F/$C-pace"-{base,full}.png
done_mark "m-mac-k03-base" || { log "REQ-FAIL $REQ: masters push missing (see $LOGD/masters.log)"; exit 1; }
secs=$(( $(date +%s) - t0 ))
st "status $REQ" "$(date -u +%FT%TZ) $REQ stills/K03/$C{,-pace}-{base,full}.png $((secs / 3600))h$(printf %02d $((secs % 3600 / 60)))m $DEVNAME K03 v6 both feels 3200x1800 spp 320 --both (PYTHONHASHSEED=0), base = the light-group pass without lg_shell as rendered (no k03s_line.py); fulls = the same render's composite without the k03s_line hairline overlay, for the registration check${REG_NOTE:+; $REG_NOTE}; render time this run" || exit 1
st "done $REQ" "$(date -u +%FT%TZ) DONE $REQ (request 2026-11-04T14:09:09Z): stills/K03/$C{,-pace}-{base,full}.png" || exit 1
log "REQ-DONE $REQ"
