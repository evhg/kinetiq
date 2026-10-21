import type { Metadata } from "next";
import { SiteHeader } from "@/components/chrome/Chrome";
import { ReserveExperience } from "@/components/reserve/ReserveExperience";
import { reserveCopy } from "@/content/reserve";

export const metadata: Metadata = { title: `${reserveCopy.pageTitle} | KINETIQ` };

// Tesla's structure: wordmark only, no footer. The last element is Pay with Card, then Place Reservation.
export default function ReservePage() {
  return (
    <>
      <SiteHeader />
      <main id="main">
        <ReserveExperience />
      </main>
    </>
  );
}
