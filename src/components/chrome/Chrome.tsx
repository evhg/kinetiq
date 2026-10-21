"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { site } from "@/content/site";
import styles from "./Chrome.module.css";

export function PreviewBanner() {
  if (process.env.NEXT_PUBLIC_LAUNCHED === "true") return null;
  return (
    <p className={styles.banner} role="note">
      Preview: claims pending verification. Not open for orders yet.
    </p>
  );
}

/**
 * Wordmark only. On the landing page a compact Reserve Now appears once the hero has
 * left the viewport (sentinel = the element with id "hero").
 */
export function SiteHeader({ compactCta = false }: { compactCta?: boolean }) {
  const [scrolled, setScrolled] = useState(false);
  const [pastHero, setPastHero] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 40);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    const hero = document.getElementById("hero");
    let io: IntersectionObserver | null = null;
    if (compactCta && hero) {
      io = new IntersectionObserver(([e]) => setPastHero(!e.isIntersecting), { threshold: 0 });
      io.observe(hero);
    }
    return () => {
      window.removeEventListener("scroll", onScroll);
      io?.disconnect();
    };
  }, [compactCta]);

  return (
    <header className={styles.header} data-scrolled={scrolled}>
      <PreviewBanner />
      <div className={styles.row}>
        <Link href="/" className={styles.wordmark} aria-label="KINETIQ home">
          KINETIQ
        </Link>
        {compactCta ? (
          <Link
            href="/reserve"
            prefetch={false}
            className={`btn btn-primary ${styles.compact}`}
            data-visible={pastHero}
            tabIndex={pastHero ? 0 : -1}
            aria-hidden={!pastHero}
          >
            {site.ctaLabel}
          </Link>
        ) : null}
      </div>
    </header>
  );
}

export function SiteFooter() {
  return (
    <footer className={styles.footer}>
      <p>© 2026 KINETIQ. 100% Swiss Made.</p>
      <a href="/CREDITS.md">Credits</a>
    </footer>
  );
}
