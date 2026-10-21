// Commercial facts shared by the landing page and /reserve.
export const site = {
  name: "KINETIQ",
  fromPriceLabel: "From €410",
  shipLabel: "Ships January 2027",
  refundShort: "Fully refundable",
  refundLabel: "Fully refundable until your racket ships",
  ctaLabel: "Reserve Now",
  payLabel: "Pay with Card",
  placeLabel: "Place Reservation",
} as const;

export type FeelId = "command" | "pace";

export const feels: Record<FeelId, { name: string; sub: string }> = {
  command: { name: "Command", sub: "Control" },
  pace: { name: "Pace", sub: "Power" },
};

export function isFeelId(v: string | null | undefined): v is FeelId {
  return v === "command" || v === "pace";
}
