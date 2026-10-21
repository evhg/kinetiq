import type { Metadata } from "next";
import Link from "next/link";
import { SiteFooter, SiteHeader } from "@/components/chrome/Chrome";
import styles from "./not-found.module.css";

export const metadata: Metadata = {
  title: "Page not found",
};

/** Unknown URLs (and /lab in production): on brand, not Next's default white page. */
export default function NotFound() {
  return (
    <>
      <SiteHeader />
      <main id="main" className={`lift tech-grid ${styles.main}`}>
        <hr className={`lightline ${styles.line}`} />
        <p className={`t-eyebrow ${styles.code}`}>404</p>
        <h1 className="t-h1">Nothing here.</h1>
        <p className="t-lead">This page does not exist, or it has moved.</p>
        <Link href="/" className={`btn btn-secondary ${styles.home}`}>
          Back to KINETIQ
        </Link>
      </main>
      <SiteFooter />
    </>
  );
}
