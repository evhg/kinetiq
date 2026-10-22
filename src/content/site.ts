import { priceLabel, tiers } from "@/content/lineup";

// A no-break space keeps the month and year on one line wherever they wrap.
const shipMonth = "January\u00a02027";

// Commercial facts shared by the landing page and /reserve.
export const site = {
  name: "KINETIQ",
  fromPriceLabel: `From ${priceLabel(Math.min(...tiers.map((t) => t.priceEur)))}`,
  shipMonth,
  shipLabel: `Ships ${shipMonth}`,
  refundLabel: "Fully refundable until we ship",
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
