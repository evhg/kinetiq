// Commercial facts in one place. Change here, not in components.
export const site = {
  name: "KINETIQ",
  priceEur: 410,
  priceLabel: "€410",
  paymentLabel: "Paid in full today",
  shipLabel: "Ships January 2027",
  refundLabel: "Full refund any time before your racket ships",
  shippingLabel: "Free shipping in Europe",
  ctaLabel: "Reserve yours",
  origin: "St. Gallen, Switzerland",
} as const;

export type ModelId = "command" | "pace";

export const models: Record<
  ModelId,
  {
    name: string;
    line: string;
    feel: string;
    forPlayer: string;
    specs: [label: string, value: string][];
  }
> = {
  command: {
    name: "Command",
    line: "You choose the spot. The ball lands there.",
    feel: "Soft core, 3K carbon face. Control first.",
    forPlayer: "For players who win by placement: the lob, the chiquita, the bandeja.",
    specs: [
      ["Core", "Soft EVA, made on site"],
      ["Face", "3K carbon"],
      ["Weight", "355 g"],
      ["Balance", "25 cm"],
      ["Thickness", "38 mm"],
      ["Holes", "42, moulded"],
    ],
  },
  pace: {
    name: "Pace",
    line: "You accelerate. It is already there.",
    feel: "Two-density core, 12K carbon face. Power on demand.",
    forPlayer: "For players who build pressure: the first volley, the change of tempo, the smash.",
    specs: [
      ["Core", "Two-density EVA, made on site"],
      ["Face", "12K carbon"],
      ["Weight", "355 g"],
      ["Balance", "25 cm"],
      ["Thickness", "38 mm"],
      ["Holes", "42, moulded"],
    ],
  },
};

export function isModelId(value: string | null | undefined): value is ModelId {
  return value === "command" || value === "pace";
}
