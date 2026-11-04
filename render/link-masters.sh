#!/bin/bash
# Map the render finals (out/final/<shot>[-<variant>].png) to the site's still ids (src/content/stills.json).
OUTROOT="${KQ_RENDER_OUT:-/home/user/kinetiq-render-out}"
F="$OUTROOT/out/final"
M="${KQ_MASTERS:-$OUTROOT/masters}"
mkdir -p "$M"
# a 5K re-render (owner, 2026-11-03) of any final lives in final/v5k/ under the same name and wins
l() { local s="$F/$1"; [ -f "$F/v5k/$1" ] && s="$F/v5k/$1"; [ -f "$s" ] && ln -sfn "$s" "$M/$2.png" && echo "$1 -> $2"; }
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
# K03's base pass (no lg_shell, so no baked amber hairline on the rim's shoulder), the Sealed core chapter's still under
# its registered trace (Mac node, 2026-11-04, REQUEST K03-base; same render and rig as K03)
l K03-section-cut-base.png K03-base
l K03-section-cut-pace-base.png K03-base-pace
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
l K16-pair-base.png K16-base
l K16-pair-full.png K16-full
l K16-pair-pace-base.png K16-base-pace
l K16-pair-pace-full.png K16-full-pace
true
l K01-hero-beam-nogrip-base.png K01-nogrip-base
l K01-hero-beam-nogrip-full.png K01-nogrip-full
l K01-hero-beam-nogrip-pace-base.png K01-nogrip-base-pace
l K01-hero-beam-nogrip-pace-full.png K01-nogrip-full-pace
l K01-hero-frame-phone-nogrip-base.png K01-nogrip-hero-base-phone
l K01-hero-frame-phone-nogrip-full.png K01-nogrip-hero-full-phone
l K01-hero-frame-phone-nogrip-pace-base.png K01-nogrip-hero-base-phone-pace
l K01-hero-frame-phone-nogrip-pace-full.png K01-nogrip-hero-full-phone-pace
l K17-roughness-base.png K17-base
l K17-roughness.png K17-full
l K17-roughness-pace-base.png K17-base-pace
l K17-roughness-pace.png K17-full-pace
true
# grip-off twins of every still that shows the handle (owner, 2026-11-03; KQ_NOGRIP=1, README "Grip-off twins")
l K01-hero-beam-nogrip-finale.png K01-nogrip-finale
l K01-hero-beam-nogrip-pace-finale.png K01-nogrip-finale-pace
l K02-edge-line-nogrip.png K02-nogrip
l K02-edge-line-nogrip-pace.png K02-nogrip-pace
l K05-laser-scan-nogrip.png K05-nogrip
l K05-laser-scan-nogrip-phone.png K05-nogrip-phone
l K05-laser-scan-nogrip-pace.png K05-nogrip-pace
l K05-laser-scan-nogrip-pace-phone.png K05-nogrip-phone-pace
l K06-mould-nogrip-base.png K06-nogrip-base
l K06-mould-nogrip-full.png K06-nogrip-full
l K06-mould-nogrip-pace-base.png K06-nogrip-base-pace
l K06-mould-nogrip-pace-full.png K06-nogrip-full-pace
l K07-lineup-five-nogrip.png K07-nogrip
l K08-feel-pair-nogrip.png K08-nogrip
l K09-case-three-gallery-nogrip.png K09-nogrip
l K09-case-three-card-nogrip.png K09-nogrip-card
l K09-case-three-gallery-nogrip-pace.png K09-nogrip-pace
l K09-case-three-card-nogrip-pace.png K09-nogrip-card-pace
l K10-throat-serial-nogrip.png K10-nogrip
l K10-throat-serial-nogrip-pace.png K10-nogrip-pace
l K11-pair-nogrip-command.png K11-nogrip-command
l K11-pair-nogrip-pace.png K11-nogrip-pace
l K11-pair-nogrip-pace.png K11-nogrip-command-pace
l K11-single-nogrip.png K11-nogrip-single
l K11-single-nogrip-pace.png K11-nogrip-single-pace
l K12-sweet-spot-nogrip-base.png K12-nogrip-base
true
# 2026-11-03 (owner: Naked = 100 % carbon, 5K): the Naked carbon-butt K01 stills (5120 x 2880 beam, 2160 x 3840 phone)
# and the 5K grip K01 beam stills, rendered with the light-sweep scene (k01_lib SWEEP, t = 0); they replace the rows above.
l K01-hero-beam-nogrip-v5k-base.png K01-nogrip-base
l K01-hero-beam-nogrip-v5k-full.png K01-nogrip-full
l K01-hero-beam-nogrip-v5k-finale.png K01-nogrip-finale
l K01-hero-beam-nogrip-pace-v5k-base.png K01-nogrip-base-pace
l K01-hero-beam-nogrip-pace-v5k-full.png K01-nogrip-full-pace
l K01-hero-beam-nogrip-pace-v5k-finale.png K01-nogrip-finale-pace
l K01-hero-frame-phone-nogrip-v5k-base.png K01-nogrip-hero-base-phone
l K01-hero-frame-phone-nogrip-v5k-full.png K01-nogrip-hero-full-phone
l K01-hero-frame-phone-nogrip-pace-v5k-base.png K01-nogrip-hero-base-phone-pace
l K01-hero-frame-phone-nogrip-pace-v5k-full.png K01-nogrip-hero-full-phone-pace
l K01-hero-beam-v5k-base.png K01-base
l K01-hero-beam-v5k-full.png K01-full
l K01-hero-beam-v5k-finale.png K01-finale
l K01-hero-beam-pace-v5k-base.png K01-base-pace
l K01-hero-beam-pace-v5k-full.png K01-full-pace
l K01-hero-beam-pace-v5k-finale.png K01-finale-pace
l K01-hero-frame-phone-v5k-base.png K01-hero-base-phone
l K01-hero-frame-phone-v5k-full.png K01-hero-full-phone
l K01-hero-frame-phone-pace-v5k-base.png K01-hero-base-phone-pace
l K01-hero-frame-phone-pace-v5k-full.png K01-hero-full-phone-pace
true
