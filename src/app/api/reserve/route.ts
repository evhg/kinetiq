import { deliveryCountryCodes, invitesOpen, tierById, type Tier } from "@/content/lineup";
import { isFeelId } from "@/content/site";

// "Place Reservation": creates a Stripe PaymentIntent for the chosen tier and returns its
// client secret. The browser then confirms the card in place with Stripe's Payment Element.
// The amount always comes from src/content/lineup.ts, never from the browser.
//
// Env: STRIPE_SECRET_KEY (server) and NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY (browser).
// INVITE_CODES (comma-separated): the Invite Only tier needs one of them. Without codes, or while the
// ambassador extras are unsigned (lineup.ts `ambassador.confirmed`), that tier stays closed (403).
// Without STRIPE_SECRET_KEY the route answers 503 { preview: true }.
//
// Every request pins STRIPE_VERSION, so the account's default API version can never change what
// this route sends. Stripe.js loads the same release (src/lib/stripe-client.ts).
//
// Data minimisation: we send Stripe the name, email and delivery address needed to deliver
// the racket and send the receipt. Nothing is stored on our side.

const STRIPE_VERSION = "2026-09-30.endive";
const STRIPE_API = "https://api.stripe.com/v1";

type Body = {
  tier?: string;
  feel?: string;
  invite?: string;
  name?: string;
  email?: string;
  address?: { line1?: string; line2?: string; postal_code?: string; city?: string; country?: string };
  attempt?: string;
};

type StripeErrorBody = { error?: { type?: string; code?: string; param?: string; request_log_url?: string } };

const clean = (v: unknown, max = 200) => (typeof v === "string" ? v.trim().slice(0, max) : "");
const START_FAILED = "Payment could not start. Nothing was charged. Please try again.";

/** Logs what is needed to find the request in Stripe, never the message (it can echo customer data). */
async function logStripeError(what: string, res: Response) {
  let e: StripeErrorBody["error"];
  try {
    e = ((await res.json()) as StripeErrorBody).error;
  } catch {
    e = undefined;
  }
  console.error(what, res.status, e?.type ?? "", e?.code ?? "", e?.param ?? "", e?.request_log_url ?? "");
}

/**
 * Reserved units of a numbered edition: succeeded plus processing PaymentIntents for the tier.
 * Search can lag by about a minute. Returns null when the count is unavailable.
 */
async function reservedUnits(key: string, tier: Tier): Promise<number | null> {
  const count = async (status: "succeeded" | "processing") => {
    const q = new URLSearchParams({
      query: `status:"${status}" AND metadata["tier"]:"${tier.id}"`,
      limit: "1",
      "expand[]": "total_count",
    });
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

export async function POST(request: Request) {
  let body: Body;
  try {
    body = (await request.json()) as Body;
  } catch {
    return Response.json({ error: "Invalid request." }, { status: 400 });
  }

  const tier = tierById(body.tier);
  if (!tier || !tier.available) {
    return Response.json({ error: "This edition is not available." }, { status: 400 });
  }

  if (!isFeelId(body.feel)) {
    return Response.json({ error: "Choose Command or Pace.", fields: ["feel"] }, { status: 400 });
  }
  const feel = body.feel;

  const name = clean(body.name, 120);
  const email = clean(body.email, 200);
  const a = body.address ?? {};
  const address = {
    line1: clean(a.line1),
    line2: clean(a.line2),
    postal_code: clean(a.postal_code, 20),
    city: clean(a.city, 100),
    country: clean(a.country, 2).toUpperCase(),
  };
  const missing: string[] = [];
  if (name.length < 2) missing.push("name");
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) missing.push("email");
  if (!address.line1) missing.push("address");
  if (!address.postal_code) missing.push("postal code");
  if (!address.city) missing.push("city");
  if (!deliveryCountryCodes.has(address.country)) missing.push("country");
  if (missing.length) {
    return Response.json({ error: `Please check your ${missing.join(", ")}.`, fields: missing }, { status: 400 });
  }

  // Invite Only fails closed: no configured codes means no invitations yet.
  let invite = "";
  if (tier.id === "invite") {
    const codes = (process.env.INVITE_CODES ?? "")
      .split(",")
      .map((c) => c.trim().toUpperCase())
      .filter(Boolean);
    if (!invitesOpen(process.env.INVITE_CODES)) {
      return Response.json({ error: "Invitations open soon.", fields: ["invite"] }, { status: 403 });
    }
    invite = clean(body.invite, 40).toUpperCase();
    if (!codes.includes(invite)) {
      return Response.json({ error: "That invitation code is not valid.", fields: ["invite"] }, { status: 403 });
    }
  }

  const key = process.env.STRIPE_SECRET_KEY;
  if (!key) {
    return Response.json({ preview: true, error: "Reservations open at launch. Nothing was charged." }, { status: 503 });
  }

  // Numbered editions stop at their limit. If Stripe cannot count, sell: an outage must not block sales.
  if (tier.limit !== null) {
    const reserved = await reservedUnits(key, tier);
    if (reserved === null) console.error("Edition cap not checked", tier.id);
    else if (reserved >= tier.limit) {
      return Response.json({ error: `${tier.name} is sold out. Nothing was charged.`, soldOut: true }, { status: 409 });
    }
  }

  const params = new URLSearchParams({
    amount: String(tier.priceEur * 100),
    currency: "eur",
    "allowed_payment_method_types[0]": "card",
    receipt_email: email,
    description: `KINETIQ ${tier.name} reservation`,
    "shipping[name]": name,
    "shipping[address][line1]": address.line1,
    "shipping[address][postal_code]": address.postal_code,
    "shipping[address][city]": address.city,
    "shipping[address][country]": address.country,
    "metadata[tier]": tier.id,
    "metadata[feel]": feel,
    "metadata[rackets]": String(tier.rackets),
  });
  if (address.line2) params.set("shipping[address][line2]", address.line2);
  if (invite) params.set("metadata[invite]", invite);

  const headers: Record<string, string> = {
    Authorization: `Bearer ${key}`,
    "Content-Type": "application/x-www-form-urlencoded",
    "Stripe-Version": STRIPE_VERSION,
  };
  // Same attempt and same details → same PaymentIntent, so a double click never charges twice.
  // Edited details make a new key (Stripe rejects a reused key with different parameters); the
  // browser checks its previous PaymentIntent before it asks for a new one.
  const attempt = typeof body.attempt === "string" && /^[A-Za-z0-9-]{8,64}$/.test(body.attempt) ? body.attempt : "";
  if (attempt) {
    const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(params.toString()));
    const hash = Array.from(new Uint8Array(digest).slice(0, 8), (b) => b.toString(16).padStart(2, "0")).join("");
    headers["Idempotency-Key"] = `kq-${tier.id}-${attempt}-${hash}`;
  }

  try {
    const res = await fetch(`${STRIPE_API}/payment_intents`, { method: "POST", headers, body: params, cache: "no-store" });
    if (!res.ok) {
      await logStripeError("Stripe PaymentIntent failed", res);
      return Response.json({ error: START_FAILED }, { status: 502 });
    }
    const pi = (await res.json()) as { client_secret?: string; id?: string };
    if (!pi.client_secret) return Response.json({ error: START_FAILED }, { status: 502 });
    return Response.json({ clientSecret: pi.client_secret, id: pi.id });
  } catch (err) {
    console.error("Stripe PaymentIntent failed", err instanceof Error ? err.name : "unknown");
    return Response.json({ error: START_FAILED }, { status: 502 });
  }
}
