import { priceLabel, tiers } from "@/content/lineup";
import type { FeelId, GripId } from "@/content/prefs";

export * from "@/content/prefs";

// A no-break space keeps the month and year on one line wherever they wrap.
const shipMonth = "January\u00a02027";
const fromPriceLabel = `From ${priceLabel(Math.min(...tiers.map((t) => t.priceEur)))}`;

// Commercial facts shared by the landing page, /reserve and /reserved.
export const site = {
  name: "KINETIQ",
  /** The footer's first words, on every page; the root not-found (its tree ships with the gate) shows only these. */
  copyright: "© 2026 KINETIQ.",
  /**
   * The Swiss claim (CLAIMS.md row 10, high risk): one string for the hero eyebrow, the G13 Swiss badge (the /reserve
   * trust badges) and the footer, so a change to it reaches every place at once.
   */
  swissMade: "100% Swiss Made",
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
  /**
   * The feel toggle beside Reserve Now (the hero's, and the header's from 700 px): its group's accessible name. The two
   * options are the feels' names (`feels`). HeaderClient gets both as props, so its client module carries no copy.
   */
  feelToggleLabel: "Feel",
  /**
   * The grip toggle beside the feel toggle in the hero (owner, 2026-11-02: "render images without the grip to show it's
   * a single one piece ... could we have another minimal toggle to remove the grip?"): its group's accessible name.
   * The two options are `gripToggleLabels`.
   */
  gripToggleLabel: "Handle",
  /**
   * The header's view control (owner, 2026-11-03: "when on iphone, I have to scroll all the way back up to change the
   * toggle?"): the button below 1024 px that opens the Feel and Handle choices from anywhere on /, /reserve and
   * /reserved. Its accessible name; HeaderClient gets it as a prop.
   */
  viewToggleLabel: "Feel and handle",
} as const;

/**
 * The grip toggle's two labels, in its order: the racket as it ships first, then Naked (owner, 2026-11-03: "rename bare
 * to Naked which shows 100% carbon"): no overgrip and no cap, the handle and its end the shell's own carbon.
 */
export const gripToggleLabels: Record<GripId, string> = { on: "Grip", off: "Naked" };

/**
 * The two feels. A set is one feel: every racket in it is Command, or every racket is Pace. Apart from the core and
 * the face they are the same racket (CLAIMS.md rows 12 and 16), so `spec` names only those two. The face is also the
 * one you can see: Command is white 3K twill, Pace black 12K (owner, 2026-10-22).
 */
export const feels: Record<FeelId, { name: string; sub: string; spec: string }> = {
  command: { name: "Command", sub: "Control", spec: "Soft core, white 3K face" },
  pace: { name: "Pace", sub: "Power", spec: "Two-density core, black 12K face" },
};

/** The toggle's two labels, in its order (Command first, as the site opens on it). */
export const feelToggleLabels: Record<FeelId, string> = { command: feels.command.name, pace: feels.pace.name };

