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
One racket in every image (render audit, 2026-10-22): the canonical racket in `CLAUDE.md` ("Stills and graphics"),
with the same outline, 42 holes (a crown of 8 along the top, 34 below), edge and handle in every still and graphic.
Only the face changes with the feel: Command is white 3K twill, and the racket in any image that names no feel; Pace is
black 12K (owner, 2026-10-22). The cap's engraved mark is the Q, the company logo. The carbon weave is the texture the
owner loves: light every face-on shot so the tows resolve (K05, K08, K11).

## Owner rules (2026-10-21)
- Fill wide screens. Content spans a 12-column grid with margins 20 / 64 / 128 px (390 / 1440 / 2560);
  imagery is full-bleed. No left-aligned column beside an empty half, no 1200 px container on a 2560 screen.
- Never 90% black. Fill rule (checked by the harness at every screenshot): at most 40% of a viewport at
  luma ≤ 12, at least 8% at luma ≥ 40, and no flat-black vertical strip a quarter of the viewport wide.
  Fix a failing section with light, a lift or a graphic; never lower the thresholds.
- Text larger than Tesla's 14 px: nothing below 15 px anywhere, body 18 px and up, 16 px minimum on /reserve.
- No motion toggle. `prefers-reduced-motion` is honoured silently.
- Weights always carry a decimal (355.0 g, ±1.0 g), never a range.
- Copy (owner, 2026-10-22): plain, sincere sentences, as Jony Ive would say them. Each says what we made and what it
  does for the player; a superlative is backed by one fact. No two-beat slogans, stacked fragments or "Not X. Y."
  pairs; no "premium", "simply", "incredibly", "monolithic" or other lofty words; no middle dots; no workshop, town,
  golf or supply-chain talk; never the banned lines listed in `src/content/copy.ts`. The owner's hero sentence stays
  verbatim.
- "One piece" is retired (owner, 2026-10-22), except in the owner's hero sentence: construction words are
  "unibody" and "Zero seams", scoped to the frame ("Zero seams, so there is no joint to work loose."); never "zero
  weak points" or "nothing to come apart" (absolute, CLAIMS.md row 8b), never "first unibody".
  Durability is "Built to last five years", said in the Durability section only (owner, 2026-10-22: never the hero,
  the finale or the edition includes), its usage profile told by point 4's own sentence; "guarantee" only for One of
  Ten ("five-year guarantee", never "lifetime guarantee"), whose guarantee include is the one edition line that names
  five years, because the owner asked for that guarantee.
- Sealed core (owner, 2026-10-22; CLAIMS.md rows 30 to 34): the carbon shell closes around the whole EVA core and lines
  all 42 holes, so the core never touches the air; the EVA is Swiss-made (country level only) and injected straight
  into the mould. Told once per place: the reveal in Unibody, the drilled hole in Holes, the result in Durability
  ("made to last three times longer than the same core left open"). It keeps out sweat, humidity and UV, never
  heat; never "airtight", "waterproof" or "first".
- Sweet spot (owner, 2026-10-22; CLAIMS.md row 6b): told once, in its own section right after the hero, the way Apple
  tells an edge-to-edge display (see "Sweet spot" below). A design ceiling, never "bezel", "zero", "100%" or a
  comparison with a tubular racket.
- One landing CTA, "Reserve Now", only in the hero, at the Identical peak, in the finale and as the compact
  header button after the hero. On /reserve: "Pay with Card", then "Place Reservation", nothing after it.
  The invitation unlock on /reserve ("Have an invitation?", then "Unlock") is a quiet control for invitees
  only, above the options; it is not a CTA.
- Editions (owner, 2026-10-22): one racket in three editions, KINETIQ, First 500 and One of Ten. The names count and
  order the rackets and never describe them; every edition holds the same racket, and the copy says so plainly ("It
  is the same racket you will find in every edition."). Write "First 500" and "One of Ten" in full, never with ™.
  First 500 at €990 is the premium edition (numbered 001 to 500, first out of the mould, first to ship; KINETIQ's
  include says it ships after the First 500 sets, in the same month): never compared with the single price. Status
  tags are states, never verbs: Available, Limited, Invite Only.
- One of Ten is invite only: shown whole everywhere but never interactive for other visitors (no hover, press,
  focus, arrow or selected glow; not a link on the landing page) until a valid invitation code unlocks it on /reserve.
- No small print (owner, 2026-10-22): no footnote markers (*, †, ‡, §) and no fine-print lines anywhere. A qualifier
  that keeps a claim honest is part of a plain sentence in the body copy, or is dropped; graphics with unmeasured data
  keep their short "Illustrative" caption.
- The EU legal-guarantee notice and the One of Ten GARAN label (CLAIMS.md row 29 and the note under the tables)
  are fixed EU artwork that overrides the palette, type and 15 px rules. Neither is built yet: both wait for
  the owner's documented exception.

## Colour tokens (`globals.css`)
| Token | Hex | Role |
| --- | --- | --- |
| `--void` | #060607 | Page background |
| `--stage` / `--lift` | #111113 / #2b2b31 | Graphite section floor and the radial lift behind graphics (G10) |
| `--graphite`, `--graphite-2`, `--field` | #18181b, #202024, #141417 | Cards, secondary buttons, inputs |
| `--hairline`, `--edge`, `--grid` | #2c2c31, #6b6e76, #26262a | Rules, input borders, drawing grids |
| `--text`, `--steel`, `--muted` | #f5f5f3, #c9ccd1, #9b9ea6 | Headlines and primary CTA fill, leads and labels, captions and quiet notes (7:1+ on --void) |
| `--amber`, `--amber-hot` | #e3a467, #ffe2bf | Data glow, light lines (G09), selected edges, the lit sweet spot (G15). Never body text. |
| `--ember` | #ff3a1e | One red line per image (the K05 laser). Never UI text or a fill. |
| `--swiss` | #da291c | The Swiss cross only |
| `--paper`, `--ink` | #f3f2ee, #0a0a0a | The measurement card |

## Type
Archivo (OFL, variable weight and width) for display and text; Saira (OFL) for data, labels and numerals.
Headlines Archivo wdth 112 wght 580; record numerals wght 200–220, tabular; wordmark wdth 125 tracking 0.32em.
Fluid scale up to 2560 in `globals.css` (`--fs-record` … `--fs-fine`); classes `.t-h1` … `.t-fine`.

## Page
Three movements, one idea per screen (batch 3, 2026-10-22): Meet it (what the racket does for you, then why), Prove it
(how it is made, how exact it is, how long it lasts, then the whole drawing as a recap), Choose it (sameness, feel,
edition). The first scroll after the hero holds one racket, one headline, two lines and two numbers.

| # | Section | Media | Motion (reduced motion: final state, no pin) |
| --- | --- | --- | --- |
| 1 | Hero | K01 base → beam crossfade. ≥ 1000 px: words (h1 and the owner's lead, nothing after it), Reserve Now and the price line ("From €410, fully refundable, and shipping in January 2027.") in the left 7 columns, the still moved right 21vw (racket about 54% of the screen tall); the floor fades into the sweet-spot section's first colour, rgb(26 25 25), over the scroll veil (phones too), so the beam never ends on a hard line. Phones: words, racket, Reserve Now on the floor (short phones drop the lead; the price line wraps, balanced) | Load reveal; scroll drift and veil (the button stays opaque); ≥ 1000 px the racket fades out between 10% and 32% of the hero scrolled, so it is gone before G15 (or K12) rises beside it and the two rackets only cross at low light |
| 2 | Sweet spot (`#sweet-spot`) | K12 once exported (K12-base, then K12-full crossfading over it); until then G15, which reads on its own. ≥ 1000 px: eyebrow "Sweet spot", "Edge to edge.", two lines and the lockup ("Nearly 94%" and 4 mm under one amber hairline) in columns 1 to 5; the racket on the right, where the hero's stood (K12 full bleed below the header: the whole 16:9 frame, centred and feathered into the floor on every side; the caption under the lockup in columns 1 to 5). Phones: headline, image, lines, lockup. Not pinned, so no Skip link. Details under "Sweet spot" | ≥ 1000 px one scrub as the section enters (its top at 85% of the screen to its centre at the centre): after a short wait (0.12 of it, while the hero's racket fades out) the racket rises, the light spreads from the sweet spot to the 4 mm line, then the lens; the words rise once. Below 1000 px the image fades in and each block rises on entry |
| 3 | Unibody (pinned 2 screens ≥ 900 px; `#unibody`) | Beat A: K02 edge-on, "It feels like one thing in your hand." (its body opens "We left out the frame tube.": the cause is told here, once), three callouts placed under the parts they name (handle, bridge, rim; a three-column row in the same proportions when stacked ≥ 900 px; a list on phones, rim first). Pinned, the eyebrow, headline, lead, K02 and the callouts are one block centred in the stage below the header (K02 hangs from its racket band and feathers into the graphite above and below it); stacked ≥ 700 px the words come first, then K02 and the callouts; phones open on the eyebrow and headline, then K02 upright (its top and bottom feathered), then the lead and the callouts. Its first colour is the sweet spot's last, rgb(19 20 22). Beat B: K03b tubular → K03 cut-through + G07 sections ("Open core" / "Sealed core"), "The shell is the frame.". The sealed core ends the chapter: "The core never touches the air.", three callouts, and an amber trace on K03 (one line around the stippled core, both bores lit and lined, `SealedCoreTrace`). Beat C (the three proofs) is retired; the Skip link lands on Feel | Light line sweep (0.02 to 0.24 of the timeline), then the callouts handle → rim (from 0.12, 0.02 apart), so the whole of beat A holds until 0.62 (over 400 px of scroll on a 900 px screen); beat crossfades (beat A leaves before beat B arrives); for the sealed core the words leave the shell first, K03 slides right, the words rise in the left columns and the trace draws once (stacked on phones and in reduced motion, without the trace) |
| 4 | Feel (`#feel`) | G02 vibration graph; "You feel exactly where you met the ball." and three points (the third "The head twists less."). Unibody has just told the cause, so Feel names the joint once (point 1) and never the tube | Graph reveal on entry |
| 5 | Born whole | K06 mould, Swiss lockup, G13 badges | Scrubbed push-in, cavity glow |
| 6 | Precision (pinned ≥ 900 px) | K05 scan, record counter; G03 tolerance graph | Counter 500 → 15 µm while the K05 frame settles (scale 1.08 → 1); its line ("About a fifth of a human hair.") under the numeral, in view from the first frame |
| 7 | Holes | K04 macro + G05 fibre flow; G06 drilled vs moulded (the body adds that a drilled hole opens the core), each plate lit like a light table around its dark bore (fill rule) | Ring glow, flow advection |
| 8 | Durability (`#durability`) | G14 lifespan graph (0 to 5 years: most padel rackets 1 to 2, KINETIQ 5). ≥ 1000 px: copy in columns 1–4, G14 in columns 6–12; then four reasons (the sealed core first; four across ≥ 1200 px, two by two from 900 px, on a shared title row and body row so every body starts on one line); the fourth, "Made for regular play.", gives the usage profile (about 160,000 ball strikes) and the promised fatigue tests in its own sentence. No fine print: the only section that says five years | G14 draws on entry: window, typical lane, KINETIQ trace behind a glow head, then the five-year numeral |
| 9 | Specifications (`#specifications`) | Eyebrow "Specifications" and "As large as the rules allow." beside the lead from 900 px; six cells ruled like a spec sheet, every figure to one decimal (owner, 2026-10-22: 455.0 mm, 260.0 mm, 38.0 mm, 355.0 g, 250.0 mm, then 42 holes moulded; G01 and the Two feels closing line use the same precision; 3 × 2 from 900 px, 2 × 3 on phones); then G01 whole (full sheet ≥ 1240 px, front view below), on two lifts. G01 draws the canonical racket: Ø14.0 ×8 and Ø12.4 ×34, the 4 mm line where the flat face ends, the head flowing into the handle, the overgrip's helical wrap and the black cap engraved Q, the logo (named in callouts on the full sheet); Section A-A cuts below the hole field, B-B through the top row | Cells rise on entry; the drawing draws on |
| 10 | Identical (CTA 2) | K07 five rackets; G04 spikes, G08 card; "Every KINETIQ is made to the same weight and balance."; Reserve Now with the hero's price line. From 700 px K07 spans the width at its own 16:9, anchored to the section's foot, and the section is the words plus two thirds of K07's height, so the words always end a third of the way down it, over the dim tops of the light shafts and clear of the racket heads (every pixel under the lead 4.5:1 or more against `--steel`); above it the floor is K07's own top colour. Phones: the words over a lift, then K07's trio crop | Rise on entry |
| 11 | Choose your feel (`#feels`) | K08 pair (Command white 3K left, Pace black 12K right), each feel's name and "Built for control" / "Built for power" (steel, lead size) directly under its racket's cap and shown with the photo, so the pair is never two unnamed rackets; then the compare, one column per feel: one character line (what we made, then what it does for you), and four ruled rows, label left and value right at 18 px and up (Feel, Face, Core, Suits; the Face row is a spec, the colour and the weave, never a repeat of the line). The two lines are kept the same length and set in the ruled rows' box, left-aligned on the labels' edge, so they wrap alike and the two columns read as one grid. From 700 px the columns share their rows through CSS subgrid, so every row sits level with its counterpart; phones stack Command, then Pace. Then the closing line across both columns under a full-width hairline: only the core and the face differ | Rise on entry |
| 12 | Editions (`#editions`) | The h2 "We make one racket, in three editions." (each clause kept whole) and its lead (`editionsIntro`), then three cards (K12-base portrait / K11 Command pair / K09; below 600 px the frames are square, KINETIQ's racket shown whole with its sides feathered), every card with its includes (KINETIQ's four follow First 500's order, racket, number, card, shipping, so no card shows an empty band above its price) and one price foot line. The availability tags are all in the amber family (Available and Limited amber, Invite Only amber-hot), so none reads as a control. KINETIQ and First 500 are whole-card links to /reserve?tier= with the arrow; One of Ten is not a link (no hover, no arrow): "By invitation" in its foot while invitations are open, and a quiet "Have an invitation?" link to /reserve?invite ("Invitations open soon." while invitations are closed). Nothing under the cards: no markers and no fine print (owner, 2026-10-22). The intro's light spills about 100 to 130 px up into Choose your feel on purpose, so the two sections meet without a hard line; Choose your feel's words sit above it (z-index 1) | Rise on entry |
| 13 | Finale | K01 in its beam over the horizon, one screen with the footer: ≥ 1000 px the hero mirrored (racket left, words in the right 7 columns as the hero's sit in the left 7; the line a step under the h2 size at a 24ch measure, three or four even lines); phones: racket, then words. Line: "Each KINETIQ is moulded in Switzerland as one carbon shell, to within 15 microns." (Born whole, Unibody and Precision in one whole sentence, answering the hero's "moulded to 15 microns"; never the five years or "the feel you choose", which Two feels and Editions say); under it, the hero's price line | Rise on entry |
| /reserve | Sticky gallery with per-edition slides and gallery controls. KINETIQ opens on K01, shows K12 second for Command once it is exported (K12-base, with K12-full fading in), then K02, K04 and K08's Command racket, and ends on the racket's own measurement card (serial KQ-000427, in the chosen feel); in Pace it opens on K08's Pace racket and its card is KQ-000428's, the racket K08 shows. First 500 opens on K11, the set in the chosen feel with 027/500 on both throats, then K10 (Command only: its throat is white twill) and the two matching sample cards: B sits behind A with only its header and set number showing (below 1024 px its set number alone, so the pair fits the 4:5 frame whole, A at the single card's width in a tighter rhythm, its text at 16 px; under 390 px wide the pair shows at 94%), never the text-free thumb and never cut off by the frame. One of Ten opens on K09, then G12. The gallery follows the slide on show, not its position: a change of feel keeps the measurement card or the feel's racket in view (to compare), and otherwise moves to the chosen feel's racket; a new edition starts on its first slide. Beside the gallery, the options column, headed "Reserve your KINETIQ" (the cards name the editions, so the base edition's name, the brand's, is not repeated in the chrome: each card's includes sit under "Included"); the sticky bar reads the racket count ("One racket", "Two rackets") over Due Today. Before the edition streams in, a neutral shell shows (lit stage, empty column: no edition, price or count), so a ?tier= link never paints another edition first. The column fades under the header and above the sticky Due Today bar instead of being sliced | Tier cards (G11 glyphs: one racket, two, three; One of Ten shown whole but locked, with no hover, press, focus or selection until an invitation code unlocks it), the feel picker (Command and Pace stacked, two across once each can be 320 px wide; each shows name and sub, the spec in Saira and one line, with the helper line under them), trust list, Due Today, the order line, Pay with Card → form in place | Crossfades; the K12 reveal (900 ms after 350 ms, out in 200 ms, instant under reduced motion); fields rise 8 px |

Stills are exported by `scripts/stills.mjs` from 16-bit Blender masters (not committed) to AVIF + WebP with
phone crops (`src/content/stills.json`), and rendered with `<Still>` (`src/components/media/Still.tsx`). K12 (the
sweet spot) has two passes that register pixel for pixel, `K12-base` and `K12-full`, each with a `wide` and a
`portrait` crop (the 4:5 phone window, x 0.435 to 0.885 of the master).
Graphics live in `src/components/graphics/` with review pages at `/lab/<id>` (dev only); G15 is the sweet spot
(`SweetSpotField`, `/lab/g15`).

## Sweet spot (owner, 2026-10-22)
The owner: make a claim for how big the sweet spot is, the way Apple claimed almost no border on the iPhone and Apple
Watch screens, assuming the sweet spot is as big as it can theoretically be.
- **The claim, told as Apple tells a display:** a vision line, one area share and one border in millimetres (Apple
  Watch Series 7: "nearly 20 percent more screen area", "borders at just 1.7 mm"). Apple adds a footnote that says
  what is counted; here there is no footnote (owner, 2026-10-22: no small print), so line 1 says it in its own words.
  Eyebrow "Sweet spot" and h2 "Edge to edge." (the section is labelled by both), two lines in the plain voice (the
  first about the face only, ending "we designed all of that flat face to be sweet spot": what is counted, and that it
  is a design; the frame tube is Unibody's to tell), then the lockup "Nearly 94% of the face is sweet spot" ("Nearly"
  at the unit's size, on the numeral's baseline) and "4 mm from the sweet spot to the edge", Saira at weight 200,
  tabular, each item read as a sentence. Caption: "Illustrative. The sweet spot as designed." No comparison in the
  copy or the drawing. The words rise on opacity only (never visibility), so the claim stays in the accessibility
  tree.
- **The numbers come from the geometry,** never typed by hand: `graphics-sweetspot.ts` takes the face above the
  bridge (y ≥ −86.5 mm, 531.5 cm²) and insets it 4 mm from the outline and 4 mm above the throat (498.7 cm², 93.8%),
  and `SWEET_CLAIM` rounds it as Apple rounds a display: down to the whole number, or up only with "Nearly" (Apple
  Watch Series 7: "nearly 20 percent"; a 5.85-inch iPhone X display was sold as 5.8-inch). The section, G15's text
  alternative and K12's alt are built from it; /lab/g15 checks it against the geometry. If `racket-shape.ts`
  changes, the lockup and the alt text change with it.
- **The image:** K12, a face-on white Command racket (serial KQ-000427 on the throat, the Q on the cap) whose face
  lights up warm and even to 4 mm from the edge, the weave reading through the light; the holes stay dark, the 4 mm
  band and the rim stay bare carbon. Base (the white racket under a soft pool of light) and full (the face dimmed
  around the lit field) are one render in two passes, so the page crossfades between them. Wide master 3200 × 1800
  with x 0 to 0.45 kept clear for the words.
- **G15** stands in until K12 is exported, drawn as K12's full pass: the canonical silhouette face-on in white 3K
  twill (an SVG pattern: the warp a step darker than the weft, rounded tows, fine crevices) in a low studio light, the
  field lit warm white and even to the 4 mm line with the weave reading through it (luma about 214 with the twill
  spanning about 30 levels at 1×), an amber hairline on the line, the holes open with each bore's lit wall and lip on
  the lower right, the overgrip's wrap and the Q on the cap, a steel rim hairline, one clear-coat gloss line, and a 6×
  lens on the edge with the dimension "4 mm" (HTML, 15 px and up). The lens is drawn at its own scale, never the
  racket scaled up (`lensDetail` in `graphics-sweetspot.ts`): the flat band in the racket's carbon tone at that spot,
  the 1.5 mm edge radius as a highlight, the lit field with a fine hatch to its amber line, the page's own graphite
  beyond the edge; the dimension's arrows end on the 4 mm line and the outline, with short extension ticks. Variants: "wide", "portrait" (phones; the lens
  beside the handle) and "auto" (portrait below 700 px). No ember, no tube line.
- **Layout:** ≥ 1000 px the words in columns 1 to 5, centred in one screen, and the image on the right where the hero
  racket stood (K12 full bleed behind the words, below the header: the whole 16:9 frame, centred, no taller than keeps
  its rim inside the right margin, its edges feathered; the caption under the lockup); 700 to 999 px the wide crop in a
  4:5 box; phones the portrait crop. Below 1000 px the box's edges feather into the floor too, and K12's own backdrop
  is the lift (no section lift behind it, which showed as a lighter rim).
  The section's foot ends on Unibody's first colour, rgb(19 20 22) (checked with a pixel probe). Fill rule: the racket sits on a graphite lift, never flat black.
- **Motion:** the light never scales: a soft mask disc grows from the sweet spot (about 25 mm above the head centre)
  and reveals a field that is already whole. K12's full pass crossfades over its base (scrubbed on wide screens,
  1.2 s on phones). Reduced motion and the server render show the final state: the face lit, every word visible.

## Micro-interactions
Pressables scale 0.97 on `:active`; hover only behind `(hover: hover) and (pointer: fine)`; transform and
opacity only, 150–300 ms ease-out (`--ease-out`); exits faster than entries.
Skip links on the pinned chapters (Unibody, Precision) appear only on keyboard focus: visually hidden otherwise (still
in the tab order), shown at once, with no animation, at the top of the pinned stage under the header, 44 px tall,
`--text` on the void at 85% with an `--edge` border and the focus ring. Focusing one brings its chapter's first
screen into view; Enter jumps to the next section and moves focus there. Mouse and touch visitors never see them.

## NDA gate (owner, 2026-10-22)
Part of the investor presentation and the first screen anyone sees: `/nda`, shown in place of every page until the
visitor has declared the NDA (rules in `CLAUDE.md`, "NDA gate"; words in `src/content/nda.ts`). No product image,
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
  instant. Text 16 px and up; Enter submits. The tab shows the site icon (`src/app/icon.svg`, the Q, the company mark, over an amber line).
- Mechanics:
  - `src/proxy.ts` (Next 16 "proxy", Node runtime) skips only `/_next/static/`, the HMR socket and the two icon files
    (`/icon.svg`, `/apple-icon.png`, from `src/app/`); each exclusion is anchored, so `/iconography` or `/_next/imagex`
    cannot borrow it. Without the cookie a page is rewritten to `/nda` (the URL stays as typed); assets, `/api/*` and
    other `/_next/*` paths get an empty 403. `POST /api/nda` always passes; `/nda` with the cookie redirects to `/`.
    Dev only: `/__nextjs_*` (the error overlay) passes.
  - The cookie (`src/lib/nda.ts`): `kq_nda`, base64url of `{"email","at"}`, HttpOnly, SameSite=Lax, Secure on https,
    Path=/, 365 days; valid when it decodes and the email looks valid. Known limit: `/_next/static/` chunks are served
    without it, and the landing and /reserve chunks carry edition copy, so a chunk URL a cleared visitor forwards
    stays readable.
  - The root not-found's footer drops "100% Swiss Made." (`brandLine={false}`), because its tree ships with the gate.
  - Arrival: the gate sets `kq_nda_tried` in sessionStorage and reloads; the head script (`lib/motion-preference.ts`)
    then marks `html[data-arrive]` and the page lifts out of the void veil (globals.css; /reserve holds it until its
    neutral shell is replaced by the linked edition). `components/nda/Arrival.tsx` clears the flag and the attribute.

## Languages
English only at launch (`lang="en"`). Archivo and Saira load `latin` and `latin-ext`.
