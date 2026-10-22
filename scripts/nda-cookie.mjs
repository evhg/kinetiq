// The NDA gate's cookie for scripts (contract in src/lib/nda.ts): with it, a script gets past src/proxy.ts and sees
// the real site; without it, every page is the gate and every asset or API answers 403.
//
//   import { ndaCookie } from "./nda-cookie.mjs";
//   const context = await browser.newContext();
//   await context.addCookies([ndaCookie(baseUrl)]);   // before the first navigation
//
//   node scripts/nda-cookie.mjs                     prints the Cookie header, e.g. for curl:
//   curl -H "Cookie: $(node scripts/nda-cookie.mjs)" http://localhost:3100/
//
// The address is a reserved .invalid domain, so it can never be a real person's email.

export const NDA_COOKIE = "kq_nda";
export const NDA_SCRIPT_EMAIL = "harness@kinetiq.invalid";
const MAX_AGE = 365 * 24 * 60 * 60;

/** The cookie value: base64url of JSON {"email", "at"}. */
export function ndaValue(email = NDA_SCRIPT_EMAIL, at = new Date()) {
  return Buffer.from(JSON.stringify({ email, at: at.toISOString() })).toString("base64url");
}

/** A Playwright cookie for the site at baseUrl (any URL on it): HttpOnly, SameSite=Lax, Secure on https, Path=/. */
export function ndaCookie(baseUrl, email = NDA_SCRIPT_EMAIL) {
  const url = new URL(baseUrl);
  return {
    name: NDA_COOKIE,
    value: ndaValue(email),
    domain: url.hostname,
    path: "/",
    httpOnly: true,
    secure: url.protocol === "https:",
    sameSite: "Lax",
    expires: Math.floor(Date.now() / 1000) + MAX_AGE,
  };
}

/** The Cookie request header (fetch, curl). */
export function ndaHeader(email = NDA_SCRIPT_EMAIL) {
  return `${NDA_COOKIE}=${ndaValue(email)}`;
}

if (import.meta.url === `file://${process.argv[1]}`) process.stdout.write(ndaHeader());
