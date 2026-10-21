"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { priceLabel, tierById } from "@/content/lineup";
import { reserveCopy } from "@/content/reserve";
import { feels, isFeelId, site } from "@/content/site";
import styles from "./Reserved.module.css";

type State = { status: "succeeded" | "processing" | "failed" | "unknown"; tier?: string; feel?: string };

/** Where a card returns after a 3-D Secure check (Stripe adds redirect_status to the URL). */
export function ReservedStatus() {
  const [state, setState] = useState<State | null>(null);

  useEffect(() => {
    const q = new URLSearchParams(window.location.search);
    const s = q.get("redirect_status");
    // eslint-disable-next-line react-hooks/set-state-in-effect -- one-time read of the return URL
    setState({
      status: s === "succeeded" || s === "processing" || s === "failed" ? s : "unknown",
      tier: q.get("tier") ?? undefined,
      feel: q.get("feel") ?? undefined,
    });
  }, []);

  const t = tierById(state?.tier);
  const failed = state?.status === "failed";

  return (
    <div className={styles.box} aria-live="polite">
      <p className={`t-eyebrow ${styles.eyebrow}`}>{site.name}</p>
      <h1 className="t-h2">{failed ? "Your card was not charged." : reserveCopy.confirmationHeadline}</h1>
      {failed ? (
        <p className="t-lead">The bank did not confirm the payment, so nothing was reserved and nothing was charged.</p>
      ) : (
        <>
          {t ? (
            <p className={styles.tier}>
              {t.name}
              {isFeelId(state?.feel) ? `, ${feels[state.feel].name}` : ""}. <span className="t-num">{priceLabel(t.priceEur)}</span>
            </p>
          ) : null}
          <p className="t-lead">{reserveCopy.confirmationBody}</p>
        </>
      )}
      <Link href={failed ? "/reserve" : "/"} className="btn btn-secondary">
        {failed ? "Try again" : "Back to KINETIQ"}
      </Link>
    </div>
  );
}
