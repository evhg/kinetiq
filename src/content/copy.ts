// All landing-page words, in one place. Every claim here has a row in CLAIMS.md.
// House rules: weights always carry a decimal (355.0 g, ±1.0 g), never a range. The spec figures share one
// precision (owner, 2026-10-22): 455.0, 260.0 and 38.0 mm, 355.0 g, 250.0 mm.
// No middle-dot strings, no workshop, town or supply-chain talk.
// Banned (owner, 2026-10-21): "The world's first one-piece padel racket." as a headline, and any line like
// "Moulded, measured and finished in [town], by a carbon workshop that already builds full-carbon golf clubs."
// Retired (owner, 2026-10-22): "One piece" as a marketing phrase, except in the owner's own hero sentence,
// which stays verbatim (CLAUDE.md; the owner replaced the hero lead after retiring the phrase). Elsewhere the
// construction words are "unibody" and "Zero seams.", scoped to the frame: "No joint to work loose." Never
// "zero weak points" or "nothing to come apart" (absolute durability promises, CLAIMS.md row 8b), never
// "first unibody" (the word is already used in other racket sports, row 3).
// Durability (owner, 2026-10-22): "Built to last five years" is said in one place only, the Durability section,
// where its usage profile and the promised fatigue tests are told in its own sentences (owner: the five years in
// three places was too much). Never in the hero, the finale or the meta; the one edition line that names five years
// is One of Ten's guarantee, which the owner asked for. Never "lifetime guarantee", never "sustainable", and never a
// guarantee for every racket (only One of Ten carries one). Until the independent
// fatigue report exists the testing is promised, never claimed as done (CLAIMS.md rows 26 and 28).
// No small print (owner, 2026-10-22): no footnote markers (*, \u2020, \u2021, \u00a7) and no fine-print lines. Where a
// qualifier keeps a claim honest, it is part of a plain sentence in the body copy ("as designed", "made to last",
// "Independent fatigue tests will confirm it"); a graphic with unmeasured data keeps its "Illustrative" caption.
// Sealed core (owner, 2026-10-22; CLAIMS.md rows 30 to 34): the carbon shell closes around the whole EVA core
// and lines every hole, so the core never touches the air. It is told once per place: the reveal in the
// unibody chapter (unibody.sealed), the drilled hole that opens a core (holes.body), and the result in
// Durability ("three times longer", only against the same core left open, and only as a design: "made to last").
// The seal keeps out sweat, humidity and UV; never heat (the shell does not insulate), never "airtight",
// "waterproof" or "first". "Swiss-made EVA" stays at country level: never the factory, a supplier or a town.
// Voice (owner, 2026-10-22; batch 3 names-copy-final): whole, plain sentences that say what we made and what it does
// for the player, as Jony Ive would say them. No two-beat slogans, no stacked fragments, no "Not X. Y." pairs, and
// no "premium", "simply", "incredibly", "monolithic" or other lofty words. The owner's hero sentence stays verbatim.

import { lifetime } from "./lineup";
import { site } from "./site";

export const hero = {
  eyebrow: "100% Swiss Made",
  headline: "The most precise padel racket ever made.",
  /**
   * The owner's own sentence (2026-10-22), verbatim by his instruction (CLAUDE.md): it keeps "One single piece"
   * and "1 gram" (the ±1.0 g weight tolerance, CLAIMS.md row 12) even though both rules apply everywhere else.
   */
  lead: "One single piece of space-grade carbon. No tube, no joints. Ultra-precision moulded to 15 microns and 1 gram. Every racket plays exactly the same.",
  /** Under Reserve Now: "From €410, fully refundable, and shipping in January 2027." */
  ctaNote: site.priceNote,
};

// The landing page runs in three movements, one idea per screen (batch 3 deck, section 1):
// Meet it (hero, sweet spot, Unibody, Feel), Prove it (Born whole, Precision, Holes, Durability, then the
// Specifications as the recap) and Choose it (Identical, Choose your feel, Editions, Finale). The four-number
// strip under the hero (0 seams, 15 µm, 0 drilled, 5 years) is retired: each number has its own chapter.

/**
 * Sweet spot, the first idea after the hero (CLAIMS.md row 6b): Apple's edge-to-edge display claim, told of the
 * face. The owner's assumption (2026-10-22): the sweet spot is as big as it can theoretically be, the whole flat
 * face. The numbers are never typed here: graphics-sweetspot.ts computes them from racket-shape.ts (SWEET) and
 * rounds them as Apple rounds a display (SWEET_CLAIM), and the words below take them as arguments. The flat face
 * ends 4 mm in from the edge (the 1.5 mm edge radius plus 2.5 mm) and 4 mm above the throat, and covers 498.7 of
 * the 531.5 cm² of face above the bridge, 93.8%, said "Nearly 94%" (Apple Watch Series 7: "nearly 20 percent";
 * a 5.85-inch iPhone X display was sold as 5.8-inch, so Apple never rounds up without a word). A design ceiling,
 * not a measurement: line 1 says so in its own words ("we designed all of that flat face to be sweet spot": what is
 * counted, and that it is a design), and the caption says "Illustrative. The sweet spot as designed." until the
 * independent rebound map exists. No fine print (owner, 2026-10-22). Line 1 is about the face only: the cause (the
 * frame tube we left out) is told once, in Unibody.
 * Never "all sweet spot", "zero", "no dead zones", "100%", "bezel", "twice the sweet spot", a comparison with a
 * tubular racket or another brand, or "largest".
 */
export type SweetNumbers = { share: string; nearly: boolean; exact: string; inset: string; field: string; face: string };

export const sweetSpot = {
  eyebrow: "Sweet spot",
  headline: "Edge to edge.",
  lines: [
    "The face stays flat right out to where the edge begins to curve, and we designed all of that flat face to be sweet spot.",
    "That matters most on the shots you can't set up, when you meet the ball late, high or off the glass.",
  ],
  /**
   * The lockup, each item read as a sentence: "Nearly 94% of the face is sweet spot." and "4 mm from the sweet spot
   * to the edge." `nearly` shows only when the numeral is rounded up. A no-break space keeps "sweet spot", the
   * section's own term, on one line wherever a label wraps.
   */
  share: { nearly: "Nearly", unit: "%", label: "of the face is sweet\u00a0spot" },
  inset: { unit: "mm", label: "from the sweet\u00a0spot to the edge" },
  /** Under the image, the K12 still or G15, which stands in for it until K12 is exported. */
  caption: "Illustrative. The sweet spot as designed.",
  /** K12 (K12-base, then K12-full): a face-on white Command racket whose face lights up to 4 mm from the edge. */
  imageAlt: (n: SweetNumbers) =>
    `A white KINETIQ Command racket face-on. Its face lights up evenly to within ${n.inset}\u00a0mm of the edge: the sweet spot as designed.`,
  graphic: {
    /** G15's detail: the edge magnified, with the band between the light and the edge dimensioned. */
    detail: (n: SweetNumbers) => `${n.inset} mm`,
    alt: (n: SweetNumbers) =>
      `Face-on KINETIQ Command racket in white 3K carbon twill. Warm light fills its face to within ${n.inset}\u00a0mm of the edge, ${n.nearly ? "nearly " : ""}${n.share}% of the face above the bridge, and the 42 moulded holes stay dark. A magnified detail of the edge measures the ${n.inset}\u00a0mm band. Illustrative.`,
  },
};

/**
 * Specifications, the recap before the buy (CLAIMS.md row 6c): six cells, then G01 whole. The outer dimensions
 * sit at the FIP limits (length 45.5 cm, width 26 cm, thickness 38 mm; `racket-shape.ts` peaks at exactly
 * 260.0 mm). Never "the largest face the rules allow": head length is free under the rules. The tolerances
 * (±1.0 g, ±1.0 mm) are told by Identical, which follows.
 */
export const specifications = {
  eyebrow: "Specifications",
  headline: "As large as the rules allow.",
  lead: "Its length, width and thickness each sit at the limit set by the rules of padel, and no further. The drawing below is to scale.",
  cells: [
    { value: "455.0", unit: "mm", label: "length" },
    { value: "260.0", unit: "mm", label: "width" },
    { value: "38.0", unit: "mm", label: "thickness" },
    { value: "355.0", unit: "g", label: "weight" },
    { value: "250.0", unit: "mm", label: "balance" },
    { value: "42", unit: "", label: "holes, moulded" },
  ],
};

/**
 * Unibody, pinned on wide screens: beat A (K02 edge-on), beat B (the cut-through and G07), then the sealed core.
 * Beat A says what one shell means in your hand, then what we left out (CLAIMS.md row 8c): "frame tube" is said here,
 * once, and the sweet-spot line above it speaks only of the face. Its three callouts sit beside
 * the parts they name, rim, bridge and handle, in that order (top to bottom on phones, where K02 stands upright).
 * Beat C (the three proofs) is retired: "One structure." is said by beat A, "A wider sweet spot." by the sweet-spot
 * section, and "The head twists less." by Feel. The chapter makes no sweet-spot claim of its own: the section above is
 * the only one (CLAIMS.md row 6b), so nothing here ties the sweet spot to the tube or says "more" against it.
 */
export const unibody = {
  edge: {
    eyebrow: "Unibody",
    headline: "It feels like one thing in your hand.",
    body: "We left out the frame tube. The face, the bridge and the handle are one carbon shell.",
    // The handle callout gives no number: Identical tells the tolerances (±1.0 g, ±1.0 mm).
    callouts: [
      { at: "rim", text: "The face is in play almost to the rim." },
      { at: "bridge", text: "Zero seams, so there is no joint to work loose." },
      { at: "handle", text: "The balance is set in the mould." },
    ] as { at: "rim" | "bridge" | "handle"; text: string }[],
  },
  section: {
    eyebrow: "Construction",
    headline: "The shell is the frame.",
    body: "Most padel rackets are built around a carbon tube. In KINETIQ, the faces close around the edge into one shell.",
    // G07 labels only the contrast it draws: the tube, its joints and the open core against one shell and a sealed
    // core. Only the frame tube's joints are marked: both constructions bond their faces to a core (CLAIMS.md row 4).
    // The tubular core is open to the air where the drilled hole cuts it; the KINETIQ shell lines the hole
    // and closes around the core (CLAIMS.md rows 30 and 31).
    // "Joints": one label led to both of the tube's joints (full section); "Joint": the one joint a phone's half shows.
    left: { title: "Tubular racket", tube: "Frame tube", joints: "Joints", joint: "Joint", core: "Open core" },
    right: { title: "KINETIQ", shell: "One continuous shell", core: "Sealed core" },
  },
  /**
   * The sealed core, over the K03 cut-through: the reveal. Durability carries the result (CLAIMS.md rows 30 to 33).
   * "Conventional" means a racket whose holes are drilled after curing; the claim is the drilled bore only, never
   * the core's edge, which a tubular frame closes (row 31).
   */
  sealed: {
    eyebrow: "Sealed core",
    headline: "The core never touches the air.",
    body: "In a conventional racket, every drilled hole opens the foam core to sweat, humidity and UV. In KINETIQ, the carbon shell closes around the whole core.",
    callouts: ["Swiss-made EVA", "Injected straight into the mould", "All 42 holes lined in carbon"],
  },
};

export const bornWhole = {
  eyebrow: "Born whole",
  headline: "Swiss Made, right down to the core.",
  body: "The two words you find on the dial of a Swiss watch are etched into the side of every KINETIQ. We make each one in Switzerland, in one mould, by one patented process.",
  lockup: { value: "100%", label: "Swiss Made" },
  badges: ["100% Swiss Made", "Patented one-mould process"],
};

export const precision = {
  /** `spokenUnit`: the record's h2 says "15 microns" to screen readers (the graph section's h2 says the headline). */
  record: { from: 500, to: 15, unit: "µm", spokenUnit: "microns" },
  /** "About": 15 µm is 21% of the 70 µm hair G03 prints, so "a fifth" alone would round in our favour. */
  recordLine: "About a fifth of a human hair.",
  headline: "Measured in microns.",
  body: "We hold every surface to within 15 microns of its design, and we measure every racket, not a sample, so each one plays the way we drew it.",
  graph: {
    caption: "Illustrative. Surface deviation along the racket, against the ±15 µm limit.",
    limitLabel: "15 µm",
    references: [
      { label: "Human hair", um: 70 },
      { label: "Sheet of paper", um: 100 },
    ],
  },
};

export const holes = {
  headline: "All 42 holes are formed in the mould.",
  body: "Drilling a racket cuts the fibres that carry the shot and opens its core to the air. We mould each hole instead, and wrap carbon around its edge.",
  stats: [
    { value: "42", label: "holes, moulded" },
    { value: "0", label: "drilled" },
    { value: "0", label: "fibres cut" },
  ],
  pair: { drilled: "Drilled: every fibre at the bore is cut.", moulded: "Moulded: every fibre flows around it." },
};

// Durability (CLAIMS.md rows 26 to 28, 34, 8b and 9b). The owner's "first of its kind" (row 28) names its category
// and claims the design, not finished tests: the fatigue report is promised before the first racket ships.
// Without a counsel-reviewed market search at launch, the lead's second sentence becomes "KINETIQ is built for
// five." Never the hero h1.
export const durability = {
  eyebrow: "Durability",
  headline: `${lifetime.line}.`,
  lead: "Most padel rackets are spent in one to two years. KINETIQ is the first padel racket built for five.",
  // The sealed core comes first: in most rackets the foam core is what gives out first (CLAIMS.md row 34). Its title
  // names the difference ("sealed, not open"), never "nothing to break down" (absolute, rows 8b and 30).
  // Point 4 carries what the fine print used to: the usage profile and the promised fatigue tests (future tense); it
  // never reads as a test already passed, and never repeats the five years the headline states (row 26). Its body is a
  // whole sentence that stands without its title; no "design life" (the page no longer defines it). It counts ball
  // strikes, the figure row 26's fatigue protocol tests (160,000+), never hours "of play" (row 27).
  // "Three times longer" compares the sealed core with the same EVA left open ("the same core left open"), never with
  // other brands' rackets, and never becomes a racket lifespan ("three to six years"): the five years rest on row 26's
  // own test. "Made to last" keeps it a design until the independent test exists (row 34).
  points: [
    {
      title: "A sealed core, not an open one.",
      body: "In a padel racket, the foam core usually gives out first. Sealed in carbon, ours is made to last three times longer than the same core left open.",
    },
    {
      title: "No seam to open.",
      body: "The face and the frame are moulded as one, so there is no joint between them to loosen over the years.",
    },
    { title: "No drilled hole to crack.", body: "Cracks often start at a drilled hole. All 42 of ours are moulded, with carbon wrapped around every edge." },
    {
      title: "Made for regular play.",
      body: "We designed it for two 90-minute sessions a week, about 160,000 ball strikes in all. Independent fatigue tests will confirm that before the first racket ships.",
    },
  ],
  graph: {
    typical: "Most padel rackets",
    typicalSpan: { value: "1 to 2", unit: "years" },
    kinetiq: "KINETIQ",
    kinetiqSpan: { value: "5", unit: "years" },
    kinetiqNote: "About 160,000 ball strikes",
    xAxis: "Years, at two 90-minute sessions a week",
    caption: "Illustrative. KINETIQ as designed, against brand and retailer guidance for most padel rackets.",
  },
};

// Feel follows the Unibody chapter, its cause (CLAIMS.md row 14). Unibody has just told the cause, so Feel names the
// joint once (point 1) and otherwise speaks of the hand: its body does not say "one carbon shell" again (the phrase is
// Unibody's and the finale's). Point 3 is the twist proof moved from the retired Unibody
// beat C (CLAIMS.md row 7); it replaced "The same, edge to centre.", which the sweet-spot section now says.
export const feel = {
  headline: "You feel exactly where you met the ball.",
  body: "What reaches your hand is the contact itself.",
  // Point 1 says "dull", never "soften": a softer hit is what Command sells (feelChoice), so the joint we left out must
  // never read as a cushion we took away. Each title states its claim once; its body gives the reason.
  points: [
    { title: "No joint to dull the impact.", body: "The face carries straight into the frame, so nothing blurs the moment of contact." },
    { title: "Vibration settles quickly.", body: "It spreads through one structure and fades, so your hand is ready for the next shot." },
    {
      title: "The head twists less.",
      body: "Because the bridge is part of the same shell, the head stays steadier on an off-centre shot, so the ball goes closer to where you aimed.",
    },
  ],
  graph: {
    caption: "Illustrative. How vibration fades after impact.",
    glued: "Tubular racket",
    kinetiq: "KINETIQ, unibody",
    settled: "Settled",
  },
};

export const identical = {
  headline: "Every KINETIQ is made to the same weight and balance.",
  body: "Each racket is within 1.0\u00a0g of the reference weight, and its balance is set in the mould to within 1.0\u00a0mm, so you can change rackets in the middle of a match and the new one feels like the one you put down.",
  stats: [
    { value: "±1.0", unit: "g", label: "weight, every racket" },
    { value: "±1.0", unit: "mm", label: "balance, set in the mould" },
  ],
  graphCaption: "Illustrative. Distribution against the tolerance window.",
  card: {
    title: "Certificate of measurement",
    tag: "Sample card",
    /** A single racket's serial, as on the K12 throat. */
    serial: "KQ-000427",
    /** The two rackets of First\u00a0500 sample set 027: their own serials, never the single racket's (CLAIMS.md row 15). */
    setSerials: { A: "KQ-000053", B: "KQ-000054" },
    rows: [
      ["Feel", "Command"],
      ["Weight", "355.2 g"],
      ["Reference", "355.0 g ±1.0 g"],
      ["Balance", "250.4 mm"],
      ["Thickness", "38.00 mm"],
      ["Max surface deviation", "0.012 mm"],
    ] as [string, string][],
    swiss: "Swiss Made",
    /**
     * A second sample racket, measured on its own: a single Pace racket's card, with this serial, and the B card of
     * the First\u00a0500 sample set, with `setSerials.B` (CLAIMS.md row 15).
     */
    second: {
      serial: "KQ-000428",
      values: { Weight: "354.9 g", Balance: "250.6 mm", "Max surface deviation": "0.011 mm" } as Record<string, string>,
    },
  },
};

/**
 * Choose your feel, under the K08 pair (CLAIMS.md row 16; batch 3 names-copy-final, section 3). The two character
 * lines follow one pattern, what we made and then what it does for you, so read side by side only the feel changes.
 * The rows are labels: no full stops. "Suits" is guidance, not a result. No stiffness numbers until measured; never
 * "Made in Europe" or "Easy on the arm". The closing line says plainly that only the core and the face differ.
 */
export const feelChoice = {
  eyebrow: "Two feels",
  headline: "We mould each racket in the feel you choose.",
  /** Before each feel's purpose: "Built for control", "Built for power". */
  builtFor: "Built for",
  feels: [
    {
      id: "command",
      name: "Command",
      sub: "Control",
      line: "We made Command to give a little as it meets the ball, so you can place it where you meant to.",
      rows: [
        ["Feel", "Soft and controlled"],
        ["Face", "White 3K carbon, the finer weave"],
        ["Core", "Soft EVA"],
        ["Suits", "A game built on placement: the lob, the chiquita, the bandeja"],
      ],
    },
    {
      id: "pace",
      name: "Pace",
      sub: "Power",
      line: "We made Pace stiffer and quicker, so it gives you more power when you swing through the ball.",
      rows: [
        ["Feel", "Quick and reactive"],
        ["Face", "Black 12K carbon, the bolder weave"],
        ["Core", "Two-density EVA, soft under the face and firmer in the centre"],
        ["Suits", "A game built on pressure: the first volley, a change of tempo, the smash"],
      ],
    },
  ] as { id: "command" | "pace"; name: string; sub: string; line: string; rows: [string, string][] }[],
  /** One bar across both columns (CLAIMS.md rows 12 and 16). */
  closing:
    "Command and Pace differ only in the core and the face. Both weigh 355.0\u00a0g, balance at 250.0\u00a0mm and are 38.0\u00a0mm thick, with the same 42 moulded holes.",
};

export const finale = {
  /**
   * The page's last line, one whole sentence that answers the hero's "moulded to 15 microns": it sums up Born whole,
   * Unibody and Precision. No five years (said once, in Durability) and no marker (owner, 2026-10-22); never "the
   * feel you choose", which Two feels and Editions say. "Each", because Identical's h2 opens "Every KINETIQ is made".
   * No-break spaces keep "in Switzerland", "one carbon shell" and "15 microns" whole, so from 768 px it sets as four
   * whole phrases ("Each KINETIQ is / moulded in Switzerland / as one carbon shell, / to within 15 microns."). Never
   * glue "moulded in Switzerland" or "as one carbon shell": either is wider than a phone's measure.
   */
  headline: "Each KINETIQ is moulded in\u00a0Switzerland as one\u00a0carbon\u00a0shell, to within 15\u00a0microns.",
  sub: site.priceNote,
};

/** The link-preview text, in whole sentences like the page. No five years (Durability only). */
export const meta = {
  title: "KINETIQ | The most precise padel racket ever made",
  description:
    "KINETIQ is a unibody padel racket in space-grade carbon, with no frame tube and a sealed core, made in Switzerland to within 15 microns. Reserve yours now, fully refundable.",
};
