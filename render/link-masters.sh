#!/bin/bash
# Map the render finals (out/final/<shot>[-<variant>].png) to the site's still ids (src/content/stills.json).
OUTROOT="${KQ_RENDER_OUT:-/home/user/kinetiq-render-out}"
F="$OUTROOT/out/final"
M="${KQ_MASTERS:-$OUTROOT/masters}"
mkdir -p "$M"
l() { [ -f "$F/$1" ] && ln -sfn "$F/$1" "$M/$2.png" && echo "$1 -> $2"; }
l K01-hero-frame-phone-base.png K01-hero-base-phone
l K01-hero-frame-phone-full.png K01-hero-full-phone
l K01-hero-beam-base.png K01-base
l K01-hero-beam-full.png K01-full
l K01-hero-beam-finale.png K01-finale
l K02-edge-line.png K02
l K03-section-cut-full.png K03
l K03b-tubular-full.png K03b-tubular
l K04-hole-macro-base.png K04-base
l K04-hole-macro-full.png K04-full
l K05-laser-scan.png K05
l K05-laser-scan-phone.png K05-phone
l K06-mould-base.png K06-base
l K06-mould-full.png K06-full
l K07-lineup-five.png K07
l K08-feel-pair.png K08
l K09-case-three-gallery.png K09
l K09-case-three-card.png K09-card
l K10-throat-serial.png K10
l K11-pair-command.png K11-command
l K11-pair-pace.png K11-pace
l K11-single.png K11-single
l K12-sweet-spot-base.png K12-base
l K12-sweet-spot-full.png K12-full
true
l K01-hero-beam-pace-base.png K01-base-pace
l K01-hero-beam-pace-full.png K01-full-pace
l K01-hero-beam-pace-finale.png K01-finale-pace
l K01-hero-frame-phone-pace-base.png K01-hero-base-phone-pace
l K01-hero-frame-phone-pace-full.png K01-hero-full-phone-pace
l K02-edge-line-pace.png K02-pace
l K05-laser-scan-pace.png K05-pace
l K05-laser-scan-pace-phone.png K05-phone-pace
l K06-mould-pace-base.png K06-base-pace
l K06-mould-pace-full.png K06-full-pace
l K10-throat-serial-pace.png K10-pace
l K11-single-pace.png K11-single-pace
l K09-case-three-gallery-pace.png K09-pace
l K09-case-three-card-pace.png K09-card-pace
l K12-sweet-spot-pace-base.png K12-base-pace
l K12-sweet-spot-pace-full.png K12-full-pace
l K03-section-cut-pace-full.png K03-pace
l K03b-tubular-pace-full.png K03b-tubular-pace
l K04-hole-macro-pace-base.png K04-base-pace
l K04-hole-macro-pace-full.png K04-full-pace
l K13-layup.png K13
l K11-pair-pace.png K11-command-pace
l K14-edge.png K14
l K14-edge-pace.png K14-pace
l K15-space-base.png K15-base
l K15-space-full.png K15-full
l K15-space-pace-base.png K15-base-pace
l K15-space-pace-full.png K15-full-pace
true
