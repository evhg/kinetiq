"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { site } from "@/content/site";
import styles from "./Chrome.module.css";

export function PreviewBanner() {
  if (process.env.NEXT_PUBLIC_LAUNCHED === "true") return null;
  return (
    <p className={styles.banner} role="note">
      <span className={styles.bannerLong}>Preview: claims pending verification. Not open for orders yet.</span>
      <span className={styles.bannerShort}>Preview. Claims pending. No orders yet.</span>
    </p>
  );
}

/**
 * Wordmark only. On the landing page a compact Reserve Now appears once the hero has
 * left the viewport (sentinel = the element with id "hero").
 */
export function SiteHeader({ compactCta = false }: { compactCta?: boolean }) {
  const ref = useRef<HTMLElement>(null);
  const [scrolled, setScrolled] = useState(false);
  const [pastHero, setPastHero] = useState(false);

  // The fixed chrome's real height (the banner wraps on phones) replaces the CSS estimate in --chrome-h.
  useEffect(() => {
    const header = ref.current;
    if (!header) return;
    const root = document.documentElement.style;
    const ro = new ResizeObserver(([entry]) => {
      const h = entry.borderBoxSize?.[0]?.blockSize ?? header.getBoundingClientRect().height;
      root.setProperty("--chrome-h", `${h}px`);
    });
    ro.observe(header);
    return () => {
      ro.disconnect();
      root.removeProperty("--chrome-h");
    };
  }, []);

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
    <header ref={ref} className={styles.header} data-scrolled={scrolled}>
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
      <Link href="/credits">Credits</Link>
    </footer>
  );
}
