import { NextResponse } from "next/server";
import { isModelId, site } from "@/content/site";

// Creates a Stripe Checkout Session and redirects to it.
// Until STRIPE_SECRET_KEY and both price IDs are set (Vercel → Settings →
// Environment Variables), it redirects back to /checkout in preview mode.
// Uses Stripe's REST API directly: no SDK dependency.

const EU_EEA_CH_UK = [
  "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GR", "HU", "IE", "IT", "LV", "LT", "LU",
  "MT", "NL", "PL", "PT", "RO", "SK", "SI", "ES", "SE", "IS", "LI", "NO", "CH", "GB", "MC", "AD", "SM",
];

export async function POST(request: Request) {
  const origin = process.env.NEXT_PUBLIC_SITE_URL || new URL(request.url).origin;
  const form = await request.formData();
  const model = String(form.get("model") ?? "");
  if (!isModelId(model)) {
    return NextResponse.redirect(new URL("/checkout", origin), 303);
  }

  const key = process.env.STRIPE_SECRET_KEY;
  const price = model === "command" ? process.env.STRIPE_PRICE_COMMAND : process.env.STRIPE_PRICE_PACE;
  if (!key || !price) {
    return NextResponse.redirect(new URL(`/checkout?model=${model}&status=preview`, origin), 303);
  }

  const body = new URLSearchParams({
    mode: "payment",
    "line_items[0][price]": price,
    "line_items[0][quantity]": "1",
    success_url: `${origin}/reserved?session_id={CHECKOUT_SESSION_ID}`,
    cancel_url: `${origin}/checkout?model=${model}`,
    "metadata[model]": model,
    "metadata[ships]": site.shipLabel,
    billing_address_collection: "required",
    "phone_number_collection[enabled]": "true",
  });
  EU_EEA_CH_UK.forEach((c, i) => body.append(`shipping_address_collection[allowed_countries][${i}]`, c));

  const res = await fetch("https://api.stripe.com/v1/checkout/sessions", {
    method: "POST",
    headers: { Authorization: `Bearer ${key}`, "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });
  if (!res.ok) {
    console.error("Stripe checkout session failed", res.status, await res.text());
    return NextResponse.redirect(new URL(`/checkout?model=${model}&status=error`, origin), 303);
  }
  const session = (await res.json()) as { url?: string };
  return NextResponse.redirect(session.url ?? new URL(`/checkout?model=${model}&status=error`, origin), 303);
}
