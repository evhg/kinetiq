/**
 * The visitor's Feel and Handle preferences: ids, storage keys, cookie parsing and defaults, and nothing else. No copy,
 * no prices, no imports: the header's client modules (lib/feel-store.ts, lib/grip-store.ts, HeaderClient and its
 * toggles) import from here, and the root not-found's tree ships with every page, the NDA gate included, so whatever
 * this module pulls in reaches /nda. Words (the toggles' labels, the feels' names) stay in src/content/site.ts, which
 * re-exports everything here for its other readers.
 */

/**
 * The hero racket with its overgrip ("on", the default) or without it ("off"), so the bare carbon handle shows running
 * out of the head (lib/grip-store.ts, components/chrome/GripToggle.tsx; DESIGN.md "Grip toggle").
 */
export type GripId = "on" | "off";

export function isGripId(v: string | null | undefined): v is GripId {
  return v === "on" || v === "off";
}

/** The hero opens with the grip on: the racket as it ships, and the only variant the first screen downloads. */
export const DEFAULT_GRIP: GripId = "on";

/**
 * Where the grip choice is kept in the visitor's own browser (localStorage), mirrored in a first-party cookie of the
 * same name exactly as the feel is (FEEL_COOKIE_MAX_AGE, SameSite=Lax, not HttpOnly; src/proxy.ts renews it): a
 * returning visitor who chose "Naked" gets / already rendered without the grip (app/feel/bare, app/feel/<feel>/bare),
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
