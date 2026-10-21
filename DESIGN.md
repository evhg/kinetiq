# KINETIQ design

Read this and `CLAUDE.md` before any interface or animation work.
Brief (owner, 2026-10-21): an e-commerce landing page, conversion-optimised, with a Stripe checkout.
It should feel like a product reveal (think a car maker unveiling a roadster). One call to action,
placed at the emotional peaks. Full payment up front, shipping January 2027. Claims are bold by
design; see `CLAIMS.md` for what needs proof before launch.

## Direction
A product reveal on a black stage. The racket rises out of the dark into studio light, and every chapter
after that proves one claim with one big, simple idea: one piece, 15 µm, nothing glued, two identical
rackets, Swiss Made. Wide, heavy type does the shouting. The page is quiet around it. Precision is the
mood: thin rules, measured numbers, nothing decorative.

## References
| Reference | Borrow | Avoid |
| --- | --- | --- |
| Car-maker product reveals | The dark stage, the slow light-up, specs as giant numbers, one "reserve" action | Countdown timers, fake scarcity |
| lighthouse.storage/token (`docs/reference-notes.md`) | Scroll-scrubbed hero model, a skip link inside the pinned stage, Lenis off under reduced motion | Competing CTAs, a nav menu on a one-action page |
| kinetiq-review.vercel.app (old reference) | Racket proportions, model names, padel shot vocabulary | Its assets (not cleared), mono eyebrows, numbered markers on non-sequences |

## Colour tokens
| Token | Hex | Role | Contrast notes |
| --- | --- | --- | --- |
| `--black` | #000000 | Stage, page background | |
| `--surface` | #0d0d0e | Alternate chapter background | |
| `--text` | #f5f5f3 | Headlines, body emphasis, the CTA fill | 19.6:1 on black |
| `--muted` | #a3a3a8 | Body copy, labels | 8.1:1 on black, 7.4:1 on surface |
| `--steel` | #d4d6da | Leads, secondary emphasis | 14:1 on black |
| `--paper` | #f3f2ee | Measurement card only | Ink #0a0a0a on paper 18:1 |
| `--swiss` | #da291c | Swiss flag only, never UI | |

## Type scale
One family: **Archivo** (OFL), variable weight and width.
| Style | Family | Size (phone / desktop) | Weight | Line height | Tracking |
| --- | --- | --- | --- | --- | --- |
| Record number | Archivo wdth 125 | 7rem / 20rem | 800 | 0.85 | -0.025em |
| Display | Archivo wdth 125 | 2.5rem / 5.75rem | 800 | 0.95 | -0.025em |
| Display 2 | Archivo wdth 125 | 2rem / 4.5rem | 800 | 0.95 | -0.025em |
| Display 3 | Archivo wdth 125 | 1.4rem / 2rem | 800 | 1.05 | -0.025em |
| Lead | Archivo | 1.125rem / 1.375rem | 400 | 1.55 | 0 |
| Body | Archivo | 1.0625rem | 400 | 1.55 | 0 |
| Label | Archivo | 0.875rem | 400–500 | 1.4 | 0 |
| Wordmark | Archivo wdth 125 | 0.9375rem | 700 | 1 | 0.32em |

## Spacing
Base 4 px. Gutter `clamp(16px, 4vw, 56px)`. Sections 120 px top and bottom. Pinned stages are 100svh.
Two-column split at 900 px. Line length under 62ch.

## Motion language
### Signature moment
The reveal: on load, the 3D racket rises from below in the dark, turning, while the studio light comes
up (2.6 s, `expo.out`). The supporting copy and specs arrive after it. As you scroll away, the racket
turns edge-on: one piece, 38 mm.

### Scroll chapters
| # | Chapter | Pin | Scrub / trigger | Length | Motion-off version |
| --- | --- | --- | --- | --- | --- |
| 0 | Hero | No | Load-triggered reveal; scroll scrubs the racket edge-on | 1 screen | Static SVG still, all copy visible |
| 1 | One piece | Yes | Scrub: an exploded stack (face, glue, core, glue, face, frame) closes up, the glue disappears, "1 part" | 2.6 screens | Three beats stacked, stack shown merged |
| 2 | Precision | Yes | Scrub: counter 500 → 15 µm, comparison bars fill, record headline | 2 screens | 15 µm, bars full, headline visible |
| 3 | Feel | No | Scrub: two vibration lines draw (glued vs one piece) | — | Lines fully drawn |
| 4 | Holes and identical | No | None (hover tilt on the card, desktop only) | — | Same |
| 5 | Swiss | No | None | — | Same |
| 6 | Reserve | No | None | — | Same |

### Micro-interactions
| Element | Trigger | Properties | Duration | Easing |
| --- | --- | --- | --- | --- |
| CTA | press | scale 0.97 | 160 ms | ease-out curve |
| CTA | hover (fine pointer) | background colour | 200 ms | ease |
| Motion switch | press | scale 0.97 | 160 ms | ease-out curve |
| Model picker | select | background, colour | 200 ms | ease |
| Measurement card | hover (fine pointer) | rotate -3° → 0°, translateY -6 px | 300 ms | ease-out curve |
| Hero racket | pointer move (fine pointer) | small rotation toward the pointer | damped per frame | exponential |

## 3D use
One scene, the hero: a procedural racket built from `src/lib/racket-shape.ts` (outline, throat, 42 holes,
38 mm extrusion with bevels), a canvas-drawn twill texture, clearcoat, and locally rendered Lightformers.
Loaded after idle, DPR capped at 2 / 1.5, paused off-screen. Fallback: the inline SVG of the same shape.

## Content inventory
| Section | Copy | Media | CTA |
| --- | --- | --- | --- |
| Hero | Claim 1, Swiss Made, 15 µm | 3D racket / SVG still, four stats | Reserve yours |
| One piece | Three beats | Layer stack | – |
| Precision | Record claim, comparison | Counter, bars | Reserve yours (after) |
| Feel | Three reasoned feel claims | Two vibration lines | – |
| Holes + identical | Moulded holes, ±1 g / ±1 mm | Hole rings, measurement card | – |
| Swiss | 100% Swiss Made, patented, St. Gallen | Swiss flag | – |
| Reserve | Model picker, specs, price, terms | – | Reserve yours (model preselected) |
| FAQ | Six answers | – | – |
| Checkout | Model, summary, terms | – | Continue to secure payment (Stripe) |

## Languages
English only at launch (`lang="en"`). Archivo is loaded with `latin` and `latin-ext`, which also covers
German, French, Italian and Spanish if they are added later.
