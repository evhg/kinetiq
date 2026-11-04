# Render owner -> site agent: hand-off notes (owner feedback 2026-11-03)

## The laser in Precision (K05): it is the render, not code
The red laser line, its glow and the faint trail of earlier profiles are all rendered into K05 (a real tilted light
sheet: an emissive tube about 0.16 mm wide on the racket and the plate, and a halo composited from the laser's own
light group). Nothing in `Precision.tsx` / `Precision.module.css` draws it. It looked soft on the owner's 5K screen
because the K05 export stops at 2560 px and the stage draws it at 5530 device px (2560 x 1440 CSS at DPR 2, times the
pin's 1.08 start scale): x2.16 upscaled (`scripts/probe-5k.mjs`, 3 Nov). The fix is on the render side: K05 is being
re-rendered at 5120 x 2880 with a richer light (P3) and exported up to 5120 (`stills.json` wide ladder now ends at
5120). Nothing to change in the component; at rest (scale 1) the 5120 export maps 1:1 on a 5K screen, during the
1.08 settle it is 8 % up, which the scale animation hides.

## What a 5K screen gets once the queue's exports land (probe-5k.mjs, landing page, 3 Nov)
| Still | shown (device px) | export today | after |
|---|---|---|---|
| K01 hero (base, full, finale; Naked twins) | 5299 | 2560 | 5120 (queue p1a, p2a, p2c) |
| K01 swivel canvas (desktop) | ~2300 of the frame | 2560 frame | 5120 frame (p2a-p2d) |
| K05 | 5530 | 2560 | 5120 (P3) |
| K15 | 5337 | 2560 | 5120 (P4) |
| K04 | 6246 | 2560 | 3200 from the existing master on re-export; 5120+ needs a re-render (P5) |
| K17, K06, K02, K07, K08, K14, K03, K16, K03b, Unibody canvas | 3891-5530 | 1440-2560 | P5, most visible first |

Width ladders: `stills.json` `wide` is now `[828, 1280, 1920, 2560, 3840, 5120]` (phones unchanged: a 390 px phone at
DPR 3 still picks 1280; portrait, card and trio ladders untouched). `sequence.mjs` landscape widths add 3840 and 5120.
Desktop note: a 1536 px laptop at DPR 2 (3072 device px) will now pick the 3840 hero instead of 2560 (more bytes on
desktop LCP; phones are unaffected). If the desktop LCP budget suffers, cap the hero's `sizes` for <= 1600 px windows.

## Naked
- The Naked racket's butt is the shell's carbon (white 3K Command, black 12K Pace) flaring into a rounded end with the Q
  engraved (laser frost: graphite on white, pale on black); no black cap. Silhouette unchanged from the grip-off
  twins (the old cap's 1.9 mm flare), so every crop, mask and registration still holds.
- Still ids keep `-nogrip`; the swivels are `K01-swivel-nogrip-<feel>-<layout>` (Hero.tsx's SWIVEL.off already).
- K05's Naked twin comes with the new K05 (P3).

## Light sweep (hero swivel)
Frame 0 of every new swivel is the still exactly (the band starts off the head at progress 0), so the handover is
unchanged; the band crosses the face and frame as `progress` goes 0 -> 1 (linear with the turn). Reduced motion keeps
the still, which has no band.
