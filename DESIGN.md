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
- "One piece" is retired (owner, 2026-10-22), except in the owner's hero sentence: construction words are
  "unibody" and "Zero seams.", scoped to the frame ("No joint to work loose."); never "zero weak points" or
  "nothing to come apart" (absolute, CLAIMS.md row 8b), never "first unibody".
  Durability is "Built to last five years", always with its usage profile (`lifetime.fine`); "guarantee" only
  for InviQtus ("five-year guarantee", never "lifetime guarantee").
- Sealed core (owner, 2026-10-22; CLAIMS.md rows 30 to 34): the carbon shell closes around the whole EVA core and lines
  all 42 holes, so the core never touches the air; the EVA is Swiss-made (country level only) and injected straight
  into the mould. Told once per place: the reveal in Unibody, the drilled hole in Holes, the result in Durability
  ("three times longer than an open core", always with its † fine print). It keeps out sweat, humidity and UV, never
  heat; never "airtight", "waterproof" or "first".
- One landing CTA, "Reserve Now", only in the hero, at the Identical peak, in the finale and as the compact
  header button after the hero. On /reserve: "Pay with Card", then "Place Reservation", nothing after it.
  The invitation unlock on /reserve ("Have an invitation?", then "Unlock") is a quiet control for invitees
  only, above the options; it is not a CTA.
- InviQtus is invite only: shown whole everywhere but never interactive for other visitors (no hover, press,
  arrow or selected glow; not a link on the landing page) until a valid invitation code unlocks it on /reserve.
- The EU legal-guarantee notice and the InviQtus GARAN label (CLAIMS.md row 29 and the note under the tables)
  are fixed EU artwork that overrides the palette, type and 15 px rules. Neither is built yet: both wait for
  the owner's documented exception.

## Colour tokens (`globals.css`)
| Token | Hex | Role |
| --- | --- | --- |
| `--void` | #060607 | Page background |
| `--stage` / `--lift` | #111113 / #2b2b31 | Graphite section floor and the radial lift behind graphics (G10) |
| `--graphite`, `--graphite-2`, `--field` | #18181b, #202024, #141417 | Cards, secondary buttons, inputs |
| `--hairline`, `--edge`, `--grid` | #2c2c31, #6b6e76, #26262a | Rules, input borders, drawing grids |
| `--text`, `--steel`, `--muted` | #f5f5f3, #c9ccd1, #9b9ea6 | Headlines and primary CTA fill, leads and labels, fine print (7:1+ on --void) |
| `--amber`, `--amber-hot` | #e3a467, #ffe2bf | Data glow, light lines (G09), selected edges. Never body text. |
| `--ember` | #ff3a1e | One red line per image (the K05 laser). Never UI text or a fill. |
| `--swiss` | #da291c | The Swiss cross only |
| `--paper`, `--ink` | #f3f2ee, #0a0a0a | The measurement card |

## Type
Archivo (OFL, variable weight and width) for display and text; Saira (OFL) for data, labels and numerals.
Headlines Archivo wdth 112 wght 580; record numerals wght 200–220, tabular; wordmark wdth 125 tracking 0.32em.
Fluid scale up to 2560 in `globals.css` (`--fs-record` … `--fs-fine`); classes `.t-h1` … `.t-fine`.

## Page
| # | Section | Media | Motion (reduced motion: final state, no pin) |
| --- | --- | --- | --- |
| 1 | Hero | K01 base → beam crossfade. ≥ 1000 px: words (h1, the owner's lead, then "Built to last five years." in white), Reserve Now and price line in the left 7 columns, the still moved right 21vw (racket about 54% of the screen tall); phones: words, racket, Reserve Now on the floor (short phones drop the lead and the five-year line) | Load reveal; scroll drift and veil (the button stays opaque) |
| 2 | Spec strip | Four numbers (0 seams, 15 µm, 0 drilled holes, 5 years), then G01 whole in its own band (full sheet ≥ 1240 px, front view below) | Numbers rise on entry; drawing draws on |
| 3 | Unibody (pinned ≥ 900 px; `#unibody`) | K02 edge-on ("Zero seams. No joint to work loose.") → K03b tubular → K03 cut-through + G07 sections ("Open core" / "Sealed core") → sealed core ("The core never touches the air.", three callouts, and an amber trace on K03: one line around the stippled core, both bores lit and lined, `SealedCoreTrace`) → three proofs | Light line sweep, beat crossfade; for the sealed core K03 slides right, the words rise in the left columns and the trace draws once (stacked on phones and in reduced motion, without the trace); the words and trace leave before K03 moves back, and in beat C K03 settles smaller (and higher if needed) wherever full frame would run under the proofs |
| 4 | Born whole | K06 mould, Swiss lockup, G13 badges | Scrubbed push-in, cavity glow |
| 5 | Precision (pinned ≥ 900 px) | K05 scan, record counter; G03 tolerance graph | Counter 500 → 15 µm while the K05 frame settles (scale 1.08 → 1); caption under the numeral |
| 6 | Holes | K04 macro + G05 fibre flow; G06 drilled vs moulded (the body adds that a drilled hole opens the core), each plate lit like a light table around its dark bore (fill rule) | Ring glow, flow advection |
| 7 | Durability (`#durability`) | G14 lifespan graph (0 to 5 years: most padel rackets 1 to 2, KINETIQ 5). ≥ 1000 px: copy in columns 1–4, G14 in columns 6–12; then four reasons (the sealed core first; four across ≥ 1200 px, two by two from 900 px, on a shared title row and body row so every body starts on one line) and two fine-print lines: "*Built to last five years." and its usage profile, and what "three times longer" is measured against (†, raised and tight to its full stop) | G14 draws on entry: window, typical lane, KINETIQ trace behind a glow head, then the five-year numeral |
| 8 | Feel | G02 vibration graph | Graph reveal on entry |
| 9 | Identical | K07 five rackets; G04 spikes, G08 card; CTA 2 | Rise on entry |
| 10 | Choose your feel | K08 pair (Command 3K, Pace 12K) | Rise on entry |
| 11 | Editions | Three cards (K08 left / K11 Command pair / K09), every card with its includes and one price foot line. ConQuer and VanQuish are whole-card links to /reserve?tier= with the arrow; InviQtus is not a link (no hover, no arrow): "By invitation" in its foot and a quiet "Have an invitation?" link to /reserve?invite ("Invitations open soon." while `INVITE_CODES` is empty). Two fine-print lines under the cards, one per marker: the design life (*) and the InviQtus guarantee (‡, its terms and the legal-rights line) | Rise on entry |
| 12 | Finale | K01 in its beam over the horizon, one screen with the footer: ≥ 1000 px the hero mirrored (racket left, words right); phones: racket, then words. Line: "Zero seams. Fifteen microns. Five years." | Rise on entry |
| /reserve | Sticky gallery (per-edition slides; VanQuish opens on K11, the pair in the chosen feel, then K10 and the two matching sample cards, B behind A with only its header and set number showing, never the text-free thumb; gallery controls) + options column. Before the edition streams in, a neutral shell (lit stage, empty column: no edition, price or count), so a ?tier= link never paints another edition first. The column fades under the header and above the sticky Due Today bar instead of being sliced | Tier cards (G11 glyphs; InviQtus shown whole but locked: no hover, press or selection until an invitation code unlocks it), feel swatches (one feel per set), trust list, Due Today, Pay with Card → form in place | Crossfades, fields rise 8 px |

Stills are exported by `scripts/stills.mjs` from 16-bit Blender masters (not committed) to AVIF + WebP with
phone crops (`src/content/stills.json`), and rendered with `<Still>` (`src/components/media/Still.tsx`).
Graphics live in `src/components/graphics/` with review pages at `/lab/<id>` (dev only).

## Micro-interactions
Pressables scale 0.97 on `:active`; hover only behind `(hover: hover) and (pointer: fine)`; transform and
opacity only, 150–300 ms ease-out (`--ease-out`); exits faster than entries.

## NDA gate (owner, 2026-10-22)
Part of the investor presentation and the first screen anyone sees: `/nda`, shown in place of every page until the
visitor has declared the NDA (mechanics in `CLAUDE.md`, "NDA gate"; words in `src/content/nda.ts`). No product image,
no product copy, no claim.
- Stage: the graphite floor (`--stage`) with a soft pool of light behind the words (about a fifth of any viewport at
  luma 40 or more), one beam from above, a warm amber glow on the G09 horizon line at the bottom, and the 3% tech
  grid fading toward the edges. The KINETIQ wordmark sits where the header puts it (not a link).
- One centred panel: the amber eyebrow "Confidential" (Saira, tracked capitals), the h1 "Shared under NDA." (`t-h1`,
  most of the width at 2560), then one step at a time in the same place below it:
  1. "Have you signed the KINETIQ non-disclosure agreement?": "Yes, I have signed it" (primary) and "Not yet"
     (secondary), two equal columns, stacked full width on phones.
  2. Yes: "Enter your email to open the presentation.", the label "Email", one field and "Open the presentation"
     (side by side from 640 px, the field about two-thirds of the row), and the quiet line "Your email is kept in a
     cookie on this device, so you only do this once." An error takes that line's place (an `alert` live region), so
     the step never changes height. A quiet "Back" beside the line returns to step 1 (focus on Yes).
  3. Not yet: "The presentation opens once the NDA is signed. Ask your KINETIQ contact for the agreement." and Back.
- Motion: a load reveal (eyebrow, title, step: rise 8 px, 320 ms, 60 ms stagger). The steps share one grid cell and
  cross-fade without overlapping (exit 150 ms, enter 240 ms after 120 ms; transform and opacity). A step opened from
  the keyboard appears at once; focus moves to the field, the message, or back to Not yet. Leaving: a void veil fades
  in under the wordmark (240 ms) and the page reloads at the same URL, whose header puts its wordmark in the same
  place, so there is no flash. Arriving: the page's first frame is painted under the same void, which lifts over
  600 ms (on /reserve once the linked edition is in), so leaving and arriving read as one move. Reduced motion: all
  instant. Text 16 px and up; Enter submits. The tab shows the site icon (`src/app/icon.svg`, a K over an amber line).

## Languages
English only at launch (`lang="en"`). Archivo and Saira load `latin` and `latin-ext`.
