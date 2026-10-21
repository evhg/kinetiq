import { deliveryCountryCodes, tierById } from "@/content/lineup";
import { isFeelId } from "@/content/site";

// "Place Reservation": creates a Stripe PaymentIntent for the chosen tier and returns its
// client secret. The browser then confirms the card in place with Stripe's Payment Element.
// The amount always comes from src/content/lineup.ts, never from the browser.
//
// Env: STRIPE_SECRET_KEY (server) and NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY (browser).
// Optional INVITE_CODES (comma-separated): when set, the Invite Only tier needs one of them.
// Without STRIPE_SECRET_KEY the route answers 503 { preview: true }.
//
// Data minimisation: we send Stripe the name, email and delivery address needed to deliver
// the racket and send the receipt. Nothing is stored on our side.

type Body = {
  tier?: string;
  feel?: string;
  invite?: string;
  name?: string;
  email?: string;
  address?: { line1?: string; line2?: string; postal_code?: string; city?: string; country?: string };
  attempt?: string;
};

const clean = (v: unknown, max = 200) => (typeof v === "string" ? v.trim().slice(0, max) : "");

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

  if (tier.id === "invite") {
    const codes = (process.env.INVITE_CODES ?? "")
      .split(",")
      .map((c) => c.trim().toUpperCase())
      .filter(Boolean);
    if (codes.length && !codes.includes(clean(body.invite, 40).toUpperCase())) {
      return Response.json({ error: "That invitation code is not valid.", fields: ["invite"] }, { status: 403 });
    }
  }

  const key = process.env.STRIPE_SECRET_KEY;
  if (!key) {
    return Response.json({ preview: true, error: "Reservations open at launch. Nothing was charged." }, { status: 503 });
  }

  const params = new URLSearchParams({
    amount: String(tier.priceEur * 100),
    currency: "eur",
    "payment_method_types[0]": "card",
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

  const headers: Record<string, string> = {
    Authorization: `Bearer ${key}`,
    "Content-Type": "application/x-www-form-urlencoded",
  };
  // Same attempt and same details → same PaymentIntent, so a double click never charges twice.
  // Edited details make a new key (Stripe rejects a reused key with different parameters).
  const attempt = clean(body.attempt, 64);
  if (attempt) {
    const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(params.toString()));
    const hash = Array.from(new Uint8Array(digest).slice(0, 8), (b) => b.toString(16).padStart(2, "0")).join("");
    headers["Idempotency-Key"] = `kq-${tier.id}-${attempt}-${hash}`;
  }

  const res = await fetch("https://api.stripe.com/v1/payment_intents", { method: "POST", headers, body: params });
  if (!res.ok) {
    console.error("Stripe PaymentIntent failed", res.status, await res.text());
    return Response.json({ error: "Payment could not start. Nothing was charged. Please try again." }, { status: 502 });
  }
  const pi = (await res.json()) as { client_secret?: string; id?: string };
  return Response.json({ clientSecret: pi.client_secret, id: pi.id });
}
