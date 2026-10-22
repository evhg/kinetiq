import Link from "next/link";
import { site } from "@/content/site";
import { HeaderClient } from "./HeaderClient";
import styles from "./Chrome.module.css";

// Server side of the chrome. The words stay here and reach the client only where a page renders them: the root
// not-found (header without CTA, footer without the brand line) is serialised into every page, the NDA gate
// included, so nothing it renders may carry product copy or claims.

/** Wordmark only; `compactCta` adds the compact Reserve Now that appears after the hero (landing page). */
export function SiteHeader({ compactCta = false }: { compactCta?: boolean }) {
  return <HeaderClient ctaLabel={compactCta ? site.ctaLabel : undefined} />;
}

/** `brandLine={false}` drops "100% Swiss Made." (a claim, CLAIMS.md row 10): the root not-found uses it. */
export function SiteFooter({ brandLine = true }: { brandLine?: boolean }) {
  return (
    <footer className={styles.footer}>
      <p>{brandLine ? "© 2026 KINETIQ. 100% Swiss Made." : "© 2026 KINETIQ."}</p>
      <Link href="/credits">Credits</Link>
    </footer>
  );
}
