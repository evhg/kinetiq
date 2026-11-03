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
 * The hero racket with its overgrip ("on", the default) or without it ("off"), so the bare carbon handle shows running
 * out of the head (lib/grip-store.ts, components/chrome/GripToggle.tsx; DESIGN.md "Grip toggle").
 */
export type GripId = "on" | "off";

/** The grip toggle's two labels, in its order: the racket as it ships first, then the bare shell. */
export const gripToggleLabels: Record<GripId, string> = { on: "Grip", off: "Bare" };

export function isGripId(v: string | null | undefined): v is GripId {
  return v === "on" || v === "off";
}

/** The hero opens with the grip on: the racket as it ships, and the only variant the first screen downloads. */
export const DEFAULT_GRIP: GripId = "on";

/**
 * Where the grip choice is kept in the visitor's own browser (localStorage), mirrored in a first-party cookie of the
 * same name exactly as the feel is (FEEL_COOKIE_MAX_AGE, SameSite=Lax, not HttpOnly; src/proxy.ts renews it): a
 * returning visitor who chose "Bare" gets / already rendered without the grip (app/feel/bare, app/feel/<feel>/bare),
 * so the phone's first screen loads the bare stills alone, with no grip-on download first (review, 2026-11-02: LCP
 * 5.4 s without it). The head script mirrors it on html[data-grip] before the first paint. Nothing stores or logs it.
 */
export const GRIP_PREFERENCE_KEY = "kq-grip";

/** The `kq-grip` cookie's value in a Cookie header (or document.cookie), when it names a grip state. */
export function gripFromCookie(header: string | null | undefined): GripId | null {
  const m = header?.match(new RegExp(`(?:^|; *)${GRIP_PREFERENCE_KEY}=([a-z]+)`));
  const v = m?.[1];
  return isGripId(v) ? v : null;
}

export function storedGrip(): GripId | null {
  try {
    const v = window.localStorage.getItem(GRIP_PREFERENCE_KEY);
    return isGripId(v) ? v : null;
  } catch {
    return null;
  }
}

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
 * keeps it in step with localStorage, and src/proxy.ts renews it), so src/proxy.ts can serve a returning visitor the
 * page already rendered in their feel (app/feel/<feel>/): the hero arrives in Pace without downloading Command first.
 * Nothing stores or logs it.
 */
export const FEEL_PREFERENCE_KEY = "kq-feel";
/**
 * One year. Safari (Intelligent Tracking Prevention) holds a cookie written by script to 7 days, so the script writes
 * (a choice, lib/feel-store.ts; the head script restoring a missing or out-of-step cookie) only bridge to the server:
 * src/proxy.ts sends the cookie back with Set-Cookie and a fresh year on every cleared page load that carries it, and
 * renewFeelCookie (lib/feel-store.ts) asks it to right after a script write, so the 7 days never run out between visits.
 */
export const FEEL_COOKIE_MAX_AGE = 31536000;

/**
 * The request that has src/proxy.ts renew `kq-feel` from the server (a HEAD of /, which carries the cookie just
 * written; no body, never cached). Shared by lib/feel-store.ts and the head script (lib/motion-preference.ts).
 */
export const FEEL_COOKIE_RENEW_URL = "/";

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
