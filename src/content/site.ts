import { priceLabel, tiers } from "@/content/lineup";

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

/** The toggle's two labels, in its order (Command first, as the site opens on it). */
export const feelToggleLabels: Record<FeelId, string> = { command: feels.command.name, pace: feels.pace.name };

export function isFeelId(v: string | null | undefined): v is FeelId {
  return v === "command" || v === "pace";
}

/** The feel the site opens on (owner, 2026-10-23: Command), wherever no choice has been made yet. */
export const DEFAULT_FEEL: FeelId = "command";

/**
 * Where a site-wide feel choice is kept in the visitor's own browser (a per-visitor convenience, never recorded by us).
 * The feel toggles beside Reserve Now and the /reserve feel picker write it (lib/feel-store.ts), the head script mirrors
 * it on html[data-feel] before the first paint, and /reserve reads it when the link carries no ?feel=
 * (ReserveExperience). Reads and writes fail quietly (private windows, blocked storage).
 * A first-party cookie of the same name mirrors it (FEEL_COOKIE_MAX_AGE, SameSite=Lax, not HttpOnly: the head script
 * keeps it in step with localStorage), so src/proxy.ts can serve a returning visitor the page already rendered in their
 * feel (app/feel/<feel>/): the hero arrives in Pace without downloading Command first. Nothing stores or logs it.
 */
export const FEEL_PREFERENCE_KEY = "kq-feel";
/** One year, renewed on every choice and on every page load that finds the cookie missing or out of step. */
export const FEEL_COOKIE_MAX_AGE = 31536000;

/** The `kq-feel` cookie's value in a Cookie header (or document.cookie), when it names a feel. */
export function feelFromCookie(header: string | null | undefined): FeelId | null {
  const m = header?.match(new RegExp(`(?:^|; *)${FEEL_PREFERENCE_KEY}=([a-z]+)`));
  const v = m?.[1];
  return isFeelId(v) ? v : null;
}

export function storedFeel(): FeelId | null {
  try {
    const v = window.localStorage.getItem(FEEL_PREFERENCE_KEY);
    return isFeelId(v) ? v : null;
  } catch {
    return null;
  }
}
