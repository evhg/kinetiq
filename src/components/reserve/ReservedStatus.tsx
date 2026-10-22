"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { orderLine, priceLabel, tierById, tiers, type Tier } from "@/content/lineup";
import { reserveCopy } from "@/content/reserve";
import { feels, isFeelId, site } from "@/content/site";
import { loadStripe } from "@/lib/stripe-client";
import styles from "./Reserved.module.css";

type Status = "checking" | "succeeded" | "processing" | "failed" | "unknown";

const PK = process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY;
const R = reserveCopy.reserved;

/** What Stripe's redirect_status says, before it is checked. */
function fromRedirect(s: string | undefined): Exclude<Status, "checking"> {
  return s === "succeeded" || s === "processing" || s === "failed" ? s : "unknown";
}

/** What a PaymentIntent's status means for the buyer. */
function fromIntent(s: string): Exclude<Status, "checking"> {
  if (s === "succeeded" || s === "processing") return s;
  return "failed";
}

type Props = {
  /** The static shell: nothing is known yet. */
  pending?: boolean;
  /** redirect_status from the return URL. */
  redirect?: string;
  /** Whether the return URL carries payment_intent_client_secret (Stripe always adds it). */
  hasSecret?: boolean;
  tier?: string;
  feel?: string;
};

/**
 * Where a card returns after a redirect-based check. The reservation is confirmed only when Stripe
 * says so: with a publishable key the PaymentIntent is read back from the client secret in the URL.
 */
export function ReservedStatus({ pending = false, redirect, hasSecret = false, tier, feel }: Props) {
  const initial: Status = pending ? "checking" : !redirect ? "unknown" : PK ? (hasSecret ? "checking" : "unknown") : fromRedirect(redirect);
  const [status, setStatus] = useState<Status>(initial);
  const [paidTier, setPaidTier] = useState<Tier | undefined>(undefined);
  const [paymentId, setPaymentId] = useState<string | null>(null);

  useEffect(() => {
    if (pending || !redirect || !PK || !hasSecret) return;
    const secret = new URLSearchParams(window.location.search).get("payment_intent_client_secret");
    let cancelled = false;
    loadStripe(PK)
      .then((stripe) => (stripe && secret ? stripe.retrievePaymentIntent(secret) : null))
      .then((r) => {
        if (cancelled) return;
        const pi = r?.paymentIntent;
        // Only when Stripe cannot be reached does the redirect's word count. A secret Stripe
        // rejects (edited or foreign link) confirms nothing.
        if (!pi) return setStatus(r?.error && r.error.type !== "api_connection_error" ? "unknown" : fromRedirect(redirect));
        setPaidTier(tiers.find((t) => t.priceEur * 100 === pi.amount));
        setPaymentId(pi.id);
        setStatus(fromIntent(pi.status));
      })
      .catch(() => {
        if (!cancelled) setStatus(fromRedirect(redirect));
      });
    return () => {
      cancelled = true;
    };
  }, [pending, redirect, hasSecret]);

  const t = paidTier ?? tierById(tier);
  const reserved = status === "succeeded" || status === "processing";
  // Try again returns to the same edition and feel.
  const retry = t ? `/reserve?tier=${t.id}${isFeelId(feel) ? `&feel=${feel}` : ""}` : "/reserve";

  return (
    <div className={styles.box} aria-live="polite">
      <p className={`t-eyebrow ${styles.eyebrow}`}>{site.name}</p>
      {status === "checking" ? (
        <h1 className="t-h2">{R.checking}</h1>
      ) : reserved ? (
        <>
          <h1 className="t-h2">{reserveCopy.confirmationHeadline}</h1>
          {t ? (
            <p className={styles.tier}>
              {isFeelId(feel) ? orderLine(t, feels[feel].name) : t.name}. <span className="t-num">{priceLabel(t.priceEur)}</span>
            </p>
          ) : null}
          <p className="t-lead">{reserveCopy.confirmationBody(t?.rackets)}</p>
          {paymentId ? <p className={`t-num ${styles.ref}`}>{reserveCopy.reference(paymentId)}</p> : null}
          <Link href="/" className="btn btn-secondary">
            {R.back}
          </Link>
        </>
      ) : status === "failed" ? (
        <>
          <h1 className="t-h2">{R.failedHeadline}</h1>
          <p className="t-lead">{R.failedBody}</p>
          <Link href={retry} className="btn btn-secondary">
            {R.retry}
          </Link>
        </>
      ) : (
        <>
          <h1 className="t-h2">{R.noneHeadline}</h1>
          <p className="t-lead">{R.noneBody}</p>
          <Link href="/reserve" className="btn btn-secondary">
            {site.ctaLabel}
          </Link>
        </>
      )}
    </div>
  );
}
