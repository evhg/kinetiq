import { NextResponse } from "next/server";
import { editions, isEditionId, isModelId, models, site } from "@/content/site";

// "Pay by Card": creates a Stripe Checkout Session and redirects to it.
// Only STRIPE_SECRET_KEY is needed (Vercel → Settings → Environment Variables);
// the line item is built from src/content/site.ts, so no products need setting up in Stripe.
// Without the key it redirects back to /reserve in preview mode.
//
// Data minimisation: Stripe collects only what fulfilment needs: email (receipt and
// shipping updates, always collected by Checkout), name and delivery address, and the
// card. No phone number, no account, no marketing opt-in.

const DELIVERY_COUNTRIES = [
  "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GR", "HU", "IE", "IT", "LV", "LT", "LU",
  "MT", "NL", "PL", "PT", "RO", "SK", "SI", "ES", "SE", "IS", "LI", "NO", "CH", "GB", "MC", "AD", "SM",
];

export async function POST(request: Request) {
  const origin = process.env.NEXT_PUBLIC_SITE_URL || new URL(request.url).origin;
  const form = await request.formData();
  const edition = String(form.get("edition") ?? "");
  const model = String(form.get("model") ?? "");
  if (!isEditionId(edition) || !isModelId(model) || !editions[edition].available) {
    return NextResponse.redirect(new URL("/reserve", origin), 303);
  }
  const back = `/reserve?edition=${edition}&model=${model}`;

  const key = process.env.STRIPE_SECRET_KEY;
  if (!key) {
    return NextResponse.redirect(new URL(`${back}&status=preview`, origin), 303);
  }

  const ed = editions[edition];
  const name = `${ed.name === site.name ? site.name : `KINETIQ ${ed.name}`}: ${models[model].name}`;
  const body = new URLSearchParams({
    mode: "payment",
    "line_items[0][quantity]": "1",
    "line_items[0][price_data][currency]": "eur",
    "line_items[0][price_data][unit_amount]": String(ed.priceEur * 100),
    "line_items[0][price_data][product_data][name]": name,
    "line_items[0][price_data][product_data][description]": `${site.shipLabel}. ${site.refundLabel}.`,
    "payment_method_types[0]": "card",
    billing_address_collection: "auto",
    submit_type: "pay",
    success_url: `${origin}/reserved?session_id={CHECKOUT_SESSION_ID}`,
    cancel_url: `${origin}${back}`,
    "metadata[edition]": edition,
    "metadata[model]": model,
    "payment_intent_data[metadata][edition]": edition,
    "payment_intent_data[metadata][model]": model,
    "custom_text[submit][message]": `${site.refundLabel}. ${site.shipLabel}.`,
  });
  DELIVERY_COUNTRIES.forEach((c, i) => body.append(`shipping_address_collection[allowed_countries][${i}]`, c));

  const res = await fetch("https://api.stripe.com/v1/checkout/sessions", {
    method: "POST",
    headers: { Authorization: `Bearer ${key}`, "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });
  if (!res.ok) {
    console.error("Stripe checkout session failed", res.status, await res.text());
    return NextResponse.redirect(new URL(`${back}&status=error`, origin), 303);
  }
  const session = (await res.json()) as { url?: string };
  return NextResponse.redirect(session.url ?? new URL(`${back}&status=error`, origin), 303);
}
