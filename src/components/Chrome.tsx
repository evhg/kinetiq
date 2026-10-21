import Link from "next/link";
import { MotionToggle } from "@/components/motion/MotionToggle";

export function PreviewBanner() {
  if (process.env.NEXT_PUBLIC_LAUNCHED === "true") return null;
  return (
    <p className="preview-banner" role="note">
      Preview: claims pending verification. Not open for orders yet.
    </p>
  );
}

export function SiteHeader() {
  return (
    <header className="site-header">
      <PreviewBanner />
      <div className="site-header-row">
      <Link href="/" className="wordmark" aria-label="KINETIQ home">
        KINETIQ
      </Link>
      <MotionToggle />
      </div>
    </header>
  );
}

export function SiteFooter() {
  return (
    <footer className="site-footer">
      <p>© 2026 KINETIQ. Made in St. Gallen, Switzerland.</p>
    </footer>
  );
}
