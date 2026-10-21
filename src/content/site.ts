// Commercial facts in one place. Change here, not in components.
// Editions, prices and edition limits are owner-to-confirm (see CLAIMS.md #17–#20).
export const site = {
  name: "KINETIQ",
  fromPriceLabel: "From €410",
  shipLabel: "Ships January 2027",
  refundShort: "Fully refundable",
  refundLabel: "Fully refundable until your racket ships",
  shippingLabel: "Free delivery in Europe, duties included",
  ctaLabel: "Reserve Now",
  payLabel: "Pay by Card",
  origin: "St. Gallen, Switzerland",
} as const;

export type ModelId = "command" | "pace";
export type EditionId = "kinetiq" | "founders" | "atelier";

export const models: Record<ModelId, { name: string; line: string; feel: string }> = {
  command: {
    name: "Command",
    line: "You choose the spot. The ball lands there.",
    feel: "Soft core, 3K carbon face. Control first.",
  },
  pace: {
    name: "Pace",
    line: "You accelerate. It is already there.",
    feel: "Two-density core, 12K carbon face. Power on demand.",
  },
};

export const editions: Record<
  EditionId,
  {
    name: string;
    priceEur: number;
    priceLabel: string;
    /** Total made, or null for the open edition. */
    limit: number | null;
    tagline: string;
    includes: string[];
    available: boolean;
  }
> = {
  kinetiq: {
    name: "KINETIQ",
    priceEur: 410,
    priceLabel: "€410",
    limit: null,
    tagline: "The one-piece racket.",
    includes: ["From the first production run", "Serial number and its own measurement card"],
    available: true,
  },
  founders: {
    name: "Founders Series",
    priceEur: 990,
    priceLabel: "€990",
    limit: 500,
    tagline: "Numbered 001 to 500. Never made again.",
    includes: [
      "Your number laser-marked on the throat",
      "Among the first rackets out of the mould",
      "Measurement card signed in St. Gallen",
      "Ships first, January 2027",
    ],
    available: true,
  },
  atelier: {
    name: "Atelier Edition",
    priceEur: 2900,
    priceLabel: "€2,900",
    limit: 50,
    tagline: "Fifty rackets. One for each name.",
    includes: [
      "Numbered 01 to 50, with your name on the measurement card",
      "A film of your racket leaving the mould",
      "Hand-finished and presented in a fitted case",
      "Everything in the Founders Series",
    ],
    available: true,
  },
};

export const editionOrder: EditionId[] = ["kinetiq", "founders", "atelier"];

export function isModelId(value: string | null | undefined): value is ModelId {
  return value === "command" || value === "pace";
}

export function isEditionId(value: string | null | undefined): value is EditionId {
  return value === "kinetiq" || value === "founders" || value === "atelier";
}
