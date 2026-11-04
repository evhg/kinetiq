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
- "One piece" is retired (owner, 2026-10-22), except in the owner's hero sentence: the construction word is
  "unibody", with "no joint" scoped to the frame ("The bridge is moulded in, not joined on.", "No joint
  to work loose."). "Zero seams" is retired too (owner, 2026-11-02: demoulding leaves a parting line, even where it
  sits level with a face and cannot be seen): never "seamless", "no seam" or "zero seams". Never "zero
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
Font swap (2026-11-01): until Archivo and Saira arrive (`display: swap`), text paints in metric-matched local fallbacks
(`src/app/font-fallbacks.css`, written by `scripts/font-fallbacks.mjs`): Arial, Liberation Sans or Arimo, then Roboto on
Android, one family per Archivo width and a face per weight range, each size-adjusted to the site's own words, so the
swap re-wraps nothing (CLS from fonts ~0). A rule that sets `font-variation-settings: "wdth" N` uses
`font-family: var(--font-display-N)` (108, 110, 112, 125); a new width needs its family in the script first.
The stacks name only the web font's own family (`--font-archivo-face`, `--font-saira-face`, set on <html> in
`layout.tsx`), never `var(--font-archivo)`: under Turbopack next/font ignores `adjustFontFallback: false`, and its
"Archivo Fallback" (local Arial, sized for wdth 100 at weight 400) would paint before the KQ faces wherever Arial is
installed (iOS, macOS, Windows).

## Page
A climactic rise (owner, 2026-10-28: "Re-plan the storytelling and introducing the features and claims to create a
climactic rise"): make, peak, payoff, buy. Order: 1 Hero, 2 The first Unibody, 3 Space-grade carbon, 4 Born whole,
5 Precision, 6 Moulded holes (the visual peak), 7 Sealed core, 8 Edge to edge (the sweet spot, the payoff: "This is
what all of that gives you on court."), 9 Surface (the face's grip on a slice, owner 2026-11-02), 10 Direct feel,
11 Built to last five years, 12 Identical, 13 Two feels, 14 Specifications, 15 Editions, 16 Finale. How it is made rises from what it is (the unibody) through what it is made
of, the one mould and 15 microns to the moulded holes, the image the owner feels (K04, the render language for every
new still: close, raking light, the weave), and what they keep closed; the payoff tells what that gives the player;
then the buy. Every chapter opens on an amber eyebrow except the Precision record, whose sentence leads into the
numeral. Skip links, in order: Unibody → Space-grade carbon, Precision → its graph, Holes → drilled vs moulded,
Sealed core → Sweet spot, Sweet spot → Surface (pinned since 2026-11-03), Feel → Durability (Surface is not pinned, so it has none: nothing to skip). Seams: the
hero's floor ends on Unibody's rgb(19 20 22); the sweet spot and Surface run --stage to --stage, between the sealed
core and Feel.

| # | Section | Media | Motion (reduced motion: final state, no pin) |
| --- | --- | --- | --- |
| 1 | Hero | K01 base → beam crossfade. ≥ 1000 px and 4:5 or wider (the split layout): words (h1 and the owner's lead, nothing after it), Reserve Now with the feel toggle and, after a short hairline, the grip toggle beside it ("Grip toggle" below; one row from 700 px; on phones the toggle, two small swatches with their names, sits under the racket like a caption, above the full-width Reserve Now, and the racket scales to 0.88 about its crown, 0.75 on phones 740 px tall or less, 0.68 at 650 px or less, so its foot clears the toggle; "Feel toggle" below) and the price line ("From €410, fully refundable, and shipping in January 2027.") in the left 7 columns, the still moved right 21vw (racket about 54% of the screen tall); the floor fades into the Unibody chapter's first colour, rgb(19 20 22), over the scroll veil (phones too), so the beam never ends on a hard line. Phones: words, racket, Reserve Now on the floor, and the lead always shows (phones 740 px tall or less, which is Safari on most iPhones, set the words a step smaller and the racket smaller, its frame feathered at the sides and top; the price line wraps, balanced). Portrait tablets (700 to 999 px and portrait, or any window narrower than 4:5, such as an iPad Pro) take the phone layout with the phone master, drawn from the band between the words and Reserve Now (a size container), so the crown clears the lead and the foot clears the button at any portrait size | Load reveal; scroll drift and veil (the button stays opaque); the swivel (owner, 2026-10-23): as the hero scrolls away the lit racket turns about its handle, 0° to 35° in both feels and both grips (36 Blender frames, `scripts/sequence.mjs`, per feel and per layout: `K01-swivel-<feel>-desktop|phone`, Naked `K01-swivel-nogrip-<feel>-desktop|phone`; since 2026-11-04 in the light-sweep scene, a soft band crossing the head as it turns, rendered at 5120 x 2880 and 2160 x 3840, so a 5K screen, an iPad in portrait at 2x and an iPhone at 3x draw them without upscaling, the canvas cross-fading between neighbouring frames so the turn never steps; Pace's face cards turn with the racket by 0.85 of its angle, so the black face stays lit to 35°), finished by 26% of the hero scrolled in the split layout and by 30% in the portrait one (phones, portrait tablets; owner, 2026-10-28: at 60% the turn ran on after the racket had slid under the header; the layout is chosen by the same PORTRAIT query as the CSS, through one gsap.matchMedia conditions object, never range syntax, which older iOS cannot parse); `media/Swivel.tsx` (shared with Unibody's K02 swivel) draws only the rectangle that changes onto a canvas laid over the lit still with its own object-fit and position (frame 0 is the still, so the canvas shows from frame 1 and the handover is invisible), loads the frames from the load event, the first scroll or touch, or 1.5 s after mount, whichever comes first (Safari's load event, and in-app browsers', can come seconds late; Safari has no requestIdleCallback), coarse first, and starts once no gap is wider than 4; each frame decodes through createImageBitmap, else an <img>, a failed frame is retried once and its neighbours stand in; without a sequence for the feel or layout, with Save-Data, a quarter of the frames lost or reduced motion (iOS: Reduce Motion), it shows the still exactly as before; in the split layout the racket fades out between 10% and 32% of the hero scrolled, so Unibody's K02 arrives on a dark stage |
| 2 | Unibody (pinned 1.6 screens ≥ 900 px; `#unibody`) | Beat A: K02 edge-on, eyebrow "The first Unibody", "When you hold it, there is no boundary between the material and your experience." (two lines pinned; its body opens "We no longer need the frame tube.": the cause is told here, once; the owner's words, 2026-10-23), three callouts placed under the parts they name (handle, bridge, rim; a three-column row in the same proportions when stacked ≥ 900 px; a list on phones, rim first). ≥ 900 px the rim's callout is right-aligned and balanced, so its amber dash is inline and leads its first line (never left at the box's edge when the words wrap short of it), pinned and stacked alike. Pinned, the eyebrow, headline, lead, K02 and the callouts are one block centred in the stage below the header (K02 hangs from its racket band and feathers into the graphite above and below it; in a portrait window, the 12.9-inch iPad Pro, K02 is sized by the width instead of covering the stage, so the whole racket spans the screen inside the margins and its swivel draws at 0.95x rather than 1.9x, 2026-11-01); stacked ≥ 700 px the words come first, then K02 and the callouts; phones open on the eyebrow and headline, then K02 upright (its top and bottom feathered), then the lead and the callouts. Its first colour is the hero floor's last, rgb(19 20 22) (since 2026-10-28 it follows the hero). Beat B: K03b tubular → K03 cut-through + G07 sections ("Open core" / "Sealed core"), "The shell is the frame."; stacked ≥ 700 px beat B opens on its words too, then K03, then the two sections; phones show K03 in a square window on its 4:5 card crop, the slab whole and the frame feathered at both ends. Beat B ends the chapter: the sealed core, once its last beat, is its own chapter after Holes (7b). Beat C (the three proofs) is retired; the Skip link lands on Space-grade carbon | Light line sweep (0.02 to 0.24 of the timeline) along the racket's top edge, on the overgrip from the cap and on the shell along the head, then the callouts handle → rim (from 0.12, 0.02 apart), then (Release 4, 2026-10-28) the words, the callouts and the light line step aside (0.40; the turned face would rise behind the headline on short windows) and the racket turns about its handle until its face shows (0.42 to 0.60, K02's swivel: `K02-swivel-<feel>-desktop|phone`, 60 Blender frames for Command and 45 for Pace at 2560 x 1440 (2026-10-29; phones and portrait tablets under 900 px take the frames turned upright, Command's as 45 of the 60 since 2026-11-01, like Pace's, played at the render's own timing through the kept frames' source positions in the manifest), 0° to 35°, Command and Pace, `scripts/sequence.mjs`, drawn by the shared `media/Swivel.tsx` over the still, frame 0 being K02 itself) alone, and beat A leaves at 0.62; without a sequence the beat holds whole. Phones: the upright racket turns as it crosses the screen (its centre from 85% to 30% of the screen); the stacked 700 to 899 px layout crops K02 to its 18:5 band and keeps the still; reduced motion: the still only; beat crossfades (beat A leaves before beat B arrives), the tubular cut dissolving into the shell, then beat B holds. K03 feathers into the stage at both ends when stacked; pinned, its frame feathers 24% at both sides, so its right edge never stands as a wall |
| 3 | Space-grade carbon (`#space-grade`; owner, 2026-10-23) | Right after Unibody (2026-10-28): the material, then the mould. Eyebrow "Space-grade carbon", "We build it from the carbon made for space.", a lead in two whole sentences (the fibre and resin grades of space hardware and its engineering standards, written for extreme mechanical, thermal and environmental conditions; then, against "the standard carbon most padel rackets use", what that does for the player), then three points (strength without extra weight, solid through every layer, steady in heat and cold; three across from 900 px on a subgrid, as Durability's; point 2 quotes the void content from `specs.ts`), then, under each point, three figures (owner, 2026-11-02: "convey we can back up our claims with numbers"; 2026-11-03: "the Carbon specs is too much, doesn't need its own section, I'd add some of these numbers below each of the relevant sub section"): strength, fibre tensile strength and modulus and laminate flexural strength; solid, void content, interlaminar shear strength and fibre volume; heat and cold, glass transition, service range and moisture absorption. Each is the number in the stat face (`clamp(2.5rem, 2.2vw + 1.25rem, 5rem)`, a bound "≥"/"≤" muted and a step down, the unit in `t-unit`), its term (`t-label`, steel), then its test method and any condition (`t-fine`, muted), the first under a short amber rule; from 900 px the figures are rows of the points' subgrid, so each sits level with its counterparts; 700 to 899 px a point's three figures stand side by side; phones stack them. Every figure comes from `src/content/specs.ts`, provisional until the factory's values (a launch build fails while any is). Never a country, a maker, the factory, or defence or military wording (CLAIMS.md rows 41 to 44). Media (owner, 2026-10-29: "the morse code looking graphics under space grade carbon look out of place, rather show a piece of great looking carbon in a space setting"): K15 full bleed above the words (`K15-base` and `K15-full`, two passes of one render, and their `-pace` versions; wide, card and portrait crops), 16:9 at the screen's width (at most 86svh), the 4:5 card crop on phones, feathered at both ends: the canonical racket's crown (white 3K twill, black 12K in Pace) from 30 degrees above the face, its rim a rising arc, three crown holes on the face, floating over the limb of a dark planet with a thin warm atmosphere (amber on the sunward side, pale graphite away from it) and a few faint stars; no spacecraft, satellites, flags, logos, maker or country, and nothing military. The words below it: eyebrow and h2 in columns 1 to 6, the lead in 7 to 12 from 1000 px (stacked below), then the three points. K13 and G16 are off the landing (G16 lives on in `/lab/g16`; K13 stays exported). Its floor is `--stage` at both ends, after Unibody's graphite and before Born whole's head | The sun comes up: one scrub as the section enters (its top at 92% to 12% of the screen) brings the lit pass (K15-full) in over the base, from 0.15 to 0.85 of the scrub, while the frame settles (scale 1.06 → 1); the words and the points rise on entry. Reduced motion and the server render: the lit pass at rest |
| 4 | Born whole | K06 mould, Swiss lockup; no badge under it (the body names the patent-pending process), a band of floor before Precision | Scrubbed push-in, cavity glow |
| 5 | Precision (pinned ≥ 900 px) | K05 scan; one sentence that the numeral ends (owner, 2026-10-23): "Every racket is moulded with ultra-precision, exact to within" over the record "15 µm" (the h2, spoken "... exact to within 15 microns."; one line from 700 px, two on phones; its height, `--intro-h`, is taken from the numeral's height caps and the portrait frames' tops), with its line ("About a fifth of a human hair.") directly under the numeral at every width; ≥ 700 px in landscape the numeral is capped by the height as well as the width (`min(14vw, 39svh − 130px, 54.5svh − 8.75vw − 140px)`, 5.5rem to 22.5rem), so on windows shorter than 16:10 (laptop browsers: 1280 × 720, 1366 × 657, 1440 × 789, 1536 × 730, 1920 × 955, 2560 × 1305) the line and "µm" end 16 px or more above K05's rim, where the head rises at the line's right end (both height caps less the sentence's height, so 1440 × 900 now sets the numeral at about 155 px rather than 14vw); G03 tolerance graph (one hair line and one sheet line above zero, each labelled with its thickness, never mirrored). ≥ 700 px in landscape the full-bleed scan fades in from Born whole's floor at its top and out at its foot (from 93%, below the racket's foot); phones and portrait windows from 700 px (iPads) show the K05-phone frame, which starts under the numeral's line, the whole racket and its cap below it (700 to 899 px the stage grows past the screen where it must; pinned from 900 px the frame narrows, its sides feathered, to keep the racket whole); the graph section's lift and grid rise out of `--stage` over its first 160 px and fade back to it above Holes | The numeral never counts (a paused count read as the spec): the scrub settles the K05 frame (scale 1.08 → 1) and brings the numeral and its line in together near the start, so they always read as a pair |
| 6 | Holes (pinned 1.4 screens ≥ 900 px; `#holes`; the visual peak, owner 2026-10-28: "Only with this one I feel something") | K04 macro full bleed + G05 fibre flow; eyebrow "Moulded holes"; the body adds that a drilled hole opens the core and that the wrap is "the same patent-pending process", then the owner's line, brighter: no other racket on the market has holes made this way (none drilled, no foam exposed, the carbon wrapped smooth); then the pair (`#holes-pair`, where the Skip link lands), rendered and then drawn (owner, 2026-10-29: "one 2D and one 3D visualization"): first K16, two 8:9 frames of one render in K04's language (one camera, one light, the same white 3K twill at the same scale; left a drilled hole: the tows cut dead at a chipped edge, a band of crazed resin, fibre stubs off the cut, the laminate's cut plies and the core in the wall; right a moulded hole: the twill flowing round a lined lip, the warm bore glow), side by side from 700 px with G06's gap, stacked on phones, each labelled "Drilled" / "Moulded" over a rule (amber for moulded), feathered at its foot; as each frame scrolls through it settles (scale 1.06 to 1) and the light comes up through the moulded hole only (K16-full's right half fades in, 0.25 to 0.75 of the scrub). Then G06 drilled vs moulded, each plate lit like a light table around its dark bore (fill rule); as each plate scrolls through (its top at 85% to its foot at 15% of the screen) a soft comet of light runs left to right along its fibres (owner, 2026-10-29): on the moulded plate it follows the streamlines round the bore and on out the other side, the lines nearest the bore leading, and the bore's lip catches it as it passes; on the drilled plate a dimmer one runs along the same tows and dies at the cut. Stroke dashes only, hidden with reduced motion. The leads are `t-lead`, as in every section. Phones: K04's whole card crop (32:45) at the full width, feathered at both ends, then the words; the stats sit about 80 px above G06 | Pinned: K04 alone first, close on the lit hole (scale 1.22 → 1 over 0.7 of the pin) while the ring of light comes up (0.08 to 0.38), then the shade and the words (from 0.42, staggered), then the screen holds. Below 900 px: the layers settle (scale 1.14 → 1) and the ring comes up as the band scrolls through, the words rise on entry |
| 7 | Sealed core (pinned 1 screen ≥ 900 px; `#sealed-core`) | Right after Holes (owner, 2026-10-23): eyebrow "Sealed core", "The core never touches the air.", a body that picks up from the moulded, lined holes, and three callouts ("Swiss-made EVA", "Injected straight into the mould", "Three times the life of an exposed EVA core"). Pinned: the words in the left columns (vertically centred, `min(48vw, 1240px)`), K03 cut-through covering the stage moved right and smaller (translate 19% 4%, scale 0.92), its frame feathered 24% at both sides and 8% top and foot, with `SealedCoreTrace` (one amber line around the stippled core, both bores lit and lined). Stacked: the words and callouts centred, then K03 (phones: the square window on its card crop, the trace drawn through the same window; from 700 px the 16:9 crop feathered at both ends, with the trace drawn on it). Registration (owner, 2026-11-03: "the yellow outline doesn't follow the graphic, like its placed at the wrong angle"): the trace is drawn in the crop's own pixel space and fitted exactly as the image (cover; `node scripts/probe-overlay.mjs` maps image points through the img and through the SVG at 390, 768, 1440 and 2560, both feels: 0.001 px apart). The line the owner saw at the wrong angle is the render's own: K03 is the full pass of its render, with a baked amber hairline along the shell's shoulder (lg_shell, Unibody's light line), which beside the trace read as a misplaced outline; the chapter shows `K03-base` (the same render without lg_shell, K03's crops) once it is exported, and K03 until then. Its Skip link lands on the sweet spot | Heading and K03 on screen from the first frame (never a blank entry); the scrub settles K03 (scale 1.06 → 1), lists the callouts (from 0.12), draws the trace once (0.24 to 0.54), then holds |
| 8 | Sweet spot (`#sweet-spot`; the payoff, after the sealed core; pinned 1.4 screens ≥ 900 px since 2026-11-03, owner: "When scrolling down sweet spot section the page doesn't pause and there is no animation?") | K14 (a raking-light macro of the face running out to the rim, in K04's language; `stills.json` wide, portrait and card, and K14-pace) with `SweetSpotEdge`, the 1 mm line traced from the render; G15 is the fallback if K14 is missing (it reads on its own). Pinned (≥ 900 px, motion): one screen, K14 covering the stage moved right and down (translate 28% 14%) so the rim arcs across its right half, feathered at the left and the foot; eyebrow "Sweet spot", "Edge to edge.", the two lines and the lockup ("Nearly 99%" and 1 mm under one amber hairline) in columns 1 to 5 on the dark studio, every size capped by the height (1536 × 730 holds it all); a portrait window (the iPad Pro) sets the words across the top and K14 in the lower part. Stacked (below 900 px, and reduced motion at any width): phones the headline, K14's 4:5 portrait crop at the full width (560 px from 700 px), the lines, the lockup; from 900 px the macro full bleed across the top (16:9, at most 72svh), the head and lines in columns 1 to 6 and the lockup in 7 to 12. Floor --stage at both ends. Its Skip link lands on Surface; the sealed core's lands here. Details under "Sweet spot" | Pinned: the heading on screen from the first frame; the face comes up out of the dark (a void veil 0.62 → 0 over 0 to 0.3) as the frame settles (scale 1.1 → 1 over 0.5); a soft warm band of light, parallel to the rim, sweeps across the weave from the sweet spot out past the edge (0.1 to 0.56; transform only, colour dodge so it lights only the lit carbon); the amber 1 mm line draws along the rim from the lit side (0.34 to 0.6); the lines rise at 0.16, "Nearly 99%" at 0.46 and "1 mm" at 0.6; then the screen holds. Below 900 px the image settles (1.08 → 1, 1.6 s) and its line draws as it enters, each block rises. Reduced motion and the server render: the final state (the line drawn, no light band, every word visible) |
| 9 | Surface (`#surface`; owner, 2026-11-02: "unique surface roughness"; after the sweet spot, before Feel) | Eyebrow "Surface", "A face that grips the ball.", the lead (the same patent-pending process that forms the holes moulds a fine texture into the face, many times rougher than a smooth or painted face; on a slice, a drop shot or a bandeja the face brushes across the ball, grips the felt instead of letting it slide, and sends it away with more spin), the player's line brighter (a slice that stays low and kicks away is a shot most players only see the professionals play; "designed to help you play it"), one quieter line (the texture is part of the carbon, not grit glued on), then the lockup under one amber hairline, as the sweet spot's: "0.65" friction between the face and a padel ball and "16 µm" average roughness (both `specs.ts` `surfaceSpecs`, provisional). K17 (the roughness macro: a padel ball on the face, the moulded micro-dome field around it; K17-full and -pace) ≥ 1000 px full bleed across the top (16:9, at most 72svh, feathered at both ends), the head and words in columns 1 to 6 and, in 7 to 12 from the top of the head, G18 (`GripContact`, `/lab/g18`, review 2026-11-02: how the ball gets its slice, which K17 alone does not show) above the lockup; below 1000 px its `phone` crop (4:5, x 0.06 to 0.51 of the master: the textured face, a crown hole, the ball's edge on the face and the throat; the old `portrait` and `card` crops, nearly all felt, were removed on 2026-11-02), at the full width on phones and 560 px from 700 px; below 1000 px G18 and the lockup follow the words. G18: a magnified side section at the contact, no text in the drawing: the face in graphite with its micro-domes along the top, the ball pressed flat on them with steel felt fuzz, the felt in the patch dragged along the face's travel (amber-hot), a straight amber arrow under the face (its travel) and a curved one round the ball (the spin it gives); an HTML legend of three lines with matching glyphs (15 px and up): "The face sweeps across the back of the ball.", "Its moulded texture grips the felt instead of letting it slide.", "So the ball leaves with more spin.". Then the h3 "The same slice, after the bounce." and G17 (`SliceBounce`, `/lab/g17`): one sliced shot seen from above the side of the court (a small 3D scene projected in `graphics-slice.ts`: the receiving half, net, service and centre lines, the back and side glass as hairlines), the flight in (--text) crossing the net and landing past the service line, then the two exits: off a standard face (--steel) the ball rises to about 1.0 m and runs on 8 degrees off its line; off KINETIQ (amber, with a soft glow) it stays under about 0.3 m and kicks 36 degrees to the side. Floor shadows under every path show the turn on the court. HTML labels (15 px and up): "Bounce", "Standard face / Sits up and runs on", "KINETIQ / Stays low and kicks away". A wide framing (1600 × 760) from 700 px across all twelve columns; a portrait one (800 × 660, pulled back on 2026-11-02 so the net, the flight over it and the back glass sit inside the frame and nothing crosses the heading) at the full width on phones; the flight's floor shadow starts at the net, where the drawn floor does. Not pinned; floor --stage at both ends with three lifts (image, words, drawing) | K17 settles (scale 1.08 → 1; scrubbed from 1000 px, 1.6 s on entry below); the words rise on entry. G17 scrubs with its own scroll (its top at 85% to its foot at 55%): the flight draws with a ball riding its head, the bounce mark lands and a ripple runs out from it, then both exits draw together, each with its ball, and the labels arrive. Reduced motion and the server render: the final state (both exits drawn, both balls at their ends, the labels shown) |
| 10 | Feel (pinned 0.8 screen ≥ 900 px; `#feel`; after Surface, 2026-11-02) | G02 vibration graph; eyebrow "Direct feel", "You feel exactly where you met the ball.", the owner's lead "The impact is absorbed by the entire unibody's surface." and three points (the second's title carries the impact-absorption number from `specs.ts`, "Vibration settles within 60 ms.", provisional; the third "The head twists less."). From 900 px wide and 560 px tall the headline, G02 and the three points are one screen below the header, pinned or not (owner, 2026-10-23): the words and points keep their size (the h2 capped at 6.6svh, so 1536 × 730 keeps two lines) and G02 fills the height between them (`VibrationGraph fill`). Phones and tablets stack it. Unibody has just told the cause, so Feel names the joint once (point 1) and never the tube. The points' rules are a translucent white (as Durability's), so they read over the pool's light as well as the floor. Its Skip link lands on Durability | Graph reveal on entry; pinned, the three points rise in the scrub (0.04 to 0.36, staggered), then the screen holds; below 900 px they rise on entry |
| 11 | Durability (`#durability`; after Feel) | G14 lifespan graph (0 to 5 years: most padel rackets 1 to 2, KINETIQ 5). ≥ 1000 px: copy in columns 1–4, G14 in columns 6–12; then four reasons (the sealed core first; four across ≥ 1200 px, two by two from 900 px, on a shared title row and body row so every body starts on one line); the fourth, "Made for regular play.", gives the usage profile (about 160,000 ball strikes) and the promised fatigue tests in its own sentence. No fine print: the only section that says five years | G14 draws on entry: window, typical lane, KINETIQ trace behind a glow head, then the five-year numeral |
| 12 | Identical (CTA 2) | K07 five rackets, Command and Pace alternating (the re-render, owner 2026-10-23); "within 1.0 g ... to within 0.1 mm", the stats ±1.0 g and ±0.1 mm; G04 spikes, G08 card; "Every KINETIQ is made to the same weight and balance."; Reserve Now with the hero's price line. From 700 px K07 spans the width at its own 16:9, anchored to the section's foot, and the section is the words plus two thirds of K07's height, so the words always end a third of the way down it, over the dim tops of the light shafts and clear of the racket heads (every pixel under the lead 4.5:1 or more against `--steel`); above it the floor is K07's own top colour. Phones: the words over a lift, then K07's trio crop; Reserve Now at the full measure, like the hero's and the finale's. From 700 to 899 px the card is about 460 px wide and centred, so it and its Reserve Now share one screen. Only the price line under the card rises in: the Reserve Now never fades, so whenever the header's compact one hides for it, it is on screen | Rise on entry |
| 13 | Choose your feel (`#feels`) | K08 pair (Command white 3K left, Pace black 12K right; the frame rises out of the floor at its top, over at most 64 px from 700 px and 20 px on phones, clear of the crowns, and fades at its foot), each feel's name and "Built for control" / "Built for power" (steel, lead size) directly under its racket's cap and shown with the photo, so the pair is never two unnamed rackets; then the compare, one column per feel: one character line (what we made, then what it does for you), and four ruled rows, label left and value right at 18 px and up (Feel, Face, Core, Suits; the Face row is a spec, the colour and the weave, never a repeat of the line). The two lines are kept the same length and set in the ruled rows' box, left-aligned on the labels' edge, so they wrap alike and the two columns read as one grid. From 700 px the columns share their rows through CSS subgrid, so every row sits level with its counterpart; phones stack Command, then Pace. Then the closing line across both columns under a full-width hairline: only the core and the face differ | Rise on entry |
| 14 | Specifications (`#specifications`) | Eyebrow "Specifications" and "As large as the rules allow." beside the lead from 900 px; six cells ruled like a spec sheet, every figure to one decimal (owner, 2026-10-22: 455.0 mm, 260.0 mm, 38.0 mm, 355.0 g, 250.0 mm, then 42 holes moulded; G01 and the Two feels closing line use the same precision; 3 × 2 from 900 px, 2 × 3 on phones); then G01 whole (full sheet ≥ 1240 px, front view below), on two lifts. G01 draws the canonical racket: Ø14.0 ×8 and Ø12.4 ×34, the 4 mm line where the flat face ends, the head flowing into the handle, the overgrip's helical wrap and the black cap engraved Q, the logo (named in callouts on the full sheet); Section A-A cuts below the hole field, B-B through the top row | Cells rise on entry; the drawing draws on |
| 15 | Editions (`#editions`) | The h2 "We make one racket, in three editions." (each clause kept whole) and its lead (`editionsIntro`), then three cards (K11-single, one white Command racket shot with K11's camera and light / K11 Command pair / K09; below 900 px the frames are square (from 600 to 899 px each card is 62% of the track, so the next one peeks in), KINETIQ's racket and the First 500 pair shown whole with air above and below and their sides feathered, and the price sits right under the name, so a card's image and price share a screen and the spare height falls at the card's foot), every card with its includes (KINETIQ's four follow First 500's order, racket, number, card, shipping) and one price foot line. From 900 px the three cards share six rows through subgrid (image, name, card line, includes, One of Ten's invitation note, price foot), so the includes start on one line and the feet stay level; from 900 to 1279 px the status sits above the name, as on phones, so the head fits its card. The availability tags are all in the amber family (First Edition and Limited amber, Invite Only amber-hot), so none reads as a control. KINETIQ and First 500 are whole-card links to /reserve?tier= with the arrow; One of Ten is not a link (no hover, no arrow): "By invitation" in its foot while invitations are open, and a quiet "Have an invitation?" link to /reserve?invite ("Invitations open soon." while invitations are closed). Nothing under the cards: no markers and no fine print (owner, 2026-10-22). The intro's light spills about 100 to 130 px up into the section above on purpose (Specifications since 2026-10-28, whose drawing ends above it), so the two sections meet without a hard line | Rise on entry |
| 16 | Finale | K01 in its beam over the horizon, one screen with the footer: ≥ 1000 px the hero mirrored (racket left, words in the right 7 columns as the hero's sit in the left 7; the line a step under the h2 size at a 24ch measure, four lines, each a whole phrase, with no-break spaces in `copy.ts`; the frame fades in from Editions' floor at its top and out into the section's last colour above the footer, clear of the cap's foot, so the beam never meets the footer on a line); phones: racket, then words, the line a step under the h2 size so it sets in four whole phrases too, and a header-high band above the frame that ramps from Editions' floor to the 4:5 frame's top row; phones 740 px tall or less show the wide crop (the whole racket and its horizon centred, exactly one screen with the footer) on a flat band, the frame rising out of it over 32 px, since that crop's top row is darker left than right; taller phones the 4:5 card crop. Line: "Each KINETIQ is moulded in Switzerland as one carbon shell, to within 15 microns." (Born whole, Unibody and Precision in one whole sentence, answering the hero's "moulded to 15 microns"; never the five years or "the feel you choose", which Two feels and Editions say); under it, the hero's price line | Rise on entry |
| /reserve | Sticky gallery with per-edition slides and gallery controls. KINETIQ opens on K01, shows K12 second for Command once it is exported (K12-base only, its lit pass shown nowhere, so at the payment the racket looks as the feel picker says), then K02, K04 and K08's Command racket, and ends on the racket's own measurement card (serial KQ-000427, in the chosen feel); in Pace it opens on K08's Pace racket and its card is KQ-000428's, the racket K08 shows. First 500 opens on K11, the set in the chosen feel with 027/500 on both throats, then K10 (Command only: its throat is white twill) and the two matching sample cards: B sits behind A with only its header and set number showing (below 1024 px its set number alone, so the pair fits the frame whole, A at the single card's width in a tighter rhythm, its text at 16 px; in a frame under 468 px tall B shows only its edge behind A and the text shrinks to fit, never under 15 px; the single card on phones is A's size, 300 px wide), never the text-free thumb and never cut off by the frame. The gallery stacks above the options below 1024 px and in any portrait window (`(max-aspect-ratio: 4/5)`, the 12.9-inch iPad Pro at 1024 × 1366 or 1024 × 1292; side by side only from 1024 px and wider than 4:5, range syntax, the exact complement, as in the Hero). Stacked, the frame is 4:5 where the screen is tall enough and shorter, down to square, where it is not, so the first view holds the frame and its arrows, dots and counter (56 px) above the Due Today bar and its fade (390 × 664, 375 × 667 and 768 × 1024 alike); the slides use their 4:5 phone crops wherever it stacks (`phoneMedia`), K02 edge-on contained with its sides feathered, K07's square trio crop shown whole across the frame's width with its top and foot feathered, and every other subject kept whole by its position. K12 shows its 4:5 portrait crop at every size, contained and centred on a flat slide in the render's own edge tone (no lift behind it), its edges feathered; on wide screens its frame ends 16 px above the floating controls, so the engraved cap clears them. One of Ten opens on K09, then G12. The gallery follows the slide on show, not its position: a change of feel keeps the measurement card or the feel's racket in view (to compare), and otherwise moves to the chosen feel's racket; a new edition starts on its first slide. Beside the gallery, the options column, headed "Reserve your KINETIQ" (the cards name the editions, so the base edition's name, the brand's, is not repeated in the chrome: each card's includes sit under "Included"); the sticky bar reads the racket count ("One racket", "Two rackets") over Due Today. Before the edition streams in, a neutral shell shows (lit stage, empty column: no edition, price or count), so a ?tier= link never paints another edition first. The column fades under the header and above the sticky Due Today bar instead of being sliced | Tier cards (G11 glyphs: one racket, two, three; One of Ten shown whole but locked, with no hover, press, focus or selection until an invitation code unlocks it), the feel picker (Command and Pace stacked, two across once each can be 320 px wide; each shows name and sub, the spec in Saira and one line, with the helper line under them), trust list (the two badges stack full width while the column is narrower than 700 px, a container query, and share one row at 2560), Due Today, the order line (it breaks only between the order and "Due today", never inside either), Pay with Card → form in place (the edition locks while it is open, the feel only while a payment is processing; Postal code and City share a row once the options column is 410 px wide, a container query, so tablets pair them and phones stack them) | Crossfades; fields rise 8 px |

Stills are exported by `scripts/stills.mjs` from 16-bit Blender masters (not committed) to AVIF + WebP with
phone crops (`src/content/stills.json`), and rendered with `<Still>` (`src/components/media/Still.tsx`). K12 (the
sweet spot) has two passes that register pixel for pixel, `K12-base` and `K12-full`, each with a `wide` and a
`portrait` crop (the 4:5 window, x 0.435 to 0.885 of the master); since 2026-10-28 only K12-base is shown, on /reserve.
`<Still phoneMedia>` moves the phone crop's breakpoint where a slot stays 4:5 or portrait above 699 px: the hero's
portrait layouts, the /reserve gallery wherever it stacks (below 1024 px, or portrait), and the finale only on phones taller than 740 px.
Swivel frames (`scripts/sequence.mjs`, `media/Swivel.tsx`; the phone load budget, 2026-11-01): AVIF where the browser
decodes it (a probe; iOS 16+), WebP 84 elsewhere. AVIF 58 for the landscape (desktop) sets, as sharp as WebP 84 and about
40% smaller; AVIF 50 for the portrait (phone) sets, about 24% smaller again (PSNR 44.5 against 45.9 dB on K02, no
difference at 100% on a 3x screen; 2x crops show the twill a touch softer). Command's K02 phone sequence keeps 45 of its
60 frames, as Pace's, and the manifest names each kept frame's source frame (`source`, `sourceFrames`) so Swivel.tsx
plays the turn at the render's own speed (60 to 45 steps 1 or 2 source frames: mapped linearly it wobbled); the frames
start after the load event and a change of feel cancels the other feel's downloads. Every frame, AVIF or WebP, is
served `private, immutable` with `Vary: Cookie` (next.config.ts). Measured with `node scripts/load-budget.mjs <url>` (the phone
profile, a visitor reading every screen; 2026-11-01, iPhone 390 x 844 in Command): the whole home page, every lazy still
and both swivels, 3.1 MB, 15.3 s of transfer and 18.1 s of busy network (the honest figure: it counts each lazy still's
round trip), was 5.7 MB and 30.7 s busy before AVIF and 3.6 MB and 20.8 s with AVIF 58 phone frames; the swivel frames
are in by 14 s. 390 x 664: 2.9 MB, 17.3 s busy. Pace: 2.2 MB, 14.4 s busy. iPad Pro portrait (2x, its K02 drawn from the
60 desktop frames at 2560): 5.3 MB, 29.6 s busy at the phone profile's 1.6 Mbps, which an iPad on Wi-Fi does not see.
Graphics live in `src/components/graphics/` with review pages at `/lab/<id>` (dev only); G15 is the sweet spot
(`SweetSpotField`, `/lab/g15`), G16 the carbon cross-sections (`CarbonLayup`, `/lab/g16` only since 2026-10-29), G17
the slice after the bounce (`SliceBounce`, `/lab/g17`, Surface).

## Sweet spot (owner, 2026-10-22)
The owner: make a claim for how big the sweet spot is, the way Apple claimed almost no border on the iPhone and Apple
Watch screens, assuming the sweet spot is as big as it can theoretically be.
- **The claim, told as Apple tells a display:** a vision line, one area share and one border in millimetres (Apple
  Watch Series 7: "nearly 20 percent more screen area", "borders at just 1.7 mm"). Apple adds a footnote that says
  what is counted; here there is no footnote (owner, 2026-10-22: no small print), so line 1 says it in its own words.
  Eyebrow "Sweet spot" and h2 "Edge to edge." (the section is labelled by both), two lines in the plain voice (the
  first about the face only, ending "we designed all of that flat face to be sweet spot": what is counted, and that it
  is a design, opening on the owner's "the world's largest sweet spot", 2026-11-02; the frame tube is Unibody's to tell), then the lockup "Nearly 99% of the hitting surface is sweet spot"
  ("Nearly" at the unit's size, on the numeral's baseline) and "1 mm from the sweet spot to the edge", Saira at weight 200,
  tabular, each item read as a sentence. No caption (owner, 2026-10-23: no "Illustrative" captions). No comparison in
  the copy or the drawing. The words rise on opacity only (never visibility), so the claim stays in the accessibility
  tree.
- **The numbers come from the geometry,** never typed by hand: `graphics-sweetspot.ts` takes the face above the
  bridge (y ≥ −86.5 mm, 531.5 cm²) and insets it 1 mm from the outline and 1 mm above the throat (523.2 cm², 98.4%;
  since 2026-11-02, when the flat face was taken out to the 1.0 mm edge radius: it was 4 mm, 93.8%), and `SWEET_CLAIM`
  rounds it as Apple rounds a display: up to the next whole number only with "Nearly", never more than one point (Apple
  Watch Series 7: "nearly 20 percent"; a 5.85-inch iPhone X display was sold as 5.8-inch). The section, G15's text
  alternative and K14's alt are built from it; /lab/g15 checks it against the geometry. If `racket-shape.ts`
  changes, the lockup and the alt text change with it.
- **The image (owner, 2026-10-28):** the upright K12 racket is off the landing ("I dont like the edge to edge hero";
  /reserve keeps K12-base). K14 (live) is a K04-style macro of the face running out to the rim: close, in
  raking light, the weave resolving, the flat face meeting the 1.0 mm edge radius (re-rendered for the 1 mm canon on 2026-11-02, both feels; `stills.json`: wide, a 4:5 portrait
  crop x 0.385 to 0.835, and K04's card crop; K14-pace the same). If K14 is ever missing, the section shows G15, the
  drawing, and reads complete.
- **G15** is the fallback if K14 is missing: the canonical silhouette face-on in white 3K
  twill (an SVG pattern: the warp a step darker than the weft, rounded tows, fine crevices) in a low studio light, the
  field lit warm white and even to the 1 mm line with the weave reading through it (luma about 214 with the twill
  spanning about 30 levels at 1×), an amber hairline on the line, the holes open with each bore's lit wall and lip on
  the lower right, the overgrip's wrap and the Q on the cap, a steel rim hairline, one clear-coat gloss line, and a 20×
  lens on the edge with the dimension "1 mm" (HTML, 15 px and up). The lens is drawn at its own scale, never the
  racket scaled up (`lensDetail` in `graphics-sweetspot.ts`): the flat band in the racket's carbon tone at that spot,
  the 1.0 mm edge radius as a highlight, the lit field with a fine hatch to its amber line, the page's own graphite
  beyond the edge; the dimension's arrows end on the 1 mm line and the outline, with short extension ticks. Variants: "wide", "portrait" (phones; the lens
  beside the handle) and "auto" (portrait below 700 px). No ember, no tube line.
- **The 1 mm line (2026-11-03):** `SweetSpotEdge` (graphics/) is traced from K14's export, not drawn from the shape:
  for each 32 px column of the 2560 master, the rim's outer edge (the first pixel over luma 90 above the studio) and
  the inner end of its highlight (the 1.0 mm edge radius, where the flat face begins), each fitted with a polynomial
  (under 1 px off at 1280). The amber line runs on the inner curve, so the lit band between it and the outline is the
  1 mm the lockup names. One path per crop through its own viewBox (wide; portrait, x 0.385 to 0.835), fitted like the
  image (cover). If K14 is re-rendered with another camera, re-trace it (the method is in the component's comment).
- **Layout:** pinned from 900 px (the table, row 8); stacked below 900 px and with reduced motion. G15 (the fallback):
  the words in columns 1 to 5 and the drawing on the right. The floor is --stage at both ends, the sealed core's above
  and Surface's below (checked with a pixel probe), with lifts behind the image and the words (fill rule).
- **Motion:** the table, row 8. G15: the light never scales: a soft mask disc grows from the sweet spot (about 25 mm
  above the head centre) and reveals a field that is already whole. Reduced motion and the server render show the
  final state: every word visible. The words rise on opacity only, never visibility.

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
- Header (owner, 2026-11-03: "when on iphone, I have to scroll all the way back up to change the toggle?"): the Feel
  and Handle choices together (`ViewControl`, `components/chrome/`), on /, /reserve and /reserved, one tap away from
  anywhere on the page. Shown as soon as the hero's own toggle row (`data-view-toggles`) is no longer wholly in view
  below the header (an IntersectionObserver with the header's height as its top margin), so at every scroll position
  one set or the other is visible and tappable (watching the whole hero left a dead band while its last screen left,
  about 600 to 790 px scrolled at 390 x 844; a probe at every viewport, both feels and both motion modes, checks it with
  document.elementFromPoint every 12 px); on /reserve and /reserved from the first paint; never hidden with the compact
  Reserve Now. It fades and settles in 200 ms ease-out (opacity, 4 px), and its box is always laid out, so nothing
  shifts. While the compact Reserve Now is hidden (over the hero's last screen, Identical and the finale) the control
  slides flush to the row's end by that button's width and the gap (`translate`, measured into `--view-shift`; 200 ms
  ease-out, crossing above it), so the phone's header never shows a hole; on phones only the button moves, since its
  panel is placed against the header. From 1024 px the two named groups sit in the header, a 1 px
  hairline between them, before the compact Reserve Now. Below 1024 px one 44 px button, a quiet capsule (1 px `--edge`
  ring) round the current face swatch and handle glyph and a small chevron, read from html[data-feel] and
  html[data-grip] so the server paint is right; its name carries the choice on show, "Feel and handle: Command, Naked"
  (`site.viewToggleLabel` and the toggles' labels, passed as props), the panel's group "Feel and handle". It fits the 375 px
  row: wordmark 128, button 66, compact Reserve Now 126. A tap opens a small panel under the header at its right margin
  (opaque `--graphite-2`, a step above the section floors so the page never ghosts through it, a hairline
  border, 22 px radius): two rows, Feel (Command, Pace) and Handle (Grip, Naked),
  each name in Saira 15 px `--muted` before its radio group, the options in two aligned columns, every option 44 px
  tall. It enters from scale 0.97 and 4 px up in 200 ms ease-out and leaves in 150 ms (transform and opacity; reduced
  motion: instant); opened or closed from the keyboard it appears and goes at once and focus moves to the checked
  option. A disclosure, not a modal (`aria-expanded`, `aria-controls`; the panel follows the button in the tab order):
  it stays open while choices are made, so Grip and Naked can be compared on the image beneath, and closes on Escape
  (focus back on the button), a press outside it, focus leaving it, or the hero coming back. A choice there reaches
  the /reserve experience too (`onFeelChoice`), over a ?feel= from the link. The not-found and credits headers have no
  toggles, so the gate's shared not-found tree carries none of these words (props from `Chrome.tsx`).
- State: `lib/feel-store.ts` (`useFeel`, `setFeel`, useSyncExternalStore) writes `kq-feel` in localStorage (try/catch;
  in memory when blocked), a first-party `kq-feel` cookie (Path=/, one year, SameSite=Lax, Secure on https, not
  HttpOnly) and `html[data-feel]`, which the head script sets before the first paint (from localStorage, else the
  cookie). Safari on iPhone (ITP) holds a cookie written by script to 7 days, so script writes only bridge to the
  server: `src/proxy.ts` sends the cookie back with Set-Cookie and a fresh year on every cleared page load that carries
  it; a choice (a second after the last toggle) and the head script's restore of a missing or out-of-step cookie (after
  the load event) send a HEAD of / so the server renews it at once; the head script never rewrites a cookie already in
  step, which would put it back under the cap. So a Pace visitor keeps the Pace page however long ago they chose,
  as long as they come back within a year. Every toggle's
  thumb and labels read that attribute, so all of them agree and a stored Pace never flashes Command. Reserve Now
  links (hero, header, Identical, finale, the edition cards) carry the choice into checkout (`?feel=`, `ReserveLink`);
  the /reserve feel picker writes the same preference, and its gallery shows a still's Pace version in its own feel.
- Stills: a still's Pace version is its id plus "-pace" with the same crops (`K01-full-pace`, `K01-hero-full-phone-pace`,
  `K02-pace`, `K05-pace`, `K05-phone-pace`, `K06-base-pace` so far, `stills.json`). Where one is exported, `<Still>`
  follows the feel (`FeelPicture`): one <picture> holding one version at a time (never both downloading), the server
  painting the page's feel. Server feel (2026-11-01, phone LCP for a returning Pace visitor 5.5 s → Command's): with the
  `kq-feel` cookie, `src/proxy.ts` rewrites /, /reserve and /reserved to the same page prerendered in that feel
  (`app/feel/command|pace/`, re-exporting the pages under a `ServerFeel` layout, `lib/feel-context.tsx`; the URL stays,
  pages stay `private, no-cache`, so they are revalidated against the current cookie; /feel/* directly is a 404), and
  `useFeel` hydrates from it, so the HTML already points the hero and every Pace-capable still at its Pace files and
  Command is never fetched. Without the cookie (a first visit, or a choice made before the cookie existed: the head
  script sets it for the next load) the server paints Command; after hydration a stored Pace replaces it, hidden from the first paint by html[data-feel], and a
  change fades the image out (150 ms) and the other version in once loaded (240 ms ease-out, opacity only; reduced
  motion: instant). The box keeps its size, so nothing shifts. A crop without a Pace export keeps its Command file
  silently. Stills that name a feel keep their own logic (K08's pair, K11-command / -pace, K07 alternating, K12 and the
  measurement cards). Known cost, only without the cookie: the browser fetches the hero's Command files once before
  hydration; lazy stills load only their Pace file. `check.mjs --feel=pace` (and every case, in its own feel) fails
  on any still or swivel frame fetched in the other feel.

## Grip toggle (owner, 2026-11-02)
The owner: "render images without the grip to show it's a single one piece... like the command/pace toggle, could we
have another minimal toggle to show a remove the grip?" (`GripToggle`, `components/chrome/`; its group name "Handle" and
the labels "Grip" and "Naked" come from `site.ts`; owner, 2026-11-03 PM: "rename bare to Naked which shows 100%
carbon", so Naked has no overgrip and no black cap: the handle and its end are the shell's carbon in the feel's weave,
the Q engraved into the carbon end; internal ids keep "bare" and "nogrip"). The feel toggle's language exactly (`FeelToggle.module.css`): a
small glyph with its name in Saira, the chosen one ringed in `--text` and its name `--text`, the other `--muted`; no
pill, thumb or fill. Its glyph is an upright handle (8 × 16 px): Grip is the black overgrip with its helical wrap,
Naked is the face's own carbon in the feel on show, a fine twill with no cap (white 3K in Command, black 12K in Pace,
from html[data-feel]). A
native radio group, every option at least 44 px square to the touch, pressing to 0.97.
- Hero: after the feel toggle, a 1 px hairline between them, beside Reserve Now from 700 px and above it on phones
  (the four options in one row: 5 px padding round each name below 700 px, so the row fits 335 px at 375 px; it wraps
  under the feel toggle on anything narrower). And in the header with the feel toggle (owner, 2026-11-03), in its view
  control on /, /reserve and /reserved ("Feel toggle", Header), so Naked is one tap away anywhere. Every grip toggle
  reads the one store, so all agree; a change mid-page swaps the images in place with no reload and no scroll jump.
- What it changes (owner, 2026-11-03: "when I set the toggle to bare, Most renders still have the grip?"): every still
  that shows the handle, on /, /reserve and /reserved, in both feels. Each has a grip-off twin, named by `<Still>`'s
  `bareId`: "-nogrip" after the K-number, then "-pace" and the crop as usual (K01-nogrip-full, K02-nogrip-pace,
  K11-nogrip-single, K05-nogrip-phone), with the same crops, so callers pass nothing: a `<Still>` finds its twin by name
  (`bare={false}` opts out) and `FeelPicture` holds one variant at a time, feel and grip, swapping with the feel's fade.
  A crop or feel whose twin is not exported yet keeps its grip-on file (never the other feel's face). The twins are
  rendered by the same shot with `KQ_NOGRIP=1` (render/README.md), in the canon of the grip-on still they replace
  (the 1.5 mm edge with `KQ_EDGE_MM=1.5` where the site still shows it), so a flip changes only the handle. The
  hero swivel turns in Naked too (2026-11-04: `K01-swivel-nogrip-<feel>-<layout>`, both feels, the light sweep, frame 0
  the K01-nogrip-full / -hero-full-phone still); Unibody's K02 has no grip-off sequence yet, so with Naked it shows its
  still as it scrolls (the Swivel is given `K02-swivel-nogrip`, which finds no frames; a future
  `K02-swivel-nogrip-<feel>-<layout>` export plays with no code change). Not changed: the
  social card (`og.jpg`: crawlers carry no cookie) and G01's drawing in Specifications (it names the overgrip).
- No wrist cord (owner, 2026-11-03: "no need to add the wrist cord"): no render shows the FIP cord, with the grip or
  without it; the canon keeps "no wrist cord" (render/notes/canon.md). The product must still ship with one (CLAIMS.md
  row 52).
- State: `lib/grip-store.ts` (`useGrip`, `setGrip`) writes `kq-grip` in localStorage (try/catch; in memory when
  blocked), mirrors it in a first-party `kq-grip` cookie with the feel cookie's attributes (renewed by `src/proxy.ts`
  with Set-Cookie, as `kq-feel`), and sets `html[data-grip]`, which the head script sets before the first paint (it also
  writes back a stored choice the cookie lacks). Server variant (review, 2026-11-02: a returning Naked visitor's phone
  LCP was 5.4 s when the bare stills waited for hydration): a cleared request for / with `kq-grip=off` is rewritten to
  `app/feel/bare` (no feel cookie) or `app/feel/<feel>/bare`, the same page under `ServerGrip` (`lib/grip-context.tsx`),
  so the server HTML already points every `<picture>` at the grip-off twins and no grip-on file of a still with a twin
  ever loads. /reserve and /reserved have bare variants too (`app/feel/[<feel>/]bare/reserve`, `.../reserved`; owner,
  2026-11-03). `check.mjs --grip=off` (with `--feel=pace`, and on any `--path`) checks it: LCP budget and no grip-on
  file of a still with a twin fetched.
- Release 7 (2026-11-04): the four K01 hero swivels (Grip and Naked, Command and Pace) are rendered on the Mac node
  (Metal) in the light-sweep scene with their stills on the same device, so each frame 0 is its still bit for bit; the
  Naked hero turns as it scrolls away like the Grip one.
- Release 6 (2026-11-02, accepted): Naked ships with its still. The grip-on hero stills (K01-base, K01-full, the two
  K01-hero phone masters) and K02, both feels, stay on the exports main had (the 1.5 mm canon), because each swivel's
  frame 0 must be its still and the swivels are not re-rendered yet: a new-canon still would visibly soften the weave
  as the turn starts. The HD re-renders are committed in the masters repo and reproduce bit for bit with
  `node scripts/stills.mjs <masters>/stills/K01 <ids>` (and K02); export them in the same commit as the new swivels.
- A twin follows its grip-on sibling's canon (2026-11-03): K01's hero and finale twins and K08, K12 are the 1.0 mm
  canon; K02, K05, K06, K07, K09, K10 and K11 twins are the 1.5 mm canon (`KQ_EDGE_MM=1.5`), as their grip-on stills.
  When a grip-on still moves to the new canon (K02 with its new swivel), re-render its twin in the same commit
  (the same command without `KQ_EDGE_MM` and `--set HD=0`), or a flip of the toggle changes the edge and the weave too.
  K02's Unibody turn has no grip-off sequence: render one (K02-edge-line.py `--set NOGRIP=1`, the swivel's own
  arguments) with the new-canon K02 swivel; until then Naked holds the still there, as in the hero.

## Micro-interactions
Pressables scale 0.97 on `:active`; hover only behind `(hover: hover) and (pointer: fine)`; transform and
opacity only, 150–300 ms ease-out (`--ease-out`); exits faster than entries.
Skip links on the pinned chapters (Unibody, Precision, Holes, Sealed core, Sweet spot, Feel) appear only on keyboard focus: visually hidden otherwise (still
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
English only at launch (`lang="en"`). Archivo and Saira load `latin` and `latin-ext`, but preload only `latin`
(2026-10-29): no word on the site needs `latin-ext`, which keeps its unicode-range @font-face and loads only for a
character it covers, so its 112 KB never share a phone's first second with the CSS and the hero still (phone LCP
about 0.4 s sooner).
