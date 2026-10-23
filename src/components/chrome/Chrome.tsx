import Link from "next/link";
import { site } from "@/content/site";
import { HeaderClient } from "./HeaderClient";
import styles from "./Chrome.module.css";

// Server side of the chrome. Its words come from src/content/site.ts and reach the client only where a page renders
// them: the root not-found (header without CTA, footer without the brand line) is serialised into every page, the
// NDA gate included, so nothing it renders may carry product copy or claims.

/** Wordmark only; `compactCta` adds the compact Reserve Now that appears after the hero (landing page). */
export function SiteHeader({ compactCta = false }: { compactCta?: boolean }) {
  return <HeaderClient ctaLabel={compactCta ? site.ctaLabel : undefined} />;
}

/** `brandLine={false}` drops "100% Swiss Made." (`site.swissMade`, CLAIMS.md row 10): the root not-found uses it. */
export function SiteFooter({ brandLine = true }: { brandLine?: boolean }) {
  return (
    <footer className={styles.footer}>
      <p>{brandLine ? `${site.copyright} ${site.swissMade}.` : site.copyright}</p>
      <Link href="/credits">Credits</Link>
    </footer>
  );
}
