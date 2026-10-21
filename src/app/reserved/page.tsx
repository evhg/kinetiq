import type { Metadata } from "next";
import { SiteHeader } from "@/components/chrome/Chrome";
import { ReservedStatus } from "@/components/reserve/ReservedStatus";
import styles from "@/components/reserve/Reserved.module.css";

export const metadata: Metadata = { title: "Reserved | KINETIQ", robots: { index: false, follow: false } };

export default function ReservedPage() {
  return (
    <>
      <SiteHeader />
      <main id="main" className={styles.page}>
        <ReservedStatus />
      </main>
    </>
  );
}
