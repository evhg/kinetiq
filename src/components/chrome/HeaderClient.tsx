"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import type { FeelId } from "@/content/site";
import { useFeel, withFeel } from "@/lib/feel-store";
import { FeelToggle } from "./FeelToggle";
import styles from "./Chrome.module.css";

/** The feel toggle's words, passed in from the server like the CTA label (src/content/site.ts). */
export type FeelToggleCopy = { label: string; labels: Record<FeelId, string> };

/**
 * Wordmark only. On the landing page a compact Reserve Now appears while neither the hero (the element with id
 * "hero") nor an in-page Reserve Now (marked data-cta) is on screen, so two never show at once. The label comes in
 * as a prop from the server (Chrome.tsx), so this client module carries no site copy: the root not-found renders
 * the header too, and its tree ships with every page, the NDA gate included.
 * Beside it, the Command and Pace toggle (`feelToggle`, its words passed in the same way), shown and hidden with it: on
 * phones its two swatches alone, from 700 px with their names (DESIGN.md "Feel toggle"). Reserve Now carries the
 * chosen feel into checkout (?feel=).
 */
export function HeaderClient({ ctaLabel, feelToggle }: { ctaLabel?: string; feelToggle?: FeelToggleCopy }) {
  const compactCta = Boolean(ctaLabel);
  const { chosen } = useFeel();
  const ref = useRef<HTMLElement>(null);
  const [scrolled, setScrolled] = useState(false);
  const [showCta, setShowCta] = useState(false);
  // The header's height (it follows the viewport width), so the CTA observer below always discounts the strip under it.
  const [chromeH, setChromeH] = useState(0);

  // The fixed chrome's real height replaces the CSS estimate in --chrome-h.
  useEffect(() => {
    const header = ref.current;
    if (!header) return;
    const root = document.documentElement.style;
    const ro = new ResizeObserver(([entry]) => {
      const h = entry.borderBoxSize?.[0]?.blockSize ?? header.getBoundingClientRect().height;
      root.setProperty("--chrome-h", `${h}px`);
      setChromeH(Math.round(h));
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
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  useEffect(() => {
    const hero = document.getElementById("hero");
    let io: IntersectionObserver | null = null;
    if (compactCta && hero) {
      // Whatever sits under the fixed header is not on screen: the root's top edge is the header's foot. Rebuilt when
      // the header's height changes.
      const top = chromeH || (ref.current?.offsetHeight ?? 0);
      const onScreen = new Set<Element>();
      io = new IntersectionObserver(
        (entries) => {
          for (const e of entries) {
            if (e.isIntersecting) onScreen.add(e.target);
            else onScreen.delete(e.target);
          }
          setShowCta(onScreen.size === 0);
        },
        { threshold: 0, rootMargin: `-${top}px 0px 0px 0px` },
      );
      for (const el of [hero, ...document.querySelectorAll("[data-cta]")]) io.observe(el);
    }
    return () => io?.disconnect();
  }, [compactCta, chromeH]);

  return (
    <header ref={ref} className={styles.header} data-scrolled={scrolled}>
      <div className={styles.row}>
        <Link href="/" className={styles.wordmark} aria-label="KINETIQ home">
          KINETIQ
        </Link>
        {compactCta ? (
          <div className={styles.end}>
            {feelToggle ? (
              <FeelToggle
                label={feelToggle.label}
                labels={feelToggle.labels}
                size="compact"
                className={styles.feel}
                inert={!showCta}
                visible={showCta}
              />
            ) : null}
            <Link
              href={withFeel("/reserve", chosen)}
              prefetch={false}
              className={`btn btn-primary ${styles.compact}`}
              data-visible={showCta}
              tabIndex={showCta ? 0 : -1}
              aria-hidden={!showCta}
            >
              {ctaLabel}
            </Link>
          </div>
        ) : null}
      </div>
    </header>
  );
}
