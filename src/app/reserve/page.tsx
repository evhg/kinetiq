import type { Metadata } from "next";
import { Suspense } from "react";
import { SiteHeader } from "@/components/chrome/Chrome";
import { ReserveExperience } from "@/components/reserve/ReserveExperience";
import { tierById } from "@/content/lineup";
import { reserveCopy } from "@/content/reserve";
import { isFeelId } from "@/content/site";

export const metadata: Metadata = { title: reserveCopy.pageTitle };

type Search = Promise<Record<string, string | string[] | undefined>>;

// Tesla's structure: wordmark only, no footer. The last element is Pay with Card, then Place Reservation.
// The shell (header, default edition) is static; ?tier= and ?feel= stream in behind Suspense.
export default function ReservePage({ searchParams }: { searchParams: Search }) {
  return (
    <>
      <SiteHeader />
      <main id="main">
        <Suspense fallback={<ReserveExperience />}>
          <Preselected searchParams={searchParams} />
        </Suspense>
      </main>
    </>
  );
}

async function Preselected({ searchParams }: { searchParams: Search }) {
  const q = await searchParams;
  const one = (v: string | string[] | undefined) => (Array.isArray(v) ? v[0] : v);
  const tier = tierById(one(q.tier));
  const feel = one(q.feel);
  const initialTier = tier?.available ? tier.id : undefined;
  const initialFeel = isFeelId(feel) ? feel : null;
  // Next keeps a visited /reserve alive (Activity), and useState ignores new initial values, so a link
  // with another ?tier= or ?feel= starts a fresh experience instead of showing the old choice.
  return <ReserveExperience key={`${initialTier ?? ""}:${initialFeel ?? ""}`} initialTier={initialTier} initialFeel={initialFeel} />;
}
