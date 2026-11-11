#!/usr/bin/env bash
# fw-k17weave.sh (2026-11-11, the Mac render node): cloud REQUEST k17-pace-weave (02:02Z). K17 Pace gets its own weave
# card so the black 12K tapes read under the micro-domes: a soft area light (glossy rays only, group "fill", on the face,
# rim and wall) 12 deg above the face's mirror direction and turned 25 deg about the vertical, 4 W, 1.0 m: the tapes'
# fibre lobes catch it as soft alternating grey / black tiles (no hard chessboard). Domes, ball and Command unchanged.
# Base and full at 5760x3240 spp 48 as today, masters to stills/K17, one STATUS line, then the export (K17-base-pace,
# K17-full-pace). Resumable (markers "kw ..."); the previous files go to $F/pre-k17weave once.
. "$(cd "$(dirname "$0")" && pwd)/fw-lib.sh"
R=k17-pace-weave
W57=$F/w5760
OLDF=$F/pre-k17weave
mkdir -p "$OLDF"
log "KW-START device $KQ_DEVICE free $(free_mb) MB push $PUSH"
done_mark "kw aside" || { for f in "$W57"/K17-roughness-pace{,-base}.png "$W57"/K17-roughness-pace{,-base}{.json,_bg.png} "$W57/K17-roughness-pace.exr"; do [ -e "$f" ] && mv "$f" "$OLDF"/; done; mark "kw aside"; }
t0=$(date +%s)
still kw-K17p "$W57/K17-roughness-pace.png" - -- $PY shots/K17-roughness.py --feel pace --w 5760 --h 3240 --spp 48 --out final/w5760/K17-roughness-pace
need "$W57"/K17-roughness-pace{,-base}.png || exit 1
tt=$(( $(date +%s) - t0 ))
[ "$PUSH" = 1 ] || { log "PUSH=0: rendered, not pushed"; exit 0; }
masters "kw m" stills/K17 "K17 Pace, $R base + full, 5760x3240" "$W57"/K17-roughness-pace{,-base}.png
done_mark "kw m" || exit 1
st "kw status" "$(date -u +%FT%TZ) $R:K17-roughness-pace stills/K17/K17-roughness-pace.png,stills/K17/K17-roughness-pace-base.png $(hm $tt) $DEVNAME K17 Pace (the micro-dome macro under the ball), re-rendered with its own weave card: a soft 1.0 m area light, glossy rays only, 12 deg above the face's mirror direction and turned 25 deg about the vertical, 4 W, on the face, rim and wall: the black 12K tapes now read under the domes as soft alternating grey and black tiles with a sheen (tested 6 W at -25 deg: tiles barely there; 8 to 20 W at +25 deg and 6 W at 0 deg: a hard grey chessboard); domes, ball, camera and Command unchanged; 5760x3240 spp 48, base + full from one render; with the $CANON; render time this run"
done_mark "kw status" || exit 1
done_mark "kw export" && { log "KW-DONE"; exit 0; }
out=$(KQ_RENDER_OUT=$KQ_RENDER_OUT "$KIT/mac_export.sh" "K17 Pace with its weave card (k17-pace-weave)" K17-full-pace="$W57/K17-roughness-pace.png" K17-base-pace="$W57/K17-roughness-pace-base.png" 2>&1 | tee -a "$LOGD/export.log" | tail -3)
sha=$(echo "$out" | sed -n 's/.*EXPORTED-SHA \([0-9a-f]*\).*/\1/p' | tail -1)
[ -n "$sha" ] || { log "ERROR kw export: $out"; exit 1; }
mark "kw export"
echo "$sha" > "$LOGD/kw-export.sha"
log "KW-DONE exported $sha"
