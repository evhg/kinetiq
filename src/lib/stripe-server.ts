// Server-only helpers shared by /api/reserve and /api/invite: the pinned Stripe API version, error logging
// that never echoes customer data, the PaymentIntent counter behind the edition caps and the single-use
// invitation check, and the invitation codes themselves.
//
// Every request pins STRIPE_VERSION, so the account's default API version can never change what these
// routes send. Stripe.js loads the same release (src/lib/stripe-client.ts).

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

/** A code as the buyer typed it, normalised; "" when it cannot be a code. */
export function cleanCode(v: unknown): string {
  const code = typeof v === "string" ? v.trim().toUpperCase() : "";
  return CODE.test(code) ? code : "";
}

/** The configured invitation codes (INVITE_CODES, comma-separated), normalised the same way. */
export function inviteCodes(): string[] {
  return (process.env.INVITE_CODES ?? "")
    .split(",")
    .map(cleanCode)
    .filter(Boolean);
}

/** Paid or settling reservations already made with this invitation code (codes are single-use); null when unknown. */
export function inviteUses(key: string, code: string): Promise<number | null> {
  return countPaid(key, `metadata["invite"]:"${code}"`);
}
