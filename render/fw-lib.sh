# fw-lib.sh (2026-11-07, the Mac render node): shared header for the full-weave pass (cloud REQUEST full-weave, which
# folds in pace-naked-weave): every racket image re-rendered once with the full-weave canon (kq_canon HERO_WEAVE: K01's
# hero weave on every part of every racket, both feels; FRAME_UV wrap: the throat walls wrapped; k789_lib
# pace_handle_weave: the per-camera handle card on Naked handles, re-aimed every swivel frame; k01_lib GRIP_FOLLOW: the
# grip strips keep their place relative to the bare handle's mirror direction in Naked swivels).
# Sourced by the fw-<group>.sh scripts (run in page order by req-full-weave.sh); each is resumable (markers, files on
# disk). PUSH=0 renders only.
if [ "${BASH_VERSINFO[0]}" -lt 5 ] && [ -x /opt/homebrew/bin/bash ]; then exec /opt/homebrew/bin/bash "$0" "$@"; fi
export KQ_RENDER_OUT=${KQ_RENDER_OUT:-$HOME/kinetiq-render/out}
export KQ_LOCK=${KQ_LOCK:-$HOME/kinetiq-render/render.lock}
export RENDER_ROOT=${RENDER_ROOT:-$(cd "$(dirname "$0")" && pwd)}
export KQ_DEVICE=${KQ_DEVICE:-METAL}
export KQ_NO_EXPORT=1
QNAME=queue-mac
. "$(cd "$(dirname "$0")" && pwd)/queue_lib.sh"
DEVNAME="M3Max-$KQ_DEVICE"
PUSH=${PUSH:-1}
R=${FW_R:-full-weave} RT=${FW_RT:-2026-11-07T03:20:15Z}   # a later pass (one-racket.sh) reuses these scripts under its own tag
V=$F/v5k
OLD=${FW_OLD:-$F/pre-fullweave-20261107}
mkdir -p "$OLD"
NG="env KQ_NOGRIP=1"
NG15="env KQ_NOGRIP=1 KQ_EDGE_MM=1.5"
NGF="env KQ_NOGRIP=1 KQ_NAKED_FLARE=0"
CANON="full-weave canon (K01's hero weave on every part, both feels: Pace P_HD + crimp 75, white Command WEAVE_W + WEAVE_HD; the 1.0 mm edge radius's coat roughness alternating per tow / tape (RIM_FLIP 0.5, so the weave reads over the edge); throat walls on arc-length UVs; Naked handles lit by their per-camera handle card, the butt left out of it; every Naked twin without the butt flare, KQ_NAKED_FLARE 0 canon: the handle runs straight into the Q end with the weave to the end)"
[ -n "${FW_CANON:-}" ] && CANON="$FW_CANON, on the $CANON"
hm() { printf '%dh%02dm' $(($1 / 3600)) $(($1 % 3600 / 60)); }
st() {   # st <marker> <line>
  done_mark "$1" && return 0
  if "$KIT/status_push.sh" "$2" >> "$LOGD/status.log" 2>&1; then mark "$1"; log "STATUS $1 ok: ${2:0:160}"
  else log "ERROR $1 (see $LOGD/status.log)"; return 1; fi
}
need() { local f; for f in "$@"; do [ -f "$f" ] || { log "FW-FAIL $f missing"; return 1; }; done; }
aside() {   # aside <marker> <files or dirs...>: move the previous renders out of the way once, so still()/seq() redo them
  local m="fw aside $1"; shift
  done_mark "$m" && return 0
  local f; for f in "$@"; do [ -e "$f" ] && mv "$f" "$OLD"/; done
  mark "$m"
}
# held <key>: a shot held out of the pass (one key per line in render/fw-hold, e.g. k11 while a new look is previewed,
# cloud REQUEST k04-language 2026-11-07); the group goes on with its other shots and the held one is rendered later.
held() { grep -qx "$1" "$KIT/fw-hold" 2>/dev/null && { log "FW-HOLD $1 (render/fw-hold)"; return 0; }; return 1; }
unseq() { local n; for n in "$@"; do sed -i '' "/^seqmasters $n\$/d" "$DONE"; done; }   # seq_masters runs again
nf() { ls "$S/$1" 2>/dev/null | grep -c '^f[0-9]*\.png$'; }
