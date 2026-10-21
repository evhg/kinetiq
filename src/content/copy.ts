// All landing-page words, in one place. Every claim here has a row in CLAIMS.md.
// House rules: weights always carry a decimal (355.0 g, ±1.0 g), never a range.
// No middle-dot strings, no workshop, town or supply-chain talk.
// Banned (owner, 2026-10-21): "The world's first one-piece padel racket." as a headline, and any line like
// "Moulded, measured and finished in [town], by a carbon workshop that already builds full-carbon golf clubs."

export const hero = {
  eyebrow: "100% Swiss Made",
  headline: "The most precise racket ever made.",
  lead: "One piece of space-grade carbon. No tube, no joints. Held to 15 microns. Every racket plays exactly the same.",
  ctaNote: "From €410. Fully refundable. Ships January 2027.",
};

export const specStrip = [
  { value: "1", unit: "", label: "piece, from a single mould" },
  { value: "15", unit: "µm", label: "maximum deviation, any surface" },
  { value: "0", unit: "", label: "drilled holes of 42" },
  { value: "±1.0", unit: "g", label: "every racket, against the reference" },
];

export const onePiece = {
  edge: {
    headline: "Carbon, never interrupted.",
    body: "Carbon is strongest when nothing breaks its path. In KINETIQ, nothing does. No frame tube. No joint. No cut fibre. Every shot travels through one continuous shell.",
    callouts: ["38.0 mm, one continuous wall", "No seam. No tube. No joint.", "One weave, face to edge"],
  },
  section: {
    eyebrow: "No frame tube",
    headline: "No tube. The shell is the frame.",
    body: "Most padel rackets are built around a carbon tube. KINETIQ has no frame tube. Its faces close around the edge into one shell, and the grams a tube spends on structure go to the sides, where they widen the sweet spot.",
    left: { title: "Tubular racket", parts: ["Frame tube", "Face", "Core", "Face"], glue: "joint" },
    right: { title: "KINETIQ", lines: ["One shell. No tube.", "Fibre continuous around the edge", "Balance set in the mould"] },
    proofs: [
      { title: "No frame tube.", body: "One carbon shell, face to handle. The skin carries every load, so the whole racket works as one structure." },
      { title: "A wider sweet spot.", body: "Weight moulded in at the sides, exactly where a tube would have spent it on holding the frame together." },
      { title: "Stiffer in twist.", body: "The bridge is part of the same shell. Off-centre shots twist the head less, so the ball leaves where you aimed." },
    ],
  },
};

export const bornWhole = {
  eyebrow: "Patented one-mould process",
  headline: "Swiss Made. Down to the core.",
  body: "The two words found on the finest watch dials, now on the throat of your racket. One patented process, performed nowhere else on earth.",
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
  body: "Drill a racket and you cut the very fibres that carry the shot. So we don't. All 42 holes are formed in the mould, with carbon wrapped around every edge.",
  stats: [
    { value: "42", label: "holes, moulded" },
    { value: "0", label: "drilled" },
    { value: "0", label: "fibres cut" },
  ],
  pair: { drilled: "Drilled: every fibre at the bore is cut.", moulded: "Moulded: every fibre flows around it." },
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
    kinetiq: "KINETIQ, one piece",
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
  headline: "One piece. Fifteen microns. Yours.",
  sub: "From €410. Fully refundable until your racket ships in January 2027.",
};

export const meta = {
  title: "KINETIQ | The most precise padel racket ever made",
  description:
    "One piece of space-grade carbon. No tube, no joints, held to 15 microns. Every racket plays exactly the same. 100% Swiss Made. Reserve now, fully refundable.",
};
