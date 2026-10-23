// Server-only helpers shared by /api/reserve, /api/invite and /reserve: the pinned Stripe API version, error
// logging that never echoes customer data, the PaymentIntent counter behind the edition caps and the single-use
// invitation check, the invitation codes themselves, and whether One of Ten can open at all (invitationsOpen).
//
// Every request pins STRIPE_VERSION, so the account's default API version can never change what these
// routes send. Stripe.js loads the same release (src/lib/stripe-client.ts).

import { invitesOpen } from "@/content/lineup";

export const STRIPE_VERSION = "2026-09-30.endive";
export const STRIPE_API = "https://api.stripe.com/v1";

type StripeErrorBody = { error?: { type?: string; code?: string; param?: string; request_log_url?: string } };

/** Logs what is needed to find the request in Stripe, never the message (it can echo customer data). */
export async function logStripeError(what: string, res: Response) {
  let e: StripeErrorBody["error"];
  try {
    e = ((await res.json()) as StripeErrorBody).error;
  } catch {
    e = undefined;
  }
  console.error(what, res.status, e?.type ?? "", e?.code ?? "", e?.param ?? "", e?.request_log_url ?? "");
}

/**
 * Succeeded plus processing PaymentIntents that match a search clause, e.g. metadata["tier"]:"limited".
 * Stripe's search can lag by about a minute. Returns null when Stripe cannot count.
 */
export async function countPaid(key: string, clause: string): Promise<number | null> {
  const count = async (status: "succeeded" | "processing") => {
    const q = new URLSearchParams({ query: `status:"${status}" AND ${clause}`, limit: "1", "expand[]": "total_count" });
    const res = await fetch(`${STRIPE_API}/payment_intents/search?${q}`, {
      headers: { Authorization: `Bearer ${key}`, "Stripe-Version": STRIPE_VERSION },
      signal: AbortSignal.timeout(5000),
      cache: "no-store",
    });
    if (!res.ok) {
      await logStripeError("Stripe search failed", res);
      return null;
    }
    const data = (await res.json()) as { total_count?: number };
    return typeof data.total_count === "number" ? data.total_count : null;
  };
  try {
    const [done, settling] = await Promise.all([count("succeeded"), count("processing")]);
    return done === null || settling === null ? null : done + settling;
  } catch (err) {
    console.error("Stripe search failed", err instanceof Error ? err.name : "unknown");
    return null;
  }
}

/** Invitation codes are letters, digits and hyphens only (a code goes into a Stripe search query). */
const CODE = /^[A-Z0-9-]{4,40}$/;

/**
 * The shortest configured code honoured. /api/invite answers yes or no to anyone (the NDA cookie is self-issued), so a
 * short or patterned code could be guessed and a single-use invitation spent; a shorter one is ignored (fails closed).
 */
const MIN_CODE_LENGTH = 12;
let warnedShort = false;

/** A code as the buyer typed it, normalised; "" when it cannot be a code. */
export function cleanCode(v: unknown): string {
  const code = typeof v === "string" ? v.trim().toUpperCase() : "";
  return CODE.test(code) ? code : "";
}

/**
 * The configured invitation codes (INVITE_CODES, comma-separated), normalised the same way, of 12 characters or more.
 * Shorter ones are ignored, with one warning per server instance (never the codes themselves).
 */
export function inviteCodes(): string[] {
  const all = (process.env.INVITE_CODES ?? "").split(",").map(cleanCode).filter(Boolean);
  const ok = all.filter((c) => c.length >= MIN_CODE_LENGTH);
  if (ok.length < all.length && !warnedShort) {
    warnedShort = true;
    const n = all.length - ok.length;
    const what = n === 1 ? "1 invitation code is" : `${n} invitation codes are`;
    console.warn(`[invite] ${what} ignored: shorter than ${MIN_CODE_LENGTH} characters`);
  }
  return ok;
}

/**
 * Paid or settling reservations already made with this invitation code (codes are single-use); null when unknown.
 * Search lags by about a minute and counts only succeeded and processing payments, so this alone cannot stop two
 * payments started with one code at the same time (see INVITE_ONE_USE_ENFORCED).
 */
export function inviteUses(key: string, code: string): Promise<number | null> {
  return countPaid(key, `metadata["invite"]:"${code}"`);
}

/**
 * Whether "a code reserves one set" and the cap of ten sets hold even for payments started at the same moment. Until
 * this is true, One of Ten takes no payment whatever INVITE_TERMS_READY and INVITE_CODES say (invitationsOpen).
 *
 * What must exist before it is set to true, in /api/reserve, for One of Ten only, before and after the PaymentIntent
 * is created (CLAIMS.md row 20):
 * 1. List the last hour's PaymentIntents with the list endpoint, which is current where Search lags
 *    (GET /v1/payment_intents?created[gte]=<now - 3600>&limit=100, following starting_after while has_more, up to
 *    10 pages; if a page fails or more remain, refuse with 503 and charge nothing).
 * 2. Among those with metadata.invite equal to the code: any succeeded or processing means the code is used (409).
 *    Cancel every other one still payable (requires_payment_method, requires_confirmation or requires_action) with
 *    POST /v1/payment_intents/<id>/cancel, so only the newest attempt for a code can be paid.
 * 3. The cap: succeeded and processing PaymentIntents with metadata.tier "invite" from that listing, plus Search's
 *    count of those created before it (created<now - 3600), plus offSite, must stay under 10.
 * 4. After creating the new PaymentIntent, list again and repeat 2 and 3 with it included: if another payable one for
 *    the code is newer (by created, then by id), or the code or the cap is now used, cancel the new one and refuse
 *    (409), so two requests that passed step 1 together cannot both be paid.
 * Then add a test that two concurrent reservations with one code leave exactly one payable PaymentIntent.
 */
export const INVITE_ONE_USE_ENFORCED = false;

/**
 * Whether One of Ten can be reserved now: the paperwork is ready (INVITE_TERMS_READY), at least one valid code is
 * configured (12 characters or more), and the one-use check holds (INVITE_ONE_USE_ENFORCED). Otherwise both APIs
 * refuse it and /reserve shows "Invitations open soon."
 */
export function invitationsOpen(): boolean {
  return INVITE_ONE_USE_ENFORCED && invitesOpen(inviteCodes().join(","));
}
