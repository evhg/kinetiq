/**
 * The NDA gate's cookie (owner, 2026-10-22): investors declare that they have signed the NDA and give an email
 * before anything else on the site is served. src/proxy.ts checks the cookie on every request, POST /api/nda sets it.
 *
 * Contract (scripts/nda-cookie.mjs builds the same cookie for the harness and review tools):
 *   name   kq_nda
 *   value  base64url of JSON {"email": "<address>", "at": "<ISO date>"}
 *   flags  HttpOnly, SameSite=Lax, Secure on https, Path=/, Max-Age 365 days
 * A visitor is cleared when the value decodes and its email looks valid. It is a declaration, not a login:
 * nothing is stored on the server and the email is never logged.
 */
export const NDA_COOKIE = "kq_nda";
export const NDA_MAX_AGE = 365 * 24 * 60 * 60;
/** The gate route. The proxy rewrites every gated page request to it, so the address bar keeps the typed URL. */
export const NDA_ROUTE = "/nda";
/**
 * sessionStorage key the gate sets (to Date.now()) just before it reloads the page. Within ARRIVE_MS of it, the page
 * that loads either is the real one (the arrival veil lifts, src/lib/motion-preference.ts) or is the gate again (the
 * browser refused the cookie, NdaGate says so).
 */
export const NDA_TRIED_KEY = "kq_nda_tried";
export const NDA_ARRIVE_MS = 15_000;

const MAX_EMAIL = 254;
const MAX_COOKIE = 1024;

/**
 * A plain address check: one @, a local part of the usual characters (no leading, trailing or double dots) and a
 * domain of at least two labels whose last label is letters (or a punycode TLD).
 */
const LOCAL = /^[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+)*$/;
const LABEL = /^[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?$/;
const TLD = /^(?:[A-Za-z]{2,63}|xn--[A-Za-z0-9-]{1,59})$/;

export function isEmail(value: unknown): value is string {
  if (typeof value !== "string" || value.length > MAX_EMAIL) return false;
  const at = value.lastIndexOf("@");
  if (at < 1 || value.indexOf("@") !== at) return false;
  const local = value.slice(0, at);
  const labels = value.slice(at + 1).split(".");
  return (
    local.length <= 64 &&
    LOCAL.test(local) &&
    labels.length >= 2 &&
    labels.every((l) => LABEL.test(l)) &&
    TLD.test(labels[labels.length - 1])
  );
}

/** Trims what a person typed; the address itself is kept as entered. */
export function normaliseEmail(value: unknown): string {
  return typeof value === "string" ? value.trim() : "";
}

function toBase64Url(text: string): string {
  const bytes = new TextEncoder().encode(text);
  let bin = "";
  for (const b of bytes) bin += String.fromCharCode(b);
  return btoa(bin).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

function fromBase64Url(value: string): string | null {
  if (!/^[A-Za-z0-9_-]+$/.test(value)) return null;
  try {
    const b64 = value.replace(/-/g, "+").replace(/_/g, "/");
    const bin = atob(b64 + "=".repeat((4 - (b64.length % 4)) % 4));
    return new TextDecoder("utf-8", { fatal: true }).decode(Uint8Array.from(bin, (c) => c.charCodeAt(0)));
  } catch {
    return null;
  }
}

/** The cookie value for a declared email. */
export function encodeNda(email: string, at: Date = new Date()): string {
  return toBase64Url(JSON.stringify({ email, at: at.toISOString() }));
}

/** The declared email, or null when the cookie is missing, malformed or carries no valid address. */
export function decodeNda(value: string | undefined | null): string | null {
  if (!value || value.length > MAX_COOKIE) return null;
  const json = fromBase64Url(value);
  if (!json) return null;
  try {
    const data: unknown = JSON.parse(json);
    if (!data || typeof data !== "object") return null;
    const email = (data as { email?: unknown }).email;
    return isEmail(email) ? email : null;
  } catch {
    return null;
  }
}

export function ndaCleared(value: string | undefined | null): boolean {
  return decodeNda(value) !== null;
}
