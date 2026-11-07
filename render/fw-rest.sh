#!/usr/bin/env bash
# fw-rest.sh: full-weave pass, every other racket image, each at its current master's size and recipe: K14 (edge macro),
# K16 (drilled / moulded pair), K06 (mould, grip and Naked), K07 (lineup, grip and Naked), K09 (case of three, gallery
# and card, grip and Naked), K10 (throat, grip and Naked), K12 (sweet spot), K04 (hole macro, 6400), K15 (space, cyl
# bores), K17 (roughness, 5760), K03 / K03b (section, 5120 + line mask + -line composites). One STATUS line per shot.
# FW_K14_ENV: extra env for K14 (its edge settings, chosen after the cloud's review of the preview).
. "$(cd "$(dirname "$0")" && pwd)/fw-lib.sh"
W57=$F/w5760 W64=$F/w6400
NGH="env KQ_NOGRIP=1 KQ_PACE_HANDLE=1"
NG15H="env KQ_NOGRIP=1 KQ_EDGE_MM=1.5 KQ_PACE_HANDLE=1"
log "FW-START rest device $KQ_DEVICE free $(free_mb) MB push $PUSH"
# shot <key> <masters dir> "<status text>" <files...>: masters push and STATUS for one shot once its files exist
shot() {
  local key=$1 dir=$2 txt=$3; shift 3
  need "$@" || return 1
  local tt=$(( $(date +%s) - T0 ))
  echo "$key $tt" >> "$LOGD/full-weave.times"
  [ "$PUSH" = 1 ] || { log "PUSH=0: $key rendered, not pushed"; return 0; }
  # GitHub refuses files over 100 MB (K14's EXRs at the full weave: 360 and 148 MB): those stay on the Mac, named in STATUS
  local keep=() big=() f; for f in "$@"; do
    if [ "$(stat -f %z "$f")" -gt 99000000 ]; then big+=("$(basename "$f")"); else keep+=("$f"); fi; done
  [ ${#big[@]} -gt 0 ] && { log "OVER-100MB kept on the Mac: ${big[*]}"; txt="$txt; kept on the Mac, over GitHub's 100 MB limit: ${big[*]} (the repo's copies are the previous render's)"; }
  set -- "${keep[@]}"
  masters "fw m $key" "$dir" "$key, $R ($CANON)" "$@"
  done_mark "fw m $key" || return 1
  local list=$(for f in "$@"; do printf '%s/%s,' "$dir" "$(basename "$f")"; done | sed 's/,$//')
  st "fw status $key" "$(date -u +%FT%TZ) $R:$key $list $(hm $tt) $DEVNAME $txt, with the $CANON; render time this run"
}
# ---- K14 (edge macro): 5120 spp 48, both feels
if ! done_mark "fw status k14"; then T0=$(date +%s)
  aside k14 "$V"/K14-edge{,-pace}{.png,.exr,.json,_bg.png}
  still fw-K14  "$V/K14-edge.png"      - -- env ${FW_K14_ENV:-KQ_X=1} $PY shots/K14-edge.py --w 5120 --h 2880 --spp 48 --out final/v5k/K14-edge
  still fw-K14p "$V/K14-edge-pace.png" - -- env ${FW_K14_ENV:-KQ_X=1} $PY shots/K14-edge.py --feel pace --w 5120 --h 2880 --spp 48 --out final/v5k/K14-edge-pace
  shot k14 stills/K14 "K14 edge macro 5120x2880 spp 48, both feels, same camera and crops${FW_K14_ENV:+ ($FW_K14_ENV)}" "$V"/K14-edge{,-pace}{.png,.exr,.json,_bg.png} || exit 1
fi
# ---- K16 (drilled vs moulded pair): halves 2560x2880 spp 64, combined, both feels
if ! done_mark "fw status k16"; then T0=$(date +%s)
  aside k16 "$V"/K16-{drilled,moulded,pair}{,-pace}-{base,full}.png "$V"/K16-drilled{,-pace}.exr "$V"/K16-moulded{,-pace}.exr
  still fw-K16d  "$V/K16-drilled-base.png"      - -- $PY shots/K16-pair.py --mode drilled --w 2560 --h 2880 --spp 64 --out final/v5k/K16-drilled
  still fw-K16m  "$V/K16-moulded-full.png"      - -- $PY shots/K16-pair.py --mode moulded --w 2560 --h 2880 --spp 64 --out final/v5k/K16-moulded
  still fw-K16c  "$V/K16-pair-full.png"         - -- $PY shots/K16-pair.py --combine final/v5k/K16-drilled final/v5k/K16-moulded --out final/v5k/K16-pair --gutter 0
  still fw-K16dp "$V/K16-drilled-pace-base.png" - -- $PY shots/K16-pair.py --feel pace --mode drilled --w 2560 --h 2880 --spp 64 --out final/v5k/K16-drilled-pace
  still fw-K16mp "$V/K16-moulded-pace-full.png" - -- $PY shots/K16-pair.py --feel pace --mode moulded --w 2560 --h 2880 --spp 64 --out final/v5k/K16-moulded-pace
  still fw-K16cp "$V/K16-pair-pace-full.png"    - -- $PY shots/K16-pair.py --feel pace --combine final/v5k/K16-drilled-pace final/v5k/K16-moulded-pace --out final/v5k/K16-pair-pace --gutter 0
  shot k16 stills/K16 "K16 drilled / moulded pair 5120x2880 (halves 2560x2880 spp 64), both feels" "$V"/K16-pair{,-pace}-{base,full}.png "$V"/K16-{drilled,moulded}{,-pace}-{base,full}.png || exit 1
fi
# ---- K06 (mould): 5120 spp 112, grip and Naked, both feels (no handle card: the comp scales by lg_cavity)
if ! done_mark "fw status k06"; then T0=$(date +%s)
  aside k06 "$V"/K06-mould{,-pace,-nogrip,-nogrip-pace}{,-base,-full}.png
  still fw-K06   "$V/K06-mould-full.png"             - -- $PY shots/K06-mould.py --w 5120 --h 2880 --spp 112 --out final/v5k/K06-mould
  still fw-K06p  "$V/K06-mould-pace-full.png"        - -- $PY shots/K06-mould.py --feel pace --w 5120 --h 2880 --spp 112 --out final/v5k/K06-mould-pace
  still fw-K06n  "$V/K06-mould-nogrip-full.png"      - -- $NG $PY shots/K06-mould.py --w 5120 --h 2880 --spp 112 --out final/v5k/K06-mould-nogrip
  still fw-K06np "$V/K06-mould-nogrip-pace-full.png" - -- $NG $PY shots/K06-mould.py --feel pace --w 5120 --h 2880 --spp 112 --out final/v5k/K06-mould-nogrip-pace
  shot k06 stills/K06 "K06 mould 5120x2880 spp 112, grip and Naked, both feels" "$V"/K06-mould{,-pace,-nogrip,-nogrip-pace}-{base,full}.png || exit 1
fi
# ---- K07 (lineup of five): 5120 spp 112 --seq, grip and Naked (the Pace Naked handles with their card)
if ! held k07 && ! done_mark "fw status k07"; then T0=$(date +%s)
  aside k07 "$V"/K07-lineup-five{,-nogrip}{,-seq0,-seq1,-seq2,-seq3,-seq4}.png
  still fw-K07  "$V/K07-lineup-five.png"        - -- $PY shots/K07-lineup-five.py --w 5120 --h 2880 --spp 112 --seq --out final/v5k/K07-lineup-five
  still fw-K07n "$V/K07-lineup-five-nogrip.png" - -- $NGH $PY shots/K07-lineup-five.py --w 5120 --h 2880 --spp 112 --seq --out final/v5k/K07-lineup-five-nogrip
  shot k07 stills/K07-K08 "K07 lineup 5120x2880 spp 112 --seq, grip and Naked" "$V"/K07-lineup-five{,-nogrip}{,-seq0,-seq1,-seq2,-seq3,-seq4}.png || exit 1
fi
# ---- K09 (case of three): gallery 2400x1800, card 1440x1800 --hover-mix, spp 160, grip and Naked, both feels
if ! held k09 && ! done_mark "fw status k09"; then T0=$(date +%s)
  G=K09-case-three
  aside k09 "$F/$G"-{gallery,card}{,-pace,-nogrip,-nogrip-pace}{.png,-check.png,-hover.png}
  for fe in command pace; do
    sfx=""; [ $fe = pace ] && sfx=-pace
    still fw-K09g$fe  "$F/$G-gallery$sfx.png"        - -- $PY shots/K09-case-three.py --feel $fe --variant gallery --w 2400 --h 1800 --spp 160 --out final/$G-gallery$sfx
    still fw-K09c$fe  "$F/$G-card$sfx.png"           - -- $PY shots/K09-case-three.py --feel $fe --variant card --hover-mix --w 1440 --h 1800 --spp 160 --out final/$G-card$sfx
    still fw-K09gn$fe "$F/$G-gallery-nogrip$sfx.png" - -- $NG15H $PY shots/K09-case-three.py --feel $fe --variant gallery --w 2400 --h 1800 --spp 160 --out final/$G-gallery-nogrip$sfx
    still fw-K09cn$fe "$F/$G-card-nogrip$sfx.png"    - -- $NG15H $PY shots/K09-case-three.py --feel $fe --variant card --hover-mix --w 1440 --h 1800 --spp 160 --out final/$G-card-nogrip$sfx
  done
  shot k09 stills/K09 "K09 case of three, gallery 2400x1800 and card 1440x1800 --hover-mix, spp 160, grip and Naked, both feels" $(ls "$F/$G"-{gallery,card}*.png 2>/dev/null) || exit 1
fi
# ---- K10 (throat serial): 3200x1800 spp 256 --noise 0.008, grip and Naked, both feels
if ! done_mark "fw status k10"; then T0=$(date +%s)
  aside k10 "$F"/K10-throat-serial{,-pace,-nogrip,-nogrip-pace}.png
  still fw-K10   "$F/K10-throat-serial.png"             - -- $PY shots/K10-throat-serial.py --w 3200 --h 1800 --spp 256 --noise 0.008 --out final/K10-throat-serial
  still fw-K10p  "$F/K10-throat-serial-pace.png"        - -- $PY shots/K10-throat-serial.py --feel pace --w 3200 --h 1800 --spp 256 --noise 0.008 --out final/K10-throat-serial-pace
  still fw-K10n  "$F/K10-throat-serial-nogrip.png"      - -- $NG15 $PY shots/K10-throat-serial.py --w 3200 --h 1800 --spp 256 --noise 0.008 --out final/K10-throat-serial-nogrip
  still fw-K10np "$F/K10-throat-serial-nogrip-pace.png" - -- $NG15 $PY shots/K10-throat-serial.py --feel pace --w 3200 --h 1800 --spp 256 --noise 0.008 --out final/K10-throat-serial-nogrip-pace
  shot k10 stills/K10 "K10 throat 3200x1800 spp 256, grip and Naked, both feels" "$F"/K10-throat-serial{,-pace,-nogrip,-nogrip-pace}.png || exit 1
fi
# ---- K12 (sweet spot): 3200x1800 spp 160, Command, Pace, Command Naked (base, full, phone crops)
if ! done_mark "fw status k12"; then T0=$(date +%s)
  aside k12 "$F"/K12-sweet-spot{,-pace,-nogrip}-{base,full,phone-base,phone-full,sheet}.png
  still fw-K12  "$F/K12-sweet-spot-full.png"        - -- $PY shots/K12-sweet-spot.py --w 3200 --h 1800 --spp 160 --out final/K12-sweet-spot
  still fw-K12p "$F/K12-sweet-spot-pace-full.png"   - -- $PY shots/K12-sweet-spot.py --feel pace --w 3200 --h 1800 --spp 160 --out final/K12-sweet-spot-pace
  still fw-K12n "$F/K12-sweet-spot-nogrip-full.png" - -- $NG $PY shots/K12-sweet-spot.py --w 3200 --h 1800 --spp 160 --out final/K12-sweet-spot-nogrip
  shot k12 stills/K12 "K12 sweet spot 3200x1800 spp 160, Command, Pace and Command Naked (base, full, phone crops)" $(ls "$F"/K12-sweet-spot{,-pace,-nogrip}-{base,full,phone-base,phone-full}.png 2>/dev/null) || exit 1
fi
# ---- K04 (hole macro): 6400x3600 spp 112 --variant both, both feels
if ! done_mark "fw status k04"; then T0=$(date +%s)
  aside k04 "$W64"/K04-hole-macro{,-pace}-{base,full}.png
  still fw-K04  "$W64/K04-hole-macro-full.png"      - -- $PY shots/K04-hole-macro.py --w 6400 --h 3600 --spp 112 --variant both --out final/w6400/K04-hole-macro
  still fw-K04p "$W64/K04-hole-macro-pace-full.png" - -- $PY shots/K04-hole-macro.py --feel pace --w 6400 --h 3600 --spp 112 --variant both --out final/w6400/K04-hole-macro-pace
  shot k04 stills/K04 "K04 hole macro 6400x3600 spp 112 --variant both, both feels" "$W64"/K04-hole-macro{,-pace}-{base,full}.png || exit 1
fi
# ---- K15 (space): 5120 spp 64, the bores wrapped (KQ_HOLE_UV=cyl), both feels
if ! done_mark "fw status k15"; then T0=$(date +%s)
  aside k15 "$V"/K15-space{,-pace}-{base,full}.png "$V"/K15-space{,-pace}.exr "$V"/K15-space{,-pace}.json "$V"/K15-space{,-pace}_bg_{base,full}.png
  still fw-K15  "$V/K15-space-full.png"      - -- env KQ_HOLE_UV=cyl $PY shots/K15-space.py --w 5120 --h 2880 --spp 64 --out final/v5k/K15-space
  still fw-K15p "$V/K15-space-pace-full.png" - -- env KQ_HOLE_UV=cyl $PY shots/K15-space.py --feel pace --w 5120 --h 2880 --spp 64 --out final/v5k/K15-space-pace
  shot k15 stills/K15 "K15 space 5120x2880 spp 64, bores wrapped (cyl), both feels" $(ls "$V"/K15-space{,-pace}{-base.png,-full.png,.exr,.json,_bg_base.png,_bg_full.png} 2>/dev/null) || exit 1
fi
# ---- K17 (roughness): 5760x3240 spp 48, both feels
if ! done_mark "fw status k17"; then T0=$(date +%s)
  aside k17 "$W57"/K17-roughness{,-base,-pace,-pace-base}.png
  still fw-K17  "$W57/K17-roughness.png"      - -- $PY shots/K17-roughness.py --w 5760 --h 3240 --spp 48 --out final/w5760/K17-roughness
  still fw-K17p "$W57/K17-roughness-pace.png" - -- $PY shots/K17-roughness.py --feel pace --w 5760 --h 3240 --spp 48 --out final/w5760/K17-roughness-pace
  shot k17 stills/K17 "K17 roughness 5760x3240 spp 48, both feels" "$W57"/K17-roughness{,-base,-pace,-pace-base}.png || exit 1
fi
# ---- K03 / K03b (section): 5120 --both spp 320, the hairline mask, the -line composites (the req-nov6 recipe)
if ! done_mark "fw status k03"; then T0=$(date +%s)
  C=K03-section-cut B=K03b-tubular
  aside k03 "$V"/{$C,$B}{,-pace}-{base,full,line}.png "$V/K03-line-mask.png"
  still fw-K03  "$V/$C-base.png"      - -- env PYTHONHASHSEED=0 $PY shots/K03-section-cut.py --w 5120 --h 2880 --spp 320 --both --out final/v5k/$C
  still fw-K03p "$V/$C-pace-base.png" - -- env PYTHONHASHSEED=0 $PY shots/K03-section-cut.py --feel pace --w 5120 --h 2880 --spp 320 --both --out final/v5k/$C-pace
  still fw-K03m "$V/K03-line-mask.png" - -- env PYTHONHASHSEED=0 $PY shots/K03-section-cut.py --line_mask --shell_w 0.55 --shell_tail 0.32 --w 5120 --h 2880 --spp 1024 --out final/v5k/K03-line-mask
  still fw-K03b  "$V/$B-base.png"      - -- env PYTHONHASHSEED=0 $PY shots/K03b-tubular.py --w 5120 --h 2880 --spp 320 --both --out final/v5k/$B
  still fw-K03bp "$V/$B-pace-base.png" - -- env PYTHONHASHSEED=0 $PY shots/K03b-tubular.py --feel pace --w 5120 --h 2880 --spp 320 --both --out final/v5k/$B-pace
  for s in $C $B; do for fe in "" -pace; do
    [ -z "$fe" ] && wl="--white 1 --tint 0.6" || wl="--white 0"
    still "fw-line-$s$fe" "$V/$s$fe-line.png" - -- $PY shots/k03s_line.py "$V/K03-line-mask.png" "$V/$s$fe-base.png" "$V/$s$fe-line.png" --halo 0.9 --sigma 8 $wl
  done; done
  shot k03b stills/K03b "K03b tubular 5120x2880 --both spp 320 (PYTHONHASHSEED 0) and its -line composites with the K03 mask, both feels" "$V"/$B{,-pace}-{base,full,line}.png || exit 1
  shot k03 stills/K03 "K03 section cut 5120x2880 --both spp 320 (PYTHONHASHSEED 0), the hairline mask and -line composites (the req-nov6 recipe), both feels" "$V"/$C{,-pace}-{base,full,line}.png "$V/K03-line-mask.png" || exit 1
fi
log "FW-DONE rest"
