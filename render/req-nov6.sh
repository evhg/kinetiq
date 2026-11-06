#!/usr/bin/env bash
# req-nov6.sh (2026-11-06, the Mac render node): answers four cloud requests in STATUS-mac.md (2026-11-06):
#   K05-command-fix (09:33:40, supersedes K05-command-brighter, first): v7 Command fails on seven points (grey face, the
#     coat band's hard stripe, a red glow in the crossed hole, the laser over the holes, the profile wake, speckle in
#     the bores, the Naked butt's lip and flat handle). Fix: notes/k05-v7.args v7c (each item there), Pace's 3-6 in
#     notes/k05-v7-pace.args, Naked: K01's HD weave on the handle and KQ_NAKED_FLARE=0. One render per variant at
#     5760x3240 (Command, Pace, both Naked), which also answers K05 in wider-5k-masters; face luma vs v6 in STATUS.
#   K05-command-brighter (08:57:08, superseded; its lw_card is item 1 of the fix): v7's raking key leaves the crown-side half of the white Command face mid-to-dark grey; lift
#     it (Command only), same camera and crops, 5120x2880, grip and Naked. Fix: lw_card (notes/k05-v7.args --wcard 40),
#     a soft overhead spot on that half, diffuse only, head only; the coat band, laser and scan lines are untouched.
#   wider-5k-masters: K04 at 6400x3600, K05 (Command, Pace, Naked twins, with the brighter Command) and K17 (both feels)
#     at 5760x3240, same cameras and looks. K05's -master.png (the taller frame both crops are cut from) is about
#     110 MB at 5760, over GitHub's 100 MB file limit: it stays on the Mac; the desktop and -phone crops are pushed.
#   K03-5k-and-K03b: K03 (base and full, --both) and K03b at 5120x2880, both feels, PYTHONHASHSEED=0, same rig. Also the
#     hairline at 5120: the line mask (K03-section-cut.py --line_mask --shell_w 0.55 --shell_tail 0.32) and the
#     k03s_line.py composites (-line.png = base + the amber hairline, the site's K03 / K03b; sigma 8 = 5 x 5120/3200).
# PUSH=0 renders and stops (look first); then run again without it (renders are skipped when on disk).
#   nohup caffeinate -dimsu render/req-nov6.sh >> ~/kinetiq-render/out/logs/queue-mac.log 2>&1 &
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
V=$F/v5k
W57=$F/w5760
W64=$F/w6400
mkdir -p "$W57" "$W64"
NG="env KQ_NOGRIP=1"
NGF="env KQ_NOGRIP=1 KQ_NAKED_FLARE=0"   # K05 Naked: no flare (seen from straight above it read as a lip)
R0=K05-command-fix R0T=2026-11-06T09:33:40Z R1=K05-command-brighter R2=wider-5k-masters R3=K03-5k-and-K03b RT=2026-11-06T08:57:08Z
hm() { printf '%dh%02dm' $(($1 / 3600)) $(($1 % 3600 / 60)); }
st() {   # st <marker> <line>
  done_mark "$1" && return 0
  if "$KIT/status_push.sh" "$2" >> "$LOGD/status.log" 2>&1; then mark "$1"; log "STATUS $1 ok: ${2:0:160}"
  else log "ERROR $1 (see $LOGD/status.log)"; return 1; fi
}
TM=$LOGD/req-nov6.times
tm() { [ "$2" -gt 30 ] && echo "$1 $2" >> "$TM"; true; }   # render time per group, kept for the push run
tg() { local v; v=$(awk -v k="$1" '$1==k{v=$2}END{print v+0}' "$TM" 2>/dev/null); hm "${v:-0}"; }
need() { local f; for f in "$@"; do [ -f "$f" ] || { log "REQ-FAIL $f missing"; return 1; }; done; }
args() { grep -v '^#' "$1" | tr '\n' ' '; }
A=$(args "$KIT/notes/k05-v7.args")
AP=$(args "$KIT/notes/k05-v7-pace.args")
log "REQ-START $R1 + $R2 + $R3 device $KQ_DEVICE free $(free_mb) MB push $PUSH"

# ---------------------------------------------------------------- renders
# K05 v7c at 5760 (the v7b previews of this morning, same paths, move aside once so still() renders them again)
OLD=$W57/pre-fix-20261106
if ! done_mark "k05c moved old"; then
  mkdir -p "$OLD"
  for f in "$W57"/K05-laser-scan*.png; do [ -e "$f" ] && mv "$f" "$OLD"/; done
  mark "k05c moved old"
fi
t0=$(date +%s)
still K05c "$W57/K05-laser-scan.png" - -- $PY shots/K05-laser-scan.py $A --w 5760 --h 3240 --spp 96 --out final/w5760/K05-laser-scan
still K05cn "$W57/K05-laser-scan-nogrip.png" - -- $NGF $PY shots/K05-laser-scan.py $A --w 5760 --h 3240 --spp 96 --out final/w5760/K05-laser-scan-nogrip
still K05cp "$W57/K05-laser-scan-pace.png" - -- $PY shots/K05-laser-scan.py $AP --feel pace --w 5760 --h 3240 --spp 96 --out final/w5760/K05-laser-scan-pace
still K05cnp "$W57/K05-laser-scan-nogrip-pace.png" - -- $NGF $PY shots/K05-laser-scan.py $AP --feel pace --w 5760 --h 3240 --spp 96 --out final/w5760/K05-laser-scan-nogrip-pace
tm k05c $(( $(date +%s) - t0 )); t0=$(date +%s)
still K04w "$W64/K04-hole-macro-full.png" - -- $PY shots/K04-hole-macro.py --w 6400 --h 3600 --spp 112 --variant both --out final/w6400/K04-hole-macro
still K04wp "$W64/K04-hole-macro-pace-full.png" - -- $PY shots/K04-hole-macro.py --feel pace --w 6400 --h 3600 --spp 112 --variant both --out final/w6400/K04-hole-macro-pace
tm k04 $(( $(date +%s) - t0 )); t0=$(date +%s)
still K17w "$W57/K17-roughness.png" - -- $PY shots/K17-roughness.py --w 5760 --h 3240 --spp 48 --out final/w5760/K17-roughness
still K17wp "$W57/K17-roughness-pace.png" - -- $PY shots/K17-roughness.py --feel pace --w 5760 --h 3240 --spp 48 --out final/w5760/K17-roughness-pace
tm k17 $(( $(date +%s) - t0 )); t0=$(date +%s)

# K03 and K03b at 5120 (--both: base without lg_shell, full as rendered), the hairline mask, the -line composites
C=K03-section-cut B=K03b-tubular
still K03-5k "$V/$C-base.png" - -- env PYTHONHASHSEED=0 $PY shots/K03-section-cut.py --w 5120 --h 2880 --spp 320 --both --out final/v5k/$C
still K03p-5k "$V/$C-pace-base.png" - -- env PYTHONHASHSEED=0 $PY shots/K03-section-cut.py --feel pace --w 5120 --h 2880 --spp 320 --both --out final/v5k/$C-pace
still K03m-5k "$V/K03-line-mask.png" - -- env PYTHONHASHSEED=0 $PY shots/K03-section-cut.py --line_mask --shell_w 0.55 --shell_tail 0.32 --w 5120 --h 2880 --spp 1024 --out final/v5k/K03-line-mask
tm k03 $(( $(date +%s) - t0 )); t0=$(date +%s)
still K03b-5k "$V/$B-base.png" - -- env PYTHONHASHSEED=0 $PY shots/K03b-tubular.py --w 5120 --h 2880 --spp 320 --both --out final/v5k/$B
still K03bp-5k "$V/$B-pace-base.png" - -- env PYTHONHASHSEED=0 $PY shots/K03b-tubular.py --feel pace --w 5120 --h 2880 --spp 320 --both --out final/v5k/$B-pace
tm k03b $(( $(date +%s) - t0 ))
for s in $C $B; do
  for fe in "" -pace; do
    [ -z "$fe" ] && wl="--white 1 --tint 0.6" || wl="--white 0"
    still "line-$s$fe" "$V/$s$fe-line.png" - -- $PY shots/k03s_line.py "$V/K03-line-mask.png" "$V/$s$fe-base.png" "$V/$s$fe-line.png" --halo 0.9 --sigma 8 $wl
  done
done
need "$W57"/K05-laser-scan{,-pace,-nogrip,-nogrip-pace}{,-phone}.png \
  "$W64"/K04-hole-macro{,-pace}-{base,full}.png "$W57"/K17-roughness{,-base,-pace,-pace-base}.png \
  "$V"/{$C,$B}{,-pace}-{base,full,line}.png "$V/K03-line-mask.png" || exit 1
log "REQ-RENDERS-DONE free $(free_mb) MB"
[ "$PUSH" = 1 ] || { log "PUSH=0: stop before pushing"; exit 0; }

# ---------------------------------------------------------------- pushes, STATUS, DONE
OLD7=$V/K05-laser-scan.png; [ -f "$V/pre-brighter-20261106/K05-laser-scan.png" ] && OLD7=$V/pre-brighter-20261106/K05-laser-scan.png   # v7 as live
V6=$KQ_RENDER_OUT/logs/K05-v6-wide-2560.webp   # v6, live until Release 8 (evhg/kinetiq 9a51093^)
[ -f "$V6" ] || git -C "$KIT/.." show 9a51093^:public/stills/K05-wide-2560.5d3a212063.webp > "$V6" || exit 1
LUM=$($PY "$KIT/k05_face.py" "v6=$V6" "v7=$OLD7" "new=$W57/K05-laser-scan.png" "new Naked=$W57/K05-laser-scan-nogrip.png") || exit 1
log "K05 face luma $LUM"
FIX="v7c: (1) white across the face: lw_card (soft overhead spot on the crown-side half, diffuse only, head only, Command only) and fill 9 W; (2) the coat band (the hard stripe) off; (3)+(4) the laser breaks at every hole (no hits on bores or on stone seen through a hole) and the widest halo scale off (it filled the crossed hole with red); (5) no profile wake, the crisp scan line only; (6) no stone patch in the holes and an indirect clamp: dark bores; (7) Naked: K01's HD weave on the handle and no flare (KQ_NAKED_FLARE=0; seen from straight above the canon 1.9 mm flare read as a lip; K01 and the other Naked twins keep it); the camera, framing, crops and v7's sharp laser unchanged (at full size the laser's tight halo still touches the rim of a hole it crosses, nothing inside the hole); Pace: 3-6 applied (same laser rig), its face and lights unchanged"
masters "m-k05c" stills/K05 "K05 v7c 5760x3240: Command, Pace, Naked twins (requests $R0 and $R2; -master.png stays on the Mac, over 100 MB)" "$W57"/K05-laser-scan{,-pace,-nogrip,-nogrip-pace}{,-phone}.png
done_mark "m-k05c" || exit 1
st "status k05c" "$(date -u +%FT%TZ) $R0 stills/K05/K05-laser-scan{,-pace,-nogrip,-nogrip-pace}{,-phone}.png $(tg k05c) $DEVNAME K05 v7c 5760x3240 spp 96, desktop + phone from one master each (the -master.png files, about 110 MB, are over GitHub's 100 MB limit and stay on the Mac); mean display face luma at 2560 / 1440 (head box, luma > 70, laser out; k05_face.py): $LUM; $FIX; replaces the 5120 files at the same paths, use it for the 5120-crop export too; render time this run" || exit 1
st "done $R0" "$(date -u +%FT%TZ) DONE $R0 (request $R0T): stills/K05/K05-laser-scan{,-pace,-nogrip,-nogrip-pace}{,-phone}.png at 5760x3240" || exit 1
st "done $R1" "$(date -u +%FT%TZ) DONE $R1 (request $RT): superseded by $R0 (its soft card is the fix's item 1); no separate 5120 render" || exit 1
masters "m-k04w" stills/K04 "K04 6400x3600 both feels (request $R2)" "$W64"/K04-hole-macro{,-pace}-{base,full}.png
done_mark "m-k04w" || exit 1
st "status k04w" "$(date -u +%FT%TZ) $R2:K04 stills/K04/K04-hole-macro{,-pace}-{base,full}.png $(tg k04) $DEVNAME K04 6400x3600 spp 112 --variant both, both feels, same camera and look; replaces the 5120 files; render time this run" || exit 1
masters "m-k17w" stills/K17 "K17 5760x3240 both feels (request $R2)" "$W57"/K17-roughness{,-base,-pace,-pace-base}.png
done_mark "m-k17w" || exit 1
st "status k17w" "$(date -u +%FT%TZ) $R2:K17 stills/K17/K17-roughness{,-base,-pace,-pace-base}.png $(tg k17) $DEVNAME K17 5760x3240 spp 48, both feels, same camera and look (vs the 5120 masters at 1280: mean |dLuma| 1.2 Command, 2.3 Pace, the felt fibres and the weave moire); replaces the 5120 files; render time this run (the Mac slept 1h43 mid-render on a flat battery, not counted)" || exit 1
st "done $R2" "$(date -u +%FT%TZ) DONE $R2 (request $RT): K04 6400x3600 stills/K04, K05 5760x3240 stills/K05 (the v7c render of $R0; no -master: over 100 MB), K17 5760x3240 stills/K17; memory and time were no limit (48 GB, a few minutes each)" || exit 1

REGN=${REG_NOTE:-}
masters "m-k03-5k" stills/K03 "K03 v6 5120x2880 both feels: base, full, -line (base + hairline), line mask (request $R3)" "$V"/$C{,-pace}-{base,full,line}.png "$V/K03-line-mask.png"
done_mark "m-k03-5k" || exit 1
st "status k03-5k" "$(date -u +%FT%TZ) $R3:K03 stills/K03/K03-section-cut{,-pace}-{base,full,line}.png,stills/K03/K03-line-mask.png $(tg k03) $DEVNAME K03 v6 5120x2880 spp 320 --both PYTHONHASHSEED=0, both feels, same rig and camera; base = without lg_shell, full = as rendered, -line = base + k03s_line.py hairline from the 5120 mask (--line_mask --shell_w 0.55 --shell_tail 0.32; --halo 0.9 --sigma 8, Command --white 1 --tint 0.6, Pace --white 0) for the Unibody chapter; replaces the 3200 files${REGN:+; $REGN}; render time this run" || exit 1
masters "m-k03b-5k" stills/K03b "K03b 5120x2880 both feels: base, full, -line (request $R3)" "$V"/$B{,-pace}-{base,full,line}.png
done_mark "m-k03b-5k" || exit 1
st "status k03b-5k" "$(date -u +%FT%TZ) $R3:K03b stills/K03b/K03b-tubular{,-pace}-{base,full,line}.png $(tg k03b) $DEVNAME K03b 5120x2880 spp 320 --both PYTHONHASHSEED=0, both feels, the K03 rig and camera (registers with K03); -line = base + the same K03 hairline mask and settings; render time this run" || exit 1
st "done $R3" "$(date -u +%FT%TZ) DONE $R3 (request $RT): stills/K03 (K03 5120 base, full, -line, mask) and stills/K03b (K03b 5120 base, full, -line)" || exit 1
log "REQ-DONE $R1 + $R2 + $R3 free $(free_mb) MB"
