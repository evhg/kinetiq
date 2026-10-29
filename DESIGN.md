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
  weak points" or "nothing to come apart" (absolute, CLAIMS.md row 8b), never "first unibody" except in the owner's
  own Unibody eyebrow, "The first Unibody" (2026-10-23, CLAIMS.md row 36).
  Durability is "Built to last five years", said in the Durability section only (owner, 2026-10-22: never the hero,
  the finale or the edition includes), its usage profile told by point 4's own sentence; "guarantee" only for One of
  Ten ("five-year guarantee", never "lifetime guarantee"), whose guarantee include is the one edition line that names
  five years, because the owner asked for that guarantee.
- Sealed core (owner, 2026-10-22; CLAIMS.md rows 30 to 34): the carbon shell closes around the whole EVA core and lines
  all 42 holes, so the core never touches the air; the EVA is Swiss-made (country level only) and injected straight
  into the mould. Told once per place: the drilled hole in Holes, then the reveal in its own pinned chapter right after
  it (owner, 2026-10-23: the sealed core follows the moulded holes), then the result in Durability ("made to last three
  times longer than the same core left open"; the chapter's bullet says "Three times the life of an exposed EVA
  core"). It keeps out sweat, humidity and UV, never heat; never "airtight", "waterproof" or "first".
- Patent (owner, 2026-10-23): the one-mould process is "patent pending" (Born whole, Holes, the G13 badge), never
  "patented". Holes adds the owner's point that no drilling, no exposed foam and a smooth carbon wrap around every hole
  are, together, on no other racket on the market (CLAIMS.md row 37).
- Tolerances (owner, 2026-10-23): weight ±1.0 g, balance ±0.1 mm.
- Sweet spot (owner, 2026-10-22; CLAIMS.md row 6b): told once, in its own section, the way Apple tells an
  edge-to-edge display (see "Sweet spot" below); since 2026-10-28 it is the payoff after how the racket is made, never
  the first claim. A design ceiling, never "bezel", "zero", "100%" or a
  comparison with a tubular racket.
- One landing CTA, "Reserve Now", only in the hero, at the Identical peak, in the finale and as the compact
  header button after the hero. On /reserve: "Pay with Card", then "Place Reservation", nothing after it.
  The invitation unlock on /reserve ("Have an invitation?", then "Unlock") is a quiet control for invitees
  only, above the options; it is not a CTA.
- Editions (owner, 2026-10-22): one racket in three editions, KINETIQ, First 500 and One of Ten. The names count and
  order the rackets and never describe them; every edition holds the same racket, and the copy says so plainly: the Editions h2
  and lead on the landing, and on /reserve the edition helper "Every edition holds the same racket, in the feel you
  choose." Write "First 500" and "One of Ten" in full, never with ™.
  First 500 at €990 is the premium edition (numbered 001 to 500, first out of the mould, first to ship; the KINETIQ
  and One of Ten includes say they ship after the First 500 sets, in the same month): never compared with the single
  price. Status tags are states, never verbs: First Edition, Limited, Invite Only (owner, 2026-10-28: "Available" did
  not sound exclusive or scarce; KINETIQ is the racket's first edition, made in the first production run and shipping
  in January 2027, CLAIMS.md row 45).
- One of Ten is invite only: shown whole everywhere but never interactive for other visitors (no hover, press,
  focus, arrow or selected glow; not a link on the landing page) until a valid invitation code unlocks it on /reserve.
- No small print (owner, 2026-10-22): no footnote markers (*, †, ‡, §) and no fine-print lines anywhere. A qualifier
  that keeps a claim honest is part of a plain sentence in the body copy, or is dropped. No "Illustrative" captions
  (owner, 2026-10-23: "Do apple or tesla put it on their product launch pages?"; risk accepted in CLAIMS.md): the
  graphics carry no caption, only their text alternatives.
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
A climactic rise (owner, 2026-10-28: "Re-plan the storytelling and introducing the features and claims to create a
climactic rise"): make, peak, payoff, buy. Order: 1 Hero, 2 The first Unibody, 3 Space-grade carbon, 4 Born whole,
5 Precision, 6 Moulded holes (the visual peak), 7 Sealed core, 8 Edge to edge (the sweet spot, the payoff: "This is
what all of that gives you on court."), 9 Direct feel, 10 Built to last five years, 11 Identical, 12 Two feels,
13 Specifications, 14 Editions, 15 Finale. How it is made rises from what it is (the unibody) through what it is made
of, the one mould and 15 microns to the moulded holes, the image the owner feels (K04, the render language for every
new still: close, raking light, the weave), and what they keep closed; the payoff tells what that gives the player;
then the buy. Every chapter opens on an amber eyebrow except the Precision record, whose sentence leads into the
numeral. Skip links, in order: Unibody → Space-grade carbon, Precision → its graph, Holes → drilled vs moulded,
Sealed core → Sweet spot, Feel → Durability. Seams: the
hero's floor ends on Unibody's rgb(19 20 22); the sweet spot runs --stage to --stage, between the sealed core and Feel.

| # | Section | Media | Motion (reduced motion: final state, no pin) |
| --- | --- | --- | --- |
| 1 | Hero | K01 base → beam crossfade. ≥ 1000 px and 4:5 or wider (the split layout): words (h1 and the owner's lead, nothing after it), Reserve Now with the feel toggle beside it (one row from 700 px; on phones the toggle, two small swatches with their names, sits under the racket like a caption, above the full-width Reserve Now, and the racket scales to 0.88 about its crown, 0.75 on phones 740 px tall or less, 0.68 at 650 px or less, so its foot clears the toggle; "Feel toggle" below) and the price line ("From €410, fully refundable, and shipping in January 2027.") in the left 7 columns, the still moved right 21vw (racket about 54% of the screen tall); the floor fades into the Unibody chapter's first colour, rgb(19 20 22), over the scroll veil (phones too), so the beam never ends on a hard line. Phones: words, racket, Reserve Now on the floor, and the lead always shows (phones 740 px tall or less, which is Safari on most iPhones, set the words a step smaller and the racket smaller, its frame feathered at the sides and top; the price line wraps, balanced). Portrait tablets (700 to 999 px and portrait, or any window narrower than 4:5, such as an iPad Pro) take the phone layout with the phone master, drawn from the band between the words and Reserve Now (a size container), so the crown clears the lead and the foot clears the button at any portrait size | Load reveal; scroll drift and veil (the button stays opaque); the swivel (owner, 2026-10-23): as the hero scrolls away the lit racket turns about its handle, 0° to about 35° (36 Blender frames, `scripts/sequence.mjs`, per feel and per layout: `K01-swivel-<feel>-desktop|phone`), finished by 26% of the hero scrolled in the split layout and by 30% in the portrait one (phones, portrait tablets; owner, 2026-10-28: at 60% the turn ran on after the racket had slid under the header; the layout is chosen by the same PORTRAIT query as the CSS, through one gsap.matchMedia conditions object, never range syntax, which older iOS cannot parse); `media/Swivel.tsx` (shared with Unibody's K02 swivel) draws only the rectangle that changes onto a canvas laid over the lit still with its own object-fit and position (frame 0 is the still, so the canvas shows from frame 1 and the handover is invisible), loads the frames from the load event, the first scroll or touch, or 1.5 s after mount, whichever comes first (Safari's load event, and in-app browsers', can come seconds late; Safari has no requestIdleCallback), coarse first, and starts once no gap is wider than 4; each frame decodes through createImageBitmap, else an <img>, a failed frame is retried once and its neighbours stand in; without a sequence for the feel or layout, with Save-Data, a quarter of the frames lost or reduced motion (iOS: Reduce Motion), it shows the still exactly as before; in the split layout the racket fades out between 10% and 32% of the hero scrolled, so Unibody's K02 arrives on a dark stage |
| 2 | Unibody (pinned 1.6 screens ≥ 900 px; `#unibody`) | Beat A: K02 edge-on, eyebrow "The first Unibody", "When you hold it, there is no boundary between the material and your experience." (two lines pinned; its body opens "We no longer need the frame tube.": the cause is told here, once; the owner's words, 2026-10-23), three callouts placed under the parts they name (handle, bridge, rim; a three-column row in the same proportions when stacked ≥ 900 px; a list on phones, rim first). ≥ 900 px the rim's callout is right-aligned and balanced, so its amber dash is inline and leads its first line (never left at the box's edge when the words wrap short of it), pinned and stacked alike. Pinned, the eyebrow, headline, lead, K02 and the callouts are one block centred in the stage below the header (K02 hangs from its racket band and feathers into the graphite above and below it); stacked ≥ 700 px the words come first, then K02 and the callouts; phones open on the eyebrow and headline, then K02 upright (its top and bottom feathered), then the lead and the callouts. Its first colour is the hero floor's last, rgb(19 20 22) (since 2026-10-28 it follows the hero). Beat B: K03b tubular → K03 cut-through + G07 sections ("Open core" / "Sealed core"), "The shell is the frame."; stacked ≥ 700 px beat B opens on its words too, then K03, then the two sections; phones show K03 in a square window on its 4:5 card crop, the slab whole and the frame feathered at both ends. Beat B ends the chapter: the sealed core, once its last beat, is its own chapter after Holes (7b). Beat C (the three proofs) is retired; the Skip link lands on Space-grade carbon | Light line sweep (0.02 to 0.24 of the timeline) along the racket's top edge, on the overgrip from the cap and on the shell along the head, then the callouts handle → rim (from 0.12, 0.02 apart), then (Release 4, 2026-10-28) the words, the callouts and the light line step aside (0.40; the turned face would rise behind the headline on short windows) and the racket turns about its handle until its face shows (0.42 to 0.60, K02's swivel: `K02-swivel-<feel>-desktop|phone`, 30 Blender frames, 0° to 35°, Command and Pace, `scripts/sequence.mjs`, drawn by the shared `media/Swivel.tsx` over the still, frame 0 being K02 itself) alone, and beat A leaves at 0.62; without a sequence the beat holds whole. Phones: the upright racket turns as it crosses the screen (its centre from 85% to 30% of the screen); the stacked 700 to 899 px layout crops K02 to its 18:5 band and keeps the still; reduced motion: the still only; beat crossfades (beat A leaves before beat B arrives), the tubular cut dissolving into the shell, then beat B holds. K03 feathers into the stage at both ends when stacked; pinned, its frame feathers 24% at both sides, so its right edge never stands as a wall |
| 3 | Space-grade carbon (`#space-grade`; owner, 2026-10-23) | Right after Unibody (2026-10-28): the material, then the mould. Eyebrow "Space-grade carbon", "We build it from the carbon made for space.", a lead in two whole sentences (the fibre and resin grades of space hardware and its engineering standards, written for extreme mechanical, thermal and environmental conditions; then, against "the standard carbon most padel rackets use", what that does for the player), then three points (strength without extra weight, solid through every layer, steady in heat and cold; three across from 900 px on a subgrid, as Durability's). Never a country, a maker, the factory, or defence or military wording (CLAIMS.md rows 41 to 44). Media (owner, 2026-10-29: "the morse code looking graphics under space grade carbon look out of place, rather show a piece of great looking carbon in a space setting"): K15 full bleed above the words (`K15-base` and `K15-full`, two passes of one render, and their `-pace` versions; wide, card and portrait crops), 16:9 at the screen's width (at most 86svh), the 4:5 card crop on phones, feathered at both ends: the canonical racket's crown (white 3K twill, black 12K in Pace) from 30 degrees above the face, its rim a rising arc, three crown holes on the face, floating over the limb of a dark planet with a thin warm atmosphere (amber on the sunward side, pale graphite away from it) and a few faint stars; no spacecraft, satellites, flags, logos, maker or country, and nothing military. The words below it: eyebrow and h2 in columns 1 to 6, the lead in 7 to 12 from 1000 px (stacked below), then the three points. K13 and G16 are off the landing (G16 lives on in `/lab/g16`; K13 stays exported). Its floor is `--stage` at both ends, after Unibody's graphite and before Born whole's head | The sun comes up: one scrub as the section enters (its top at 92% to 12% of the screen) brings the lit pass (K15-full) in over the base, from 0.15 to 0.85 of the scrub, while the frame settles (scale 1.06 → 1); the words and the points rise on entry. Reduced motion and the server render: the lit pass at rest |
| 4 | Born whole | K06 mould, Swiss lockup; no badge under it (the body names the patent-pending process), a band of floor before Precision | Scrubbed push-in, cavity glow |
| 5 | Precision (pinned ≥ 900 px) | K05 scan; one sentence that the numeral ends (owner, 2026-10-23): "Every racket is moulded with ultra-precision, exact to within" over the record "15 µm" (the h2, spoken "... exact to within 15 microns."; one line from 700 px, two on phones; its height, `--intro-h`, is taken from the numeral's height caps and the portrait frames' tops), with its line ("About a fifth of a human hair.") directly under the numeral at every width; ≥ 700 px in landscape the numeral is capped by the height as well as the width (`min(14vw, 39svh − 130px, 54.5svh − 8.75vw − 140px)`, 5.5rem to 22.5rem), so on windows shorter than 16:10 (laptop browsers: 1280 × 720, 1366 × 657, 1440 × 789, 1536 × 730, 1920 × 955, 2560 × 1305) the line and "µm" end 16 px or more above K05's rim, where the head rises at the line's right end (both height caps less the sentence's height, so 1440 × 900 now sets the numeral at about 155 px rather than 14vw); G03 tolerance graph (one hair line and one sheet line above zero, each labelled with its thickness, never mirrored). ≥ 700 px in landscape the full-bleed scan fades in from Born whole's floor at its top and out at its foot (from 93%, below the racket's foot); phones and portrait windows from 700 px (iPads) show the K05-phone frame, which starts under the numeral's line, the whole racket and its cap below it (700 to 899 px the stage grows past the screen where it must; pinned from 900 px the frame narrows, its sides feathered, to keep the racket whole); the graph section's lift and grid rise out of `--stage` over its first 160 px and fade back to it above Holes | The numeral never counts (a paused count read as the spec): the scrub settles the K05 frame (scale 1.08 → 1) and brings the numeral and its line in together near the start, so they always read as a pair |
| 6 | Holes (pinned 1.4 screens ≥ 900 px; `#holes`; the visual peak, owner 2026-10-28: "Only with this one I feel something") | K04 macro full bleed + G05 fibre flow; eyebrow "Moulded holes"; the body adds that a drilled hole opens the core and that the wrap is "the same patent-pending process", then the owner's line, brighter: no other racket on the market has holes made this way (none drilled, no foam exposed, the carbon wrapped smooth); then the pair (`#holes-pair`, where the Skip link lands), rendered and then drawn (owner, 2026-10-29: "one 2D and one 3D visualization"): first K16, two 8:9 frames of one render in K04's language (one camera, one light, the same white 3K twill at the same scale; left a drilled hole: the tows cut dead at a chipped edge, a band of crazed resin, fibre stubs off the cut, the laminate's cut plies and the core in the wall; right a moulded hole: the twill flowing round a lined lip, the warm bore glow), side by side from 700 px with G06's gap, stacked on phones, each labelled "Drilled" / "Moulded" over a rule (amber for moulded), feathered at its foot; as each frame scrolls through it settles (scale 1.06 to 1) and the light comes up through the moulded hole only (K16-full's right half fades in, 0.25 to 0.75 of the scrub). Then G06 drilled vs moulded, each plate lit like a light table around its dark bore (fill rule); as each plate scrolls through (its top at 85% to its foot at 15% of the screen) a soft comet of light runs left to right along its fibres (owner, 2026-10-29): on the moulded plate it follows the streamlines round the bore and on out the other side, the lines nearest the bore leading, and the bore's lip catches it as it passes; on the drilled plate a dimmer one runs along the same tows and dies at the cut. Stroke dashes only, hidden with reduced motion. The leads are `t-lead`, as in every section. Phones: K04's whole card crop (32:45) at the full width, feathered at both ends, then the words; the stats sit about 80 px above G06 | Pinned: K04 alone first, close on the lit hole (scale 1.22 → 1 over 0.7 of the pin) while the ring of light comes up (0.08 to 0.38), then the shade and the words (from 0.42, staggered), then the screen holds. Below 900 px: the layers settle (scale 1.14 → 1) and the ring comes up as the band scrolls through, the words rise on entry |
| 7 | Sealed core (pinned 1 screen ≥ 900 px; `#sealed-core`) | Right after Holes (owner, 2026-10-23): eyebrow "Sealed core", "The core never touches the air.", a body that picks up from the moulded, lined holes, and three callouts ("Swiss-made EVA", "Injected straight into the mould", "Three times the life of an exposed EVA core"). Pinned: the words in the left columns (vertically centred, `min(48vw, 1240px)`), K03 cut-through covering the stage moved right and smaller (translate 19% 4%, scale 0.92), its frame feathered 24% at both sides and 8% top and foot, with `SealedCoreTrace` (one amber line around the stippled core, both bores lit and lined). Stacked: the words and callouts centred, then K03 (phones: the square window on its card crop; from 700 px the 16:9 crop feathered at both ends, with the trace drawn on it). Its Skip link lands on the sweet spot | Heading and K03 on screen from the first frame (never a blank entry); the scrub settles K03 (scale 1.06 → 1), lists the callouts (from 0.12), draws the trace once (0.24 to 0.54), then holds |
| 8 | Sweet spot (`#sweet-spot`; the payoff, after the sealed core) | K14 (live since 2026-10-28; a raking-light macro of the face running out to the rim, in K04's language; `stills.json` wide, portrait and card, and K14-pace); G15 is the fallback if K14 is missing (it reads on its own). K12 is off the landing (owner, 2026-10-28). G15 ≥ 1000 px: eyebrow "Sweet spot", "Edge to edge.", two lines (line 1 opens on the payoff, "This is what all of that gives you on court.") and the lockup ("Nearly 94%" and 4 mm under one amber hairline) in columns 1 to 5; G15 on the right. K14 ≥ 1000 px: the macro full bleed across the top (16:9 at the screen's width, at most 72svh, feathered at both ends), the head and lines in columns 1 to 6 and the lockup in 7 to 12, level with the lines. Phones: headline, image (K14's 4:5 portrait crop at the full width), lines, lockup. Floor --stage at both ends. Not pinned; the sealed core's Skip link lands here (tabIndex −1). Details under "Sweet spot" | ≥ 1000 px one scrub as the section enters (its top at 85% of the screen to its centre at the centre): G15's light spreads from the sweet spot to the 4 mm line, then the lens; K14 settles (scale 1.08 → 1); the words rise once. Below 1000 px the image fades in (K14 settles) and each block rises on entry |
| 9 | Feel (pinned 0.8 screen ≥ 900 px; `#feel`; after the sweet spot) | G02 vibration graph; eyebrow "Direct feel", "You feel exactly where you met the ball.", the owner's lead "The impact is absorbed by the entire unibody's surface." and three points (the third "The head twists less."). From 900 px wide and 560 px tall the headline, G02 and the three points are one screen below the header, pinned or not (owner, 2026-10-23): the words and points keep their size (the h2 capped at 6.6svh, so 1536 × 730 keeps two lines) and G02 fills the height between them (`VibrationGraph fill`). Phones and tablets stack it. Unibody has just told the cause, so Feel names the joint once (point 1) and never the tube. The points' rules are a translucent white (as Durability's), so they read over the pool's light as well as the floor. Its Skip link lands on Durability | Graph reveal on entry; pinned, the three points rise in the scrub (0.04 to 0.36, staggered), then the screen holds; below 900 px they rise on entry |
| 10 | Durability (`#durability`; after Feel) | G14 lifespan graph (0 to 5 years: most padel rackets 1 to 2, KINETIQ 5). ≥ 1000 px: copy in columns 1–4, G14 in columns 6–12; then four reasons (the sealed core first; four across ≥ 1200 px, two by two from 900 px, on a shared title row and body row so every body starts on one line); the fourth, "Made for regular play.", gives the usage profile (about 160,000 ball strikes) and the promised fatigue tests in its own sentence. No fine print: the only section that says five years | G14 draws on entry: window, typical lane, KINETIQ trace behind a glow head, then the five-year numeral |
| 11 | Identical (CTA 2) | K07 five rackets, Command and Pace alternating (the re-render, owner 2026-10-23); "within 1.0 g ... to within 0.1 mm", the stats ±1.0 g and ±0.1 mm; G04 spikes, G08 card; "Every KINETIQ is made to the same weight and balance."; Reserve Now with the hero's price line. From 700 px K07 spans the width at its own 16:9, anchored to the section's foot, and the section is the words plus two thirds of K07's height, so the words always end a third of the way down it, over the dim tops of the light shafts and clear of the racket heads (every pixel under the lead 4.5:1 or more against `--steel`); above it the floor is K07's own top colour. Phones: the words over a lift, then K07's trio crop; Reserve Now at the full measure, like the hero's and the finale's. From 700 to 899 px the card is about 460 px wide and centred, so it and its Reserve Now share one screen. Only the price line under the card rises in: the Reserve Now never fades, so whenever the header's compact one hides for it, it is on screen | Rise on entry |
| 12 | Choose your feel (`#feels`) | K08 pair (Command white 3K left, Pace black 12K right; the frame rises out of the floor at its top, over at most 64 px from 700 px and 20 px on phones, clear of the crowns, and fades at its foot), each feel's name and "Built for control" / "Built for power" (steel, lead size) directly under its racket's cap and shown with the photo, so the pair is never two unnamed rackets; then the compare, one column per feel: one character line (what we made, then what it does for you), and four ruled rows, label left and value right at 18 px and up (Feel, Face, Core, Suits; the Face row is a spec, the colour and the weave, never a repeat of the line). The two lines are kept the same length and set in the ruled rows' box, left-aligned on the labels' edge, so they wrap alike and the two columns read as one grid. From 700 px the columns share their rows through CSS subgrid, so every row sits level with its counterpart; phones stack Command, then Pace. Then the closing line across both columns under a full-width hairline: only the core and the face differ | Rise on entry |
| 13 | Specifications (`#specifications`) | Eyebrow "Specifications" and "As large as the rules allow." beside the lead from 900 px; six cells ruled like a spec sheet, every figure to one decimal (owner, 2026-10-22: 455.0 mm, 260.0 mm, 38.0 mm, 355.0 g, 250.0 mm, then 42 holes moulded; G01 and the Two feels closing line use the same precision; 3 × 2 from 900 px, 2 × 3 on phones); then G01 whole (full sheet ≥ 1240 px, front view below), on two lifts. G01 draws the canonical racket: Ø14.0 ×8 and Ø12.4 ×34, the 4 mm line where the flat face ends, the head flowing into the handle, the overgrip's helical wrap and the black cap engraved Q, the logo (named in callouts on the full sheet); Section A-A cuts below the hole field, B-B through the top row | Cells rise on entry; the drawing draws on |
| 14 | Editions (`#editions`) | The h2 "We make one racket, in three editions." (each clause kept whole) and its lead (`editionsIntro`), then three cards (K11-single, one white Command racket shot with K11's camera and light / K11 Command pair / K09; below 900 px the frames are square (from 600 to 899 px each card is 62% of the track, so the next one peeks in), KINETIQ's racket and the First 500 pair shown whole with air above and below and their sides feathered, and the price sits right under the name, so a card's image and price share a screen and the spare height falls at the card's foot), every card with its includes (KINETIQ's four follow First 500's order, racket, number, card, shipping) and one price foot line. From 900 px the three cards share six rows through subgrid (image, name, card line, includes, One of Ten's invitation note, price foot), so the includes start on one line and the feet stay level; from 900 to 1279 px the status sits above the name, as on phones, so the head fits its card. The availability tags are all in the amber family (First Edition and Limited amber, Invite Only amber-hot), so none reads as a control. KINETIQ and First 500 are whole-card links to /reserve?tier= with the arrow; One of Ten is not a link (no hover, no arrow): "By invitation" in its foot while invitations are open, and a quiet "Have an invitation?" link to /reserve?invite ("Invitations open soon." while invitations are closed). Nothing under the cards: no markers and no fine print (owner, 2026-10-22). The intro's light spills about 100 to 130 px up into the section above on purpose (Specifications since 2026-10-28, whose drawing ends above it), so the two sections meet without a hard line | Rise on entry |
| 15 | Finale | K01 in its beam over the horizon, one screen with the footer: ≥ 1000 px the hero mirrored (racket left, words in the right 7 columns as the hero's sit in the left 7; the line a step under the h2 size at a 24ch measure, four lines, each a whole phrase, with no-break spaces in `copy.ts`; the frame fades in from Editions' floor at its top and out into the section's last colour above the footer, clear of the cap's foot, so the beam never meets the footer on a line); phones: racket, then words, the line a step under the h2 size so it sets in four whole phrases too, and a header-high band above the frame that ramps from Editions' floor to the 4:5 frame's top row; phones 740 px tall or less show the wide crop (the whole racket and its horizon centred, exactly one screen with the footer) on a flat band, the frame rising out of it over 32 px, since that crop's top row is darker left than right; taller phones the 4:5 card crop. Line: "Each KINETIQ is moulded in Switzerland as one carbon shell, to within 15 microns." (Born whole, Unibody and Precision in one whole sentence, answering the hero's "moulded to 15 microns"; never the five years or "the feel you choose", which Two feels and Editions say); under it, the hero's price line | Rise on entry |
| /reserve | Sticky gallery with per-edition slides and gallery controls. KINETIQ opens on K01, shows K12 second for Command once it is exported (K12-base only, its lit pass shown nowhere, so at the payment the racket looks as the feel picker says), then K02, K04 and K08's Command racket, and ends on the racket's own measurement card (serial KQ-000427, in the chosen feel); in Pace it opens on K08's Pace racket and its card is KQ-000428's, the racket K08 shows. First 500 opens on K11, the set in the chosen feel with 027/500 on both throats, then K10 (Command only: its throat is white twill) and the two matching sample cards: B sits behind A with only its header and set number showing (below 1024 px its set number alone, so the pair fits the frame whole, A at the single card's width in a tighter rhythm, its text at 16 px; in a frame under 468 px tall B shows only its edge behind A and the text shrinks to fit, never under 15 px; the single card on phones is A's size, 300 px wide), never the text-free thumb and never cut off by the frame. The gallery stacks above the options below 1024 px and in any portrait window (`(max-aspect-ratio: 4/5)`, the 12.9-inch iPad Pro at 1024 × 1366 or 1024 × 1292; side by side only from 1024 px and wider than 4:5, range syntax, the exact complement, as in the Hero). Stacked, the frame is 4:5 where the screen is tall enough and shorter, down to square, where it is not, so the first view holds the frame and its arrows, dots and counter (56 px) above the Due Today bar and its fade (390 × 664, 375 × 667 and 768 × 1024 alike); the slides use their 4:5 phone crops wherever it stacks (`phoneMedia`), K02 edge-on contained with its sides feathered, K07's square trio crop shown whole across the frame's width with its top and foot feathered, and every other subject kept whole by its position. K12 shows its 4:5 portrait crop at every size, contained and centred on a flat slide in the render's own edge tone (no lift behind it), its edges feathered; on wide screens its frame ends 16 px above the floating controls, so the engraved cap clears them. One of Ten opens on K09, then G12. The gallery follows the slide on show, not its position: a change of feel keeps the measurement card or the feel's racket in view (to compare), and otherwise moves to the chosen feel's racket; a new edition starts on its first slide. Beside the gallery, the options column, headed "Reserve your KINETIQ" (the cards name the editions, so the base edition's name, the brand's, is not repeated in the chrome: each card's includes sit under "Included"); the sticky bar reads the racket count ("One racket", "Two rackets") over Due Today. Before the edition streams in, a neutral shell shows (lit stage, empty column: no edition, price or count), so a ?tier= link never paints another edition first. The column fades under the header and above the sticky Due Today bar instead of being sliced | Tier cards (G11 glyphs: one racket, two, three; One of Ten shown whole but locked, with no hover, press, focus or selection until an invitation code unlocks it), the feel picker (Command and Pace stacked, two across once each can be 320 px wide; each shows name and sub, the spec in Saira and one line, with the helper line under them), trust list (the two badges stack full width while the column is narrower than 700 px, a container query, and share one row at 2560), Due Today, the order line (it breaks only between the order and "Due today", never inside either), Pay with Card → form in place (the edition locks while it is open, the feel only while a payment is processing; Postal code and City share a row once the options column is 410 px wide, a container query, so tablets pair them and phones stack them) | Crossfades; fields rise 8 px |

Stills are exported by `scripts/stills.mjs` from 16-bit Blender masters (not committed) to AVIF + WebP with
phone crops (`src/content/stills.json`), and rendered with `<Still>` (`src/components/media/Still.tsx`). K12 (the
sweet spot) has two passes that register pixel for pixel, `K12-base` and `K12-full`, each with a `wide` and a
`portrait` crop (the 4:5 window, x 0.435 to 0.885 of the master); since 2026-10-28 only K12-base is shown, on /reserve.
`<Still phoneMedia>` moves the phone crop's breakpoint where a slot stays 4:5 or portrait above 699 px: the hero's
portrait layouts, the /reserve gallery wherever it stacks (below 1024 px, or portrait), and the finale only on phones taller than 740 px.
Graphics live in `src/components/graphics/` with review pages at `/lab/<id>` (dev only); G15 is the sweet spot
(`SweetSpotField`, `/lab/g15`), G16 the carbon cross-sections (`CarbonLayup`, `/lab/g16` only since 2026-10-29).

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
  tabular, each item read as a sentence. No caption (owner, 2026-10-23: no "Illustrative" captions). No comparison in
  the copy or the drawing. The words rise on opacity only (never visibility), so the claim stays in the accessibility
  tree.
- **The numbers come from the geometry,** never typed by hand: `graphics-sweetspot.ts` takes the face above the
  bridge (y ≥ −86.5 mm, 531.5 cm²) and insets it 4 mm from the outline and 4 mm above the throat (498.7 cm², 93.8%),
  and `SWEET_CLAIM` rounds it as Apple rounds a display: down to the whole number, or up only with "Nearly" (Apple
  Watch Series 7: "nearly 20 percent"; a 5.85-inch iPhone X display was sold as 5.8-inch). The section, G15's text
  alternative and K14's alt are built from it; /lab/g15 checks it against the geometry. If `racket-shape.ts`
  changes, the lockup and the alt text change with it.
- **The image (owner, 2026-10-28):** the upright K12 racket is off the landing ("I dont like the edge to edge hero";
  /reserve keeps K12-base). K14 (live) is a K04-style macro of the face running out to the rim: close, in
  raking light, the weave resolving, the flat face meeting the 1.5 mm edge radius (`stills.json`: wide, a 4:5 portrait
  crop x 0.385 to 0.835, and K04's card crop; K14-pace the same). If K14 is ever missing, the section shows G15, the
  drawing, and reads complete.
- **G15** is the fallback if K14 is missing: the canonical silhouette face-on in white 3K
  twill (an SVG pattern: the warp a step darker than the weft, rounded tows, fine crevices) in a low studio light, the
  field lit warm white and even to the 4 mm line with the weave reading through it (luma about 214 with the twill
  spanning about 30 levels at 1×), an amber hairline on the line, the holes open with each bore's lit wall and lip on
  the lower right, the overgrip's wrap and the Q on the cap, a steel rim hairline, one clear-coat gloss line, and a 6×
  lens on the edge with the dimension "4 mm" (HTML, 15 px and up). The lens is drawn at its own scale, never the
  racket scaled up (`lensDetail` in `graphics-sweetspot.ts`): the flat band in the racket's carbon tone at that spot,
  the 1.5 mm edge radius as a highlight, the lit field with a fine hatch to its amber line, the page's own graphite
  beyond the edge; the dimension's arrows end on the 4 mm line and the outline, with short extension ticks. Variants: "wide", "portrait" (phones; the lens
  beside the handle) and "auto" (portrait below 700 px). No ember, no tube line.
- **Layout:** G15 ≥ 1000 px: the words in columns 1 to 5, centred in one screen, and the drawing in columns 6 to 12.
  K14 ≥ 1000 px: the macro full bleed across the top (16:9, at most 72svh, feathered at both ends), the head and lines
  in columns 1 to 6 and the lockup in 7 to 12. Below 1000 px: headline, image, lines, lockup (K14 at the full width on
  phones). The floor is --stage at both ends, the sealed core's above and Feel's below (checked with a pixel probe),
  with a lift behind the image (fill rule).
- **Motion:** G15: the light never scales: a soft mask disc grows from the sweet spot (about 25 mm above the head
  centre) and reveals a field that is already whole. K14 settles (scale 1.08 → 1; scrubbed on wide screens, 1.6 s on
  phones). Reduced motion and the server render show the final state: every word visible.

## Feel toggle (owner, 2026-10-23; made minimal 2026-10-28)
The owner, on his iPhone: "the page feels very busy. Make the toggle more minimal?" and "There is no toggle while
scrolling down on iphone?" (`FeelToggle`, `components/chrome/`; its group name "Feel" and the labels come from
`site.ts`, so HeaderClient stays free of copy). Two small face swatches, white 3K and black 12K (14 px), each with its
name in Saira at 15 px and up; the chosen swatch is ringed in `--text` (a 1 px ring 4 px clear of it, fading and
settling in 200 ms ease-out) and its name `--text`, the other `--muted`. No pill, no thumb, no fill, so it never
competes with Reserve Now. Every option is at least 44 px square to the touch through its padding; options press to
0.97; hover only on fine pointers. A native radio group (`role="radiogroup"`, arrow keys, Tab lands on the checked
option, the focus ring on the option). The site opens on Command.
- Hero: beside Reserve Now from 700 px; on phones above the full-width Reserve Now, under the racket like a caption.
- Header: beside the compact Reserve Now, shown and hidden with it, at every width. On phones (below 700 px) the two
  swatches alone, 44 px each (their names stay the radios' labels, visually hidden): the wordmark (about 130 px), the
  swatches (88 px) and the compact Reserve Now fit 335 px at 375 px; from 700 px the swatches carry their names.
- State: `lib/feel-store.ts` (`useFeel`, `setFeel`, useSyncExternalStore) writes `kq-feel` in localStorage (try/catch;
  in memory when blocked) and `html[data-feel]`, which the head script sets before the first paint; every toggle's
  thumb and labels read that attribute, so all of them agree and a stored Pace never flashes Command. Reserve Now
  links (hero, header, Identical, finale, the edition cards) carry the choice into checkout (`?feel=`, `ReserveLink`);
  the /reserve feel picker writes the same preference, and its gallery shows a still's Pace version in its own feel.
- Stills: a still's Pace version is its id plus "-pace" with the same crops (`K01-full-pace`, `K01-hero-full-phone-pace`,
  `K02-pace`, `K05-pace`, `K05-phone-pace`, `K06-base-pace` so far, `stills.json`). Where one is exported, `<Still>`
  follows the feel (`FeelPicture`): one <picture> holding one version at a time (never both downloading), the server
  painting Command; after hydration a stored Pace replaces it, hidden from the first paint by html[data-feel], and a
  change fades the image out (150 ms) and the other version in once loaded (240 ms ease-out, opacity only; reduced
  motion: instant). The box keeps its size, so nothing shifts. A crop without a Pace export keeps its Command file
  silently. Stills that name a feel keep their own logic (K08's pair, K11-command / -pace, K07 alternating, K12 and the
  measurement cards). Known cost: a Pace visitor's browser may fetch an eager still's Command file once before
  hydration (the hero's lit pass, low priority); lazy stills load only their Pace file.

## Micro-interactions
Pressables scale 0.97 on `:active`; hover only behind `(hover: hover) and (pointer: fine)`; transform and
opacity only, 150–300 ms ease-out (`--ease-out`); exits faster than entries.
Skip links on the pinned chapters (Unibody, Precision, Holes, Sealed core, Feel) appear only on keyboard focus: visually hidden otherwise (still
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
    Dev only: `/__nextjs_*` (the error overlay) passes. With the cookie, pages get `Cache-Control: private, no-cache`
    (no shared cache keeps the presentation; not no-store, so the back button's page cache works); assets and APIs
    keep their own headers. Gate responses are `private, no-store`.
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
