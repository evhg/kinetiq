"use client";

// Minimal Stripe.js loader (no SDK dependency). Stripe.js must be loaded from js.stripe.com.

export type StripeElement = {
  mount: (el: HTMLElement) => void;
  unmount: () => void;
  destroy: () => void;
  on: (event: "ready" | "change", cb: (e: { complete?: boolean }) => void) => void;
};
export type StripeElements = {
  create: (type: "payment", options?: Record<string, unknown>) => StripeElement;
  update: (options: Record<string, unknown>) => void;
  submit: () => Promise<{ error?: { message?: string } }>;
};
export type Stripe = {
  elements: (options: Record<string, unknown>) => StripeElements;
  confirmPayment: (options: Record<string, unknown>) => Promise<{
    error?: { message?: string; type?: string };
    paymentIntent?: { id: string; status: string };
  }>;
};

declare global {
  interface Window {
    Stripe?: (key: string, options?: Record<string, unknown>) => Stripe;
  }
}

let loading: Promise<Stripe | null> | null = null;

export function loadStripe(publishableKey: string | undefined): Promise<Stripe | null> {
  if (!publishableKey) return Promise.resolve(null);
  if (loading) return loading;
  loading = new Promise((resolve) => {
    const done = () => resolve(window.Stripe ? window.Stripe(publishableKey) : null);
    if (window.Stripe) return done();
    const s = document.createElement("script");
    s.src = "https://js.stripe.com/v3/";
    s.async = true;
    s.onload = done;
    s.onerror = () => resolve(null);
    document.head.appendChild(s);
  });
  return loading;
}
