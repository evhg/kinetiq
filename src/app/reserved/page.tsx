import type { Metadata } from "next";
import { Suspense } from "react";
import { SiteHeader } from "@/components/chrome/Chrome";
import { Still } from "@/components/media/Still";
import { ReservedStatus } from "@/components/reserve/ReservedStatus";
import styles from "@/components/reserve/Reserved.module.css";
import { reserveCopy } from "@/content/reserve";

export const metadata: Metadata = { title: reserveCopy.reserved.pageTitle, robots: { index: false, follow: false } };

type Search = Promise<Record<string, string | string[] | undefined>>;

export default function ReservedPage({ searchParams }: { searchParams: Search }) {
  return (
    <>
      <SiteHeader toggles />
      <main id="main" className={styles.page}>
        <div className={styles.backdrop} aria-hidden="true">
          {/* The page's largest paint (its LCP element on every viewport): fetched at once, never lazily (phone profile,
              2026-11-04: lazy, it landed at 2.52 s, over the 2.5 s budget). */}
          <Still id="K01-finale" phoneCrop="portrait" alt="" priority className={styles.still} />
        </div>
        <Suspense fallback={<ReservedStatus pending />}>
          <FromReturnUrl searchParams={searchParams} />
        </Suspense>
      </main>
    </>
  );
}

async function FromReturnUrl({ searchParams }: { searchParams: Search }) {
  const q = await searchParams;
  const one = (v: string | string[] | undefined) => (Array.isArray(v) ? v[0] : v);
  return (
    <ReservedStatus
      redirect={one(q.redirect_status)}
      hasSecret={Boolean(one(q.payment_intent_client_secret))}
      tier={one(q.tier)}
      feel={one(q.feel)}
    />
  );
}
