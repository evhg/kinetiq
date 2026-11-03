import { feelToggleLabels, gripToggleLabels, site } from "@/content/site";
import { HeaderClient, type ViewCopy } from "./HeaderClient";
import styles from "./Chrome.module.css";

// Server side of the chrome. Its words come from src/content/site.ts and reach the client only where a page renders
// them: the root not-found (header without CTA or toggles, footer without the brand line) is serialised into every
// page, the NDA gate included, so nothing it renders may carry product copy or claims.

const view: ViewCopy = {
  label: site.viewToggleLabel,
  feel: { label: site.feelToggleLabel, labels: feelToggleLabels },
  grip: { label: site.gripToggleLabel, labels: gripToggleLabels },
};

/**
 * Wordmark only; `toggles` adds the Feel and Handle choices (ViewControl: the two named groups from 1024 px, one button
 * and its panel below), on /, /reserve and /reserved, so they are reachable from anywhere on those pages (owner,
 * 2026-11-03); `compactCta` adds the compact Reserve Now that appears after the hero (landing page). Never on the
 * not-found or credits pages.
 */
export function SiteHeader({ compactCta = false, toggles = compactCta }: { compactCta?: boolean; toggles?: boolean }) {
  return <HeaderClient ctaLabel={compactCta ? site.ctaLabel : undefined} view={toggles ? view : undefined} />;
}

/**
 * `brandLine={false}` drops "100% Swiss Made." (`site.swissMade`, CLAIMS.md row 10): the root not-found uses it. No
 * Credits link (owner, 2026-10-23): /credits and public/CREDITS.md stay, unlinked from the footer.
 */
export function SiteFooter({ brandLine = true }: { brandLine?: boolean }) {
  return (
    <footer className={styles.footer}>
      <p>{brandLine ? `${site.copyright} ${site.swissMade}.` : site.copyright}</p>
    </footer>
  );
}
