import { priceLabel, tiers } from "@/content/lineup";

// A no-break space keeps the month and year on one line wherever they wrap.
const shipMonth = "January\u00a02027";
const fromPriceLabel = `From ${priceLabel(Math.min(...tiers.map((t) => t.priceEur)))}`;

// Commercial facts shared by the landing page, /reserve and /reserved.
export const site = {
  name: "KINETIQ",
  fromPriceLabel,
  shipMonth,
  /** Under the /reserve h1, worded as the KINETIQ include says it: "Ships in January 2027". */
  shipLabel: `Ships in ${shipMonth}`,
  refundLabel: "Fully refundable until we ship",
  /** The price note under a Reserve Now button, as one sentence: "From €410, fully refundable, and shipping in January 2027." */
  priceNote: `${fromPriceLabel}, fully refundable, and shipping in ${shipMonth}.`,
  ctaLabel: "Reserve Now",
  payLabel: "Pay with Card",
  placeLabel: "Place Reservation",
} as const;

export type FeelId = "command" | "pace";

/**
 * The two feels. A set is one feel: every racket in it is Command, or every racket is Pace. Apart from the core and
 * the face they are the same racket (CLAIMS.md rows 12 and 16), so `spec` names only those two. The face is also the
 * one you can see: Command is white 3K twill, Pace black 12K (owner, 2026-10-22).
 */
export const feels: Record<FeelId, { name: string; sub: string; spec: string }> = {
  command: { name: "Command", sub: "Control", spec: "Soft core, white 3K face" },
  pace: { name: "Pace", sub: "Power", spec: "Two-density core, black 12K face" },
};

export function isFeelId(v: string | null | undefined): v is FeelId {
  return v === "command" || v === "pace";
}
