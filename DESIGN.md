# KINETIQ design

Read this and `CLAUDE.md` before any interface or animation work.
Brief (owner, 2026-10-21): a launch page in the voice of a Tesla or Apple product reveal, a reservation flow
modelled on the Tesla Roadster reserve page, and assets that read as expensive and high precision.
Claims are bold by design; `CLAIMS.md` lists what needs proof before launch.

## Direction: "Out of the dark, measured."
The racket rises out of a near-black studio into a single beam. Every chapter proves one claim with one
photograph (an own Blender Cycles still) and one engineering graphic (SVG or canvas, drawn from
`src/lib/racket-shape.ts`). Graphite neutrals, a warm amber data glow, and at most one ember-red line per
image. Precision is the mood: hairlines, tabular numerals, weights with a decimal, nothing cartoonish.
No real-time 3D anywhere: the owner rejected it as toy-like.

## Owner rules (2026-10-21)
- Fill wide screens. Content spans a 12-column grid with margins 20 / 64 / 128 px (390 / 1440 / 2560);
  imagery is full-bleed. No left-aligned column beside an empty half, no 1200 px container on a 2560 screen.
- Never 90% black. Fill rule (checked by the harness at every screenshot): at most 40% of a viewport at
  luma ≤ 12, at least 8% at luma ≥ 40, and no flat-black vertical strip a quarter of the viewport wide.
  Fix a failing section with light, a lift or a graphic; never lower the thresholds.
- Text larger than Tesla's 14 px: nothing below 15 px anywhere, body 18 px and up, 16 px minimum on /reserve.
- No motion toggle. `prefers-reduced-motion` is honoured silently.
- Weights always carry a decimal (355.0 g, ±1.0 g), never a range.
- Copy in the Tesla / Apple launch voice: short, declarative, a superlative backed by one fact. No middle dots,
  no workshop, town, golf or supply-chain talk, never the banned lines listed in `src/content/copy.ts`.
- One landing CTA, "Reserve Now", only in the hero, at the Identical peak, in the finale and as the compact
  header button after the hero. On /reserve: "Pay with Card", then "Place Reservation", nothing after it.

## Colour tokens (`globals.css`)
| Token | Hex | Role |
| --- | --- | --- |
| `--void` | #060607 | Page background |
| `--stage` / `--lift` | #111113 / #2b2b31 | Graphite section floor and the radial lift behind graphics (G10) |
| `--graphite`, `--graphite-2`, `--field` | #18181b, #202024, #141417 | Cards, secondary buttons, inputs |
| `--hairline`, `--edge`, `--grid` | #2c2c31, #6b6e76, #26262a | Rules, input borders, drawing grids |
| `--text`, `--steel`, `--muted` | #f5f5f3, #c9ccd1, #9b9ea6 | Headlines and primary CTA fill, leads and labels, fine print (7:1+ on --void) |
| `--amber`, `--amber-hot` | #e3a467, #ffe2bf | Data glow, light lines (G09), selected edges. Never body text. |
| `--ember` | #ff3a1e | One red line per image (scan line). Never UI text or a fill. |
| `--swiss` | #da291c | The Swiss cross only |
| `--paper`, `--ink` | #f3f2ee, #0a0a0a | The measurement card |

## Type
Archivo (OFL, variable weight and width) for display and text; Saira (OFL) for data, labels and numerals.
Headlines Archivo wdth 112 wght 580; record numerals wght 200–220, tabular; wordmark wdth 125 tracking 0.32em.
Fluid scale up to 2560 in `globals.css` (`--fs-record` … `--fs-fine`); classes `.t-h1` … `.t-fine`.

## Page
| # | Section | Media | Motion (reduced motion: final state, no pin) |
| --- | --- | --- | --- |
| 1 | Hero | K01 base → beam crossfade | Load reveal; scroll drift and veil |
| 2 | Spec strip | G01 technical drawing | Numbers rise on entry |
| 3 | One piece (pinned ≥ 900 px) | K02 edge-on → K03 cut-through + G07 sections | Light line sweep, beat crossfade |
| 4 | Born whole | K06 mould, Swiss lockup, G13 badges | Scrubbed push-in, cavity glow |
| 5 | Precision (pinned ≥ 900 px) | K05 scan, record counter; G03 tolerance graph | Counter 500 → 15 µm with an ember scan line |
| 6 | Holes | K04 macro + G05 fibre flow; G06 drilled vs moulded | Ring glow, flow advection |
| 7 | Feel | G02 vibration graph | Graph reveal on entry |
| 8 | Identical | K07 five rackets; G04 spikes, G08 card; CTA 2 | Rise on entry |
| 9 | Choose your feel | K08 pair (Command 3K, Pace 12K) | Rise on entry |
| 10 | Editions | Three cards (K01 / K06 / K09) linking to /reserve?tier= | Rise on entry |
| 11 | Finale | K01 in its beam; CTA 3 | Rise on entry |
| /reserve | Sticky gallery (per-edition slides, G14 controls) + options column | Tier cards (G11 glyphs), feel swatches, trust list, Due Today, Pay with Card → form in place | Crossfades, fields rise 8 px |

Stills are exported by `scripts/stills.mjs` from 16-bit Blender masters (not committed) to AVIF + WebP with
phone crops (`src/content/stills.json`), and rendered with `<Still>` (`src/components/media/Still.tsx`).
Graphics live in `src/components/graphics/` with review pages at `/lab/<id>` (dev only).

## Micro-interactions
Pressables scale 0.97 on `:active`; hover only behind `(hover: hover) and (pointer: fine)`; transform and
opacity only, 150–300 ms ease-out (`--ease-out`); exits faster than entries.

## Languages
English only at launch (`lang="en"`). Archivo and Saira load `latin` and `latin-ext`.
