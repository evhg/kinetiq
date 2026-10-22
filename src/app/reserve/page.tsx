import type { Metadata } from "next";
import { Suspense } from "react";
import { SiteHeader } from "@/components/chrome/Chrome";
import { ReserveExperience } from "@/components/reserve/ReserveExperience";
import styles from "@/components/reserve/Reserve.module.css";
import { invitesOpen, tierById } from "@/content/lineup";
import { reserveCopy } from "@/content/reserve";
import { isFeelId } from "@/content/site";
import { productMetadata } from "@/lib/product-metadata";

export const metadata: Metadata = productMetadata(reserveCopy.pageTitle);

type Search = Promise<Record<string, string | string[] | undefined>>;

// Tesla's structure: wordmark only, no footer. The last element is Pay with Card, then Place Reservation.
// The shell (header and an empty stage) is static; the experience streams in behind Suspense with ?tier=, ?feel= and
// ?invite already applied, so a First 500 link never paints KINETIQ or its price first (the fallback shows no
// edition at all). One of Ten is never chosen from the link: ?tier=invite shows the default edition, and only a valid
// invitation code unlocks it (?invite=CODE checks one on load; a bare ?invite opens the code field).
export default function ReservePage({ searchParams }: { searchParams: Search }) {
  return (
    <>
      <SiteHeader />
      <main id="main">
        <Suspense fallback={<ReserveShell />}>
          <Preselected searchParams={searchParams} />
        </Suspense>
      </main>
    </>
  );
}

/**
 * What shows for the moment before the chosen edition streams in: the gallery's lit stage and the options column's
 * floor, with no edition name, price, selected card or gallery count. Neutral by design, so whatever the link asked
 * for is the first edition the visitor sees (and the NDA gate's arrival veil waits for it, globals.css).
 */
function ReserveShell() {
  return (
    <div className={styles.layout} data-reserve-shell="" aria-busy="true">
      <div className={`${styles.gallery} ${styles.shellGallery}`} aria-hidden="true">
        <div className={styles.track}>
          <div className={styles.slide} data-active="true" />
        </div>
      </div>
      <div className={`${styles.options} ${styles.shellOptions}`} aria-hidden="true" />
    </div>
  );
}

async function Preselected({ searchParams }: { searchParams: Search }) {
  const q = await searchParams;
  const one = (v: string | string[] | undefined) => (Array.isArray(v) ? v[0] : v);
  const tier = tierById(one(q.tier));
  const feel = one(q.feel);
  const initialTier = tier?.available && tier.id !== "invite" ? tier.id : undefined;
  const initialFeel = isFeelId(feel) ? feel : null;
  const invite = one(q.invite);
  const initialInvite = typeof invite === "string" ? invite.trim().slice(0, 40) : null;
  // Next keeps a visited /reserve alive (Activity), and useState ignores new initial values, so a link
  // with another ?tier= or ?feel= starts a fresh experience instead of showing the old choice.
  return (
    <ReserveExperience
      key={`${initialTier ?? ""}:${initialFeel ?? ""}:${initialInvite ?? "-"}`}
      initialTier={initialTier}
      initialFeel={initialFeel}
      initialInvite={initialInvite}
      invitesOpen={invitesOpen(process.env.INVITE_CODES)}
    />
  );
}
