"use client";

// Minimal Stripe.js loader (no SDK dependency). Stripe.js must be loaded from js.stripe.com.
// Pinned to the endive release, the same train as the Stripe-Version the reserve route sends.
const STRIPE_JS = "https://js.stripe.com/endive/stripe.js";

type StripeError = { message?: string; type?: string; code?: string };
export type PaymentIntentStatus = { id: string; status: string; amount?: number; currency?: string };

export type StripeElement = {
  mount: (el: HTMLElement) => void;
  unmount: () => void;
  destroy: () => void;
  on: (event: "ready" | "change" | "loaderror", cb: (e: { complete?: boolean; error?: StripeError }) => void) => void;
};
export type StripeElements = {
  create: (type: "payment", options?: Record<string, unknown>) => StripeElement;
  update: (options: Record<string, unknown>) => void;
  submit: () => Promise<{ error?: StripeError }>;
};
export type Stripe = {
  elements: (options: Record<string, unknown>) => StripeElements;
  confirmPayment: (options: Record<string, unknown>) => Promise<{
    error?: StripeError;
    paymentIntent?: PaymentIntentStatus;
  }>;
  retrievePaymentIntent: (clientSecret: string) => Promise<{
    error?: StripeError;
    paymentIntent?: PaymentIntentStatus;
  }>;
};

declare global {
  interface Window {
    Stripe?: (key: string, options?: Record<string, unknown>) => Stripe;
  }
}

let loading: Promise<Stripe | null> | null = null;

/** Loads Stripe.js once. A failed load is not cached, so the next call tries again. */
export function loadStripe(publishableKey: string | undefined): Promise<Stripe | null> {
  if (!publishableKey) return Promise.resolve(null);
  if (loading) return loading;
  const attempt = new Promise<Stripe | null>((resolve) => {
    // Stripe() throws on a malformed key; that must end the wait, not leave callers hanging.
    const done = () => {
      try {
        resolve(window.Stripe ? window.Stripe(publishableKey) : null);
      } catch {
        resolve(null);
      }
    };
    if (window.Stripe) return done();
    document.querySelector(`script[src="${STRIPE_JS}"]`)?.remove();
    const s = document.createElement("script");
    s.src = STRIPE_JS;
    s.async = true;
    s.onload = done;
    s.onerror = () => resolve(null);
    document.head.appendChild(s);
  });
  loading = attempt;
  attempt.then((stripe) => {
    if (!stripe && loading === attempt) loading = null;
  });
  return attempt;
}

/** The PaymentIntent behind a client secret when it is paid or settling, otherwise null. */
export async function isPaid(stripe: Stripe, clientSecret: string): Promise<PaymentIntentStatus | null> {
  try {
    const { paymentIntent } = await stripe.retrievePaymentIntent(clientSecret);
    return paymentIntent && (paymentIntent.status === "succeeded" || paymentIntent.status === "processing") ? paymentIntent : null;
  } catch {
    return null;
  }
}
