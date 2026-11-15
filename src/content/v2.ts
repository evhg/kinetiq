/**
 * The words of /v2 (owner, 2026-11-13: "a second version of the landing page" with Apple-style scroll effects; the
 * landing page at / stays as it is). /v2 reuses every section of / and adds seven effects between them; only the
 * words those effects carry are here. Kept short and claim-light: each sequence's steps describe what the frames show
 * (the factory's own process, its guidelines of 2026-11-12: a foam core, dry carbon, resin injected under vacuum), and
 * nothing here says how the holes are made (open with the factory). A preview: linked from nowhere, never indexed.
 */
export const v2 = {
  /** 6: the giant word, the letters filled with the carbon face, the camera passing through its O. */
  typeZoom: { word: "UNIBODY", spoken: "Unibody", lead: "Face, bridge and handle, in one carbon shell." },

  /** 3: the exploded layers, after Unibody. */
  explode: {
    id: "v2-layers",
    eyebrow: "Construction",
    headline: "Layer on layer, one shell.",
    steps: ["Carbon plies, each laid in its own direction.", "The core between them.", "Closed into one shell."],
    alt: "A KINETIQ racket separating into its layers, carbon plies on each side of the core, and closing again into one shell.",
  },

  /** 1: the racket made, step by step, before Born whole. */
  assemble: {
    id: "v2-made",
    eyebrow: "Born whole",
    headline: "Made whole, in one mould.",
    steps: ["The foam core.", "Carbon, laid on dry.", "Resin, injected under vacuum.", "Out of the mould as one shell."],
    alt: "A KINETIQ racket being made: the foam core, the dry carbon laid over it, the resin flowing through it, and the finished racket.",
  },

  /** 2: from the whole face into one hole, before Holes. */
  dive: {
    id: "v2-closer",
    eyebrow: "Closer",
    headline: "Look closer.",
    steps: ["The face.", "The weave.", "One hole."],
    alt: "The camera moves in from the whole face of a KINETIQ to a single hole in its carbon.",
  },

  /** 4: one racket, its feel changing under a sweep of light, before Choose your feel. */
  feelWipe: {
    id: "v2-feels",
    eyebrow: "Two feels",
    headline: "Command or Pace.",
    alt: "The same KINETIQ racket in its two feels: white Command carbon on one side of a moving line of light, black Pace carbon on the other.",
  },

  /** 7: the details, sideways, after Durability. */
  rail: {
    id: "v2-details",
    eyebrow: "The details",
    headline: "Take a closer look.",
    hint: "Swipe for more",
  },
};
