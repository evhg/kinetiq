// All landing-page words, in one place. Every claim here has a row in CLAIMS.md.
// House rules: weights always carry a decimal (355.0 g, ±1.0 g), never a range.
// No middle-dot strings, no workshop, town or supply-chain talk.
// Banned (owner, 2026-10-21): "The world's first one-piece padel racket." as a headline, and any line like
// "Moulded, measured and finished in [town], by a carbon workshop that already builds full-carbon golf clubs."
// Retired (owner, 2026-10-22): "One piece" as a marketing phrase, except in the owner's own hero sentence,
// which stays verbatim (CLAUDE.md; the owner replaced the hero lead after retiring the phrase). Elsewhere the
// construction words are "unibody" and "Zero seams.", scoped to the frame: "No joint to work loose." Never
// "zero weak points" or "nothing to come apart" (absolute durability promises, CLAIMS.md row 8b), never
// "first unibody" (the word is already used in other racket sports, row 3).
// Durability (owner, 2026-10-22): "Built to last five years" always travels with its usage profile: a footnote
// marker (lifetime.mark) links the hero and finale lines to the fine print (lifetime.fine) in the durability
// section. Never "lifetime guarantee", never "sustainable", and never a guarantee for every racket (only
// InviQtus carries one). Until the independent fatigue report exists the testing is promised, never claimed
// as done (CLAIMS.md rows 26 and 28).
// Sealed core (owner, 2026-10-22; CLAIMS.md rows 30 to 34): the carbon shell closes around the whole EVA core
// and lines every hole, so the core never touches the air. It is told once per place: the reveal in the
// unibody chapter (unibody.sealed), the drilled hole that opens a core (holes.body), and the result in
// Durability ("three times longer", only against an open core and only with its fine print, durability.coreFine).
// The seal keeps out sweat, humidity and UV; never heat (the shell does not insulate), never "airtight",
// "waterproof" or "first". "Swiss-made EVA" stays at country level: never the factory, a supplier or a town.

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
  /** Set after the lead in brighter type, with a marker to its usage profile (CLAIMS.md row 26). */
  life: `${lifetime.line}.`,
  ctaNote: `From €410. Refundable. ${site.shipLabel}.`,
};

// In page order: the unibody chapter, Precision, Holes, then Durability.
export const specStrip = [
  { value: "0", unit: "", label: "seams, one unibody shell" },
  { value: "15", unit: "µm", label: "max deviation, any surface" },
  { value: "0", unit: "", label: "drilled holes of 42" },
  { value: "5", unit: "years", label: "design life, twice a week" },
];

export const unibody = {
  edge: {
    eyebrow: "Unibody",
    headline: "Zero seams. No joint to work loose.",
    body: "Face, bridge and handle, one carbon shell. Carbon is strongest when nothing breaks its path. In KINETIQ, nothing does.",
    callouts: ["38.0 mm, one continuous wall", "No frame tube", "One weave, face to edge"],
  },
  section: {
    eyebrow: "Construction",
    headline: "No tube. The shell is the frame.",
    body: "Most padel rackets are built around a carbon tube. In KINETIQ, the faces close around the edge into one shell, and the grams a tube spends on structure go to the sides, where they widen the sweet spot.",
    // Only the frame tube's joints are marked: both constructions bond their faces to a core (CLAIMS.md row 4).
    // The tubular core is open to the air where the drilled hole cuts it; the KINETIQ shell lines the hole
    // and closes around the core (CLAIMS.md rows 30 and 31).
    left: { title: "Tubular racket", parts: ["Frame tube", "Face", "Core", "Face"], glue: "joint", core: "Open core" },
    right: {
      title: "KINETIQ",
      lines: ["One shell. No tube.", "Fibre continuous around the edge", "Balance set in the mould"],
      core: "Sealed core",
    },
    proofs: [
      { title: "One structure.", body: "One carbon shell, face to handle. The skin carries every load, from the rim to the grip." },
      { title: "A wider sweet spot.", body: "Weight moulded in at the sides, exactly where a tube would have spent it on holding the frame together." },
      { title: "Stiffer in twist.", body: "The bridge is part of the same shell. Off-centre shots twist the head less, so the ball leaves where you aimed." },
    ],
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
  headline: "Swiss Made. Down to the core.",
  body: "The two words found on the finest watch dials, now on the throat of your racket. One patented process. One mould. No exceptions.",
  lockup: { value: "100%", label: "Swiss Made" },
  badges: ["100% Swiss Made", "Patented one-mould process"],
};

export const precision = {
  record: { from: 500, to: 15, unit: "µm" },
  recordLine: "A fifth of a human hair.",
  headline: "Measured in microns.",
  body: "15 microns. The furthest any surface may stray from its design. Not on a sample. On every racket. Whatever decides the point, it won't be your racket.",
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
  headline: "42 holes. Not one drilled.",
  body: "Drill a racket and you cut the very fibres that carry the shot, and open its core to the air. So we don't. All 42 holes are formed in the mould, with carbon wrapped around every edge.",
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
  // Point 4 promises the fatigue tests (future tense); it never reads as a test already passed (row 26).
  // "Three times longer" compares the sealed core with the same EVA left open, never with other brands' rackets,
  // and never becomes a racket lifespan ("three to six years"): the five years rest on row 26's own test.
  points: [
    {
      title: "A sealed core, not an open one.",
      body: "In a padel racket, the foam core usually gives out first. Sealed in carbon, ours lasts three times longer than an open core.",
      note: "core" as const,
    },
    { title: "No seam to open.", body: "Face, bridge and handle are one carbon shell. No joint between face and frame to work loose." },
    { title: "No drilled hole to crack.", body: "Cracks often start at a drilled hole. All 42 of ours are moulded, with carbon wrapped around every edge." },
    { title: "Built for five years of play.", body: "Two 90-minute sessions a week for five years: about 780 hours of ball strikes. Independent fatigue tests will prove it before the first racket ships." },
  ],
  graph: {
    typical: "Most padel rackets",
    typicalSpan: { value: "1 to 2", unit: "years" },
    kinetiq: "KINETIQ",
    kinetiqSpan: { value: "5", unit: "years" },
    kinetiqNote: "About 780 hours of ball strikes",
    xAxis: "Years, at two 90-minute sessions a week",
    caption:
      "Illustrative. KINETIQ: design life, ball strikes only, to be verified in independent fatigue tests. Most padel rackets: brand and retailer guidance for recreational play.",
  },
  finePrint: lifetime.fine,
  /**
   * What "three times longer" is measured against, and under what use (CLAIMS.md row 34): a durability claim
   * in terms of usage time, so it never appears without this line.
   */
  coreFine:
    "Against an open core: the same EVA, left open at drilled holes, aged side by side in one accelerated test of ball strikes, humidity, artificial sweat and UV modelled on two 90-minute sessions a week, until each has lost the same share of its rebound. To be verified in independent tests before we ship.",
};

/** The marker on "three times longer" (Durability point 1), linking to durability.coreFine. */
export const coreNote = {
  mark: "\u2020",
  id: "core-fine",
  label: "Three times longer: what it is measured against",
};

/**
 * The footnote marker on the five-year lines that stand apart from their usage profile (hero, finale):
 * it links to the durability fine print, which carries the same marker.
 */
export const lifeNote = {
  mark: lifetime.mark,
  id: "durability-fine",
  label: "Five-year design life: usage profile and terms",
};

export const feel = {
  headline: "Feel the ball. Not the racket.",
  body: "Joints blur every impact. A tube echoes it back. KINETIQ has neither. You feel exactly where you met the ball, the same from edge to centre. Pure contact. Then calm.",
  points: [
    { title: "Nothing blurs the impact.", body: "No joint between face and frame to soften the signal. You feel exactly where the ball met the face." },
    { title: "Nothing echoes it back.", body: "Vibration reflects at every joint. With no joints, the shock spreads through one structure and settles fast." },
    { title: "The same, edge to centre.", body: "Walls held to the same thickness mean the same stiffness everywhere, and weight at the sides widens the sweet spot. Off-centre shots answer like centre shots." },
  ],
  graph: {
    caption: "Illustrative. How vibration fades after impact, edge to centre.",
    glued: "Tubular racket",
    kinetiq: "KINETIQ, unibody",
    settled: "Settled",
  },
};

export const identical = {
  headline: "Buy two. It's the same racket.",
  body: "Within 1.0 g of the reference weight. Within 1.0 mm of its balance point, set inside the mould. Swap rackets mid-match. Your hand will never know.",
  stats: [
    { value: "±1.0", unit: "g", label: "weight, every racket" },
    { value: "±1.0", unit: "mm", label: "balance, set in the mould" },
  ],
  graphCaption: "Illustrative. Distribution against the tolerance window.",
  card: {
    title: "Certificate of measurement",
    tag: "Sample card",
    serial: "KQ-000427",
    rows: [
      ["Feel", "Command"],
      ["Weight", "355.2 g"],
      ["Reference", "355.0 g ±1.0 g"],
      ["Balance", "250.4 mm"],
      ["Thickness", "38.00 mm"],
      ["Max surface deviation", "0.012 mm"],
    ] as [string, string][],
    swiss: "Swiss Made",
    /** The other card of a VanQuish sample set: the second racket, measured on its own (CLAIMS.md row 15). */
    second: {
      serial: "KQ-000428",
      values: { Weight: "354.9 g", Balance: "250.6 mm", "Max surface deviation": "0.011 mm" } as Record<string, string>,
    },
  },
};

export const feelChoice = {
  eyebrow: "Two feels. One standard.",
  headline: "Choose your feel. Then we mould it.",
  feels: [
    { id: "command", name: "Command", sub: "Control", line: "You choose the spot. The ball lands there.", spec: "Soft core, 3K face" },
    { id: "pace", name: "Pace", sub: "Power", line: "You accelerate. It is already there.", spec: "Two-density core, 12K face" },
  ],
};

export const editions = {
  headline: "Three editions. One racket.",
};

export const finale = {
  /** "Five years." carries the footnote marker to the usage profile (CLAIMS.md row 26). */
  headline: "Zero seams. Fifteen microns. Five years.",
  sub: `From €410. ${site.refundLabel} in ${site.shipMonth}.`,
};

export const meta = {
  title: "KINETIQ | The most precise padel racket ever made",
  description:
    "Unibody, in space-grade carbon. Zero seams, no frame tube, a sealed core, held to 15 microns. Designed to last five years at two sessions a week. 100% Swiss Made. Reserve now, fully refundable.",
};
