// Every marketing claim on the site, in one place.
// Status is tracked in CLAIMS.md. Nothing here is verified yet (owner decision,
// 2026-10-21: claim first, verify before launch). The preview banner stays on
// until NEXT_PUBLIC_LAUNCHED=true, which should only be set once CLAIMS.md is cleared.
export const claims = {
  // U+2011 non-breaking hyphen keeps "one‑piece" on one line.
  worldFirstOnePiece: "The world\u2019s first one\u2011piece padel racket.",
  onePieceDetail: "Face, frame, throat and core leave the mould as one part. Add the grip and it is done.",
  record: {
    value: 15,
    unit: "µm",
    headline: "The most precise padel racket ever made.",
    detail: "Every surface within 15 microns of the design. A human hair is about 70.",
  },
  worldFirstMouldedHoles: "The world\u2019s first padel racket with moulded holes.",
  mouldedHolesDetail: "42 holes formed in the mould, with fibre wrapped around every edge. Zero drilled. Zero cut fibres.",
  swissMade: "100% Swiss Made.",
  swissDetail: "Moulded, measured and finished in St. Gallen, by a carbon workshop that already builds full\u2011carbon golf clubs.",
  worldFirstSwiss: "The world\u2019s first 100% Swiss Made padel racket.",
  patented: "Patented one-mould process.",
  identical: {
    headline: "Buy two. They are the same racket.",
    detail: "Same mould, same foam, same fibre path. Every racket within ±1 g and ±1 mm of the reference.",
    weightTolerance: "±1 g",
    balanceTolerance: "±1 mm",
  },
  balanceMoulded: "Balance is set inside the mould, not adjusted afterwards.",
  measurementCard: "Every racket ships with its serial number and its own measurements.",
  feel: [
    {
      title: "Nothing glued. Nothing lost.",
      body: "A glued racket sends every impact through soft glue lines that blur the signal. One continuous piece of carbon carries it straight to your hand. You feel exactly where the ball met the face.",
    },
    {
      title: "Calm in the hand.",
      body: "Vibration bounces back at every joint, which is why some rackets buzz. With no joints to bounce off, the shock spreads evenly through one structure and fades faster. Easier on your arm, set after set.",
    },
    {
      title: "The same answer, every shot.",
      body: "Walls held to the same thickness everywhere mean the same stiffness everywhere. The racket answers the same way at the edge as in the centre, so you can trust the shot you meant to play.",
    },
  ],
} as const;
