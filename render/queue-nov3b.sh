#!/bin/bash
# queue-nov3b.sh (owner feedback 2026-11-03, after queue-nov3.sh): P4 K15 with wrapped bores at 5K, P3 K05 v7 at 5K
# (its look from render/notes/k05-v7.args, read when the item starts, so it can be decided while this runs), then P5:
# the full-bleed stills a 5K screen upscales (scripts/probe-5k.mjs), most visible first, into out/final/v5k/<same
# name> (link-masters.sh prefers v5k/). Resumable like queue-nov3.sh (render/notes/queue-nov3.md):
#   setsid nohup render/queue-nov3b.sh >> /home/user/kinetiq-render-out/logs/queue-nov3b.log 2>&1 &
# Waits for queue-nov3.sh to finish first (WAIT_FOR_NOV3=0 skips the wait).
QNAME=queue-nov3b
. "$(cd "$(dirname "$0")" && pwd)/queue_lib.sh"
V=$F/v5k
mkdir -p "$V"
if [ "${WAIT_FOR_NOV3:-1}" = 1 ]; then
  while ps -eo cmd | grep -q "^/bin/bash render/queue-nov3.sh\|^/bin/bash .*/queue-nov3.sh"; do sleep 120; done
fi
log "QUEUE-START (nov3b) free $(free_mb) MB"
NG="env KQ_NOGRIP=1"

if want p4; then   # K15, both feels, the bores wrapped (KQ_HOLE_UV=cyl), 5120 x 2880, on the 1.0 mm canon
  log "ITEM-START p4"
  still K15-v5k "$V/K15-space-full.png" - -- env KQ_HOLE_UV=cyl $PY shots/K15-space.py --w 5120 --h 2880 --spp 64 --out final/v5k/K15-space
  still K15p-v5k "$V/K15-space-pace-full.png" - -- env KQ_HOLE_UV=cyl $PY shots/K15-space.py --feel pace --w 5120 --h 2880 --spp 64 --out final/v5k/K15-space-pace
  if [ -f "$V/K15-space-full.png" ] && [ -f "$V/K15-space-pace-full.png" ]; then
    masters m-k15 stills/K15 "K15 5120 x 2880, bores wrapped as one moulded lining (2026-11-03)" "$V"/K15-space{,-pace}-{base,full}.png
    export_stills x-k15 "K15 Space-grade at 5120 x 2880 (owner, 3 Nov: the hole walls read as glued-in slats): every bore is wrapped as one moulded lining, the twill turning over the lip and running down the wall" K15-base K15-full K15-base-pace K15-full-pace
  fi
  log "ITEM-DONE p4"
fi

if want p3; then   # K05 v7: 5120 x 2880 (the master is taller, for the portrait crop), Command, Pace, and Naked twins
  log "ITEM-START p3"
  A=$KIT/notes/k05-v7.args
  if [ ! -f "$A" ]; then log "SKIP p3: no $A yet (the K05 v7 look is not decided)"; else
    ARGS=$(grep -v '^#' "$A" | tr '\n' ' ')
    still K05-v5k "$V/K05-laser-scan.png" - -- $PY shots/K05-laser-scan.py $ARGS --w 5120 --h 2880 --spp 96 --out final/v5k/K05-laser-scan
    still K05p-v5k "$V/K05-laser-scan-pace.png" - -- $PY shots/K05-laser-scan.py $ARGS --feel pace --w 5120 --h 2880 --spp 96 --out final/v5k/K05-laser-scan-pace
    still K05n-v5k "$V/K05-laser-scan-nogrip.png" - -- $NG $PY shots/K05-laser-scan.py $ARGS --w 5120 --h 2880 --spp 96 --out final/v5k/K05-laser-scan-nogrip
    still K05np-v5k "$V/K05-laser-scan-nogrip-pace.png" - -- $NG $PY shots/K05-laser-scan.py $ARGS --feel pace --w 5120 --h 2880 --spp 96 --out final/v5k/K05-laser-scan-nogrip-pace
    if [ -f "$V/K05-laser-scan-nogrip-pace.png" ]; then
      masters m-k05 stills/K05 "K05 v7 5120 x 2880, both feels, grip and Naked (2026-11-03)" $(ls "$V"/K05-laser-scan*.png)
      export_stills x-k05 "K05 Precision v7 at 5120 x 2880 (owner, 3 Nov: higher res, a richer light, a sharper laser), both feels, with its Naked twins" K05 K05-pace K05-phone K05-phone-pace K05-nogrip K05-nogrip-pace K05-nogrip-phone K05-nogrip-phone-pace
    fi
  fi
  log "ITEM-DONE p3"
fi

# P5: most visible first (probe-5k.mjs, 3 Nov: K04 6246, K05 5530, K17 5530, K06 5378, K15 5337, K01 5299, K02 5120,
# K07, K08, K14 5119, K03 4993, K16 2327 a half, K03b 3891)
if want p5a; then  # K14: the Sweet spot chapter's image (now a pinned scrub), cheap at 5K
  log "ITEM-START p5a"
  still K14-v5k "$V/K14-edge.png" - -- $PY shots/K14-edge.py --w 5120 --h 2880 --spp 48 --out final/v5k/K14-edge
  still K14p-v5k "$V/K14-edge-pace.png" - -- $PY shots/K14-edge.py --feel pace --w 5120 --h 2880 --spp 48 --out final/v5k/K14-edge-pace
  [ -f "$V/K14-edge-pace.png" ] && { masters m-k14 stills/K14 "K14 5120 x 2880 (2026-11-03)" "$V"/K14-edge{,-pace}.png; export_stills x-k14 "K14 (Sweet spot) at 5120 x 2880 for 5K screens, both feels" K14 K14-pace; }
  log "ITEM-DONE p5a"
fi

if want p5b; then  # K04 (Holes macro, drawn at 6246 device px)
  log "ITEM-START p5b"
  still K04-v5k "$V/K04-hole-macro-full.png" - -- $PY shots/K04-hole-macro.py --w 5120 --h 2880 --spp 112 --variant both --out final/v5k/K04-hole-macro
  still K04p-v5k "$V/K04-hole-macro-pace-full.png" - -- $PY shots/K04-hole-macro.py --feel pace --w 5120 --h 2880 --spp 112 --variant both --out final/v5k/K04-hole-macro-pace
  [ -f "$V/K04-hole-macro-pace-full.png" ] && { masters m-k04 stills/K04 "K04 5120 x 2880 (2026-11-03)" "$V"/K04-hole-macro{,-pace}-{base,full}.png; export_stills x-k04 "K04 (moulded hole macro) at 5120 x 2880 for 5K screens, both feels" K04-base K04-full K04-base-pace K04-full-pace; }
  log "ITEM-DONE p5b"
fi

if want p5c; then  # K16 (the quality bar): halves 2560 x 2880 (pair 5120 x 2880), both feels
  log "ITEM-START p5c"
  still K16d-v5k "$V/K16-drilled-base.png" - -- $PY shots/K16-pair.py --mode drilled --w 2560 --h 2880 --spp 64 --out final/v5k/K16-drilled
  still K16m-v5k "$V/K16-moulded-full.png" - -- $PY shots/K16-pair.py --mode moulded --w 2560 --h 2880 --spp 64 --out final/v5k/K16-moulded
  still K16c-v5k "$V/K16-pair-full.png" - -- $PY shots/K16-pair.py --combine final/v5k/K16-drilled final/v5k/K16-moulded --out final/v5k/K16-pair --gutter 0
  still K16dp-v5k "$V/K16-drilled-pace-base.png" - -- $PY shots/K16-pair.py --feel pace --mode drilled --w 2560 --h 2880 --spp 64 --out final/v5k/K16-drilled-pace
  still K16mp-v5k "$V/K16-moulded-pace-full.png" - -- $PY shots/K16-pair.py --feel pace --mode moulded --w 2560 --h 2880 --spp 64 --out final/v5k/K16-moulded-pace
  still K16cp-v5k "$V/K16-pair-pace-full.png" - -- $PY shots/K16-pair.py --feel pace --combine final/v5k/K16-drilled-pace final/v5k/K16-moulded-pace --out final/v5k/K16-pair-pace --gutter 0
  [ -f "$V/K16-pair-pace-full.png" ] && { masters m-k16 stills/K16 "K16 pair 5120 x 2880 (2026-11-03)" "$V"/K16-pair{,-pace}-{base,full}.png; export_stills x-k16 "K16 (drilled against moulded) at 5120 x 2880, both feels" K16-base K16-full K16-base-pace K16-full-pace; }
  log "ITEM-DONE p5c"
fi

if want p5d; then  # K17 (Surface, 5530)
  log "ITEM-START p5d"
  still K17-v5k "$V/K17-roughness.png" - -- $PY shots/K17-roughness.py --w 5120 --h 2880 --spp 48 --out final/v5k/K17-roughness
  still K17p-v5k "$V/K17-roughness-pace.png" - -- $PY shots/K17-roughness.py --feel pace --w 5120 --h 2880 --spp 48 --out final/v5k/K17-roughness-pace
  [ -f "$V/K17-roughness-pace.png" ] && { masters m-k17 stills/K17 "K17 5120 x 2880 (2026-11-03)" "$V"/K17-roughness{,-base,-pace,-pace-base}.png; export_stills x-k17 "K17 (Surface) at 5120 x 2880, both feels" K17-base K17-full K17-base-pace K17-full-pace; }
  log "ITEM-DONE p5d"
fi

if want p5e; then  # K06 (BornWhole, 5378): grip and Naked, both feels
  log "ITEM-START p5e"
  still K06-v5k "$V/K06-mould-full.png" - -- $PY shots/K06-mould.py --w 5120 --h 2880 --spp 112 --out final/v5k/K06-mould
  still K06n-v5k "$V/K06-mould-nogrip-full.png" - -- $NG $PY shots/K06-mould.py --w 5120 --h 2880 --spp 112 --out final/v5k/K06-mould-nogrip
  still K06p-v5k "$V/K06-mould-pace-full.png" - -- $PY shots/K06-mould.py --feel pace --w 5120 --h 2880 --spp 112 --out final/v5k/K06-mould-pace
  still K06np-v5k "$V/K06-mould-nogrip-pace-full.png" - -- $NG $PY shots/K06-mould.py --feel pace --w 5120 --h 2880 --spp 112 --out final/v5k/K06-mould-nogrip-pace
  [ -f "$V/K06-mould-nogrip-pace-full.png" ] && { masters m-k06 stills/K06 "K06 5120 x 2880, grip and Naked (2026-11-03)" $(ls "$V"/K06-mould*-{base,full}.png); export_stills x-k06 "K06 (mould) at 5120 x 2880, grip and Naked, both feels" K06-base K06-full K06-base-pace K06-full-pace K06-nogrip-base K06-nogrip-full K06-nogrip-base-pace K06-nogrip-full-pace; }
  log "ITEM-DONE p5e"
fi

if want p5f; then  # K07 and K08 (5120): grip and Naked
  log "ITEM-START p5f"
  still K07-v5k "$V/K07-lineup-five.png" - -- $PY shots/K07-lineup-five.py --w 5120 --h 2880 --spp 112 --seq --out final/v5k/K07-lineup-five
  still K07n-v5k "$V/K07-lineup-five-nogrip.png" - -- $NG $PY shots/K07-lineup-five.py --w 5120 --h 2880 --spp 112 --seq --out final/v5k/K07-lineup-five-nogrip
  still K08-v5k "$V/K08-feel-pair.png" - -- $PY shots/K08-feel-pair.py --w 5120 --h 2880 --spp 96 --crops --out final/v5k/K08-feel-pair
  still K08n-v5k "$V/K08-feel-pair-nogrip.png" - -- $NG $PY shots/K08-feel-pair.py --w 5120 --h 2880 --spp 96 --crops --out final/v5k/K08-feel-pair-nogrip
  [ -f "$V/K08-feel-pair-nogrip.png" ] && { masters m-k0708 stills/K07-K08 "K07 and K08 5120 x 2880, grip and Naked (2026-11-03)" "$V"/K07-lineup-five{,-nogrip}.png "$V"/K08-feel-pair{,-nogrip}.png; export_stills x-k0708 "K07 (lineup) and K08 (the two feels) at 5120 x 2880, grip and Naked" K07 K07-nogrip K08 K08-nogrip; }
  log "ITEM-DONE p5f"
fi

log "ALL-DONE (nov3b) free $(free_mb) MB"
