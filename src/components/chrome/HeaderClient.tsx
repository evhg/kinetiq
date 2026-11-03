"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { useFeel, withFeel } from "@/lib/feel-store";
import { ViewControl, type ViewCopy } from "./ViewControl";
import styles from "./Chrome.module.css";

export type { ViewCopy };

/**
 * Wordmark only. On the landing page a compact Reserve Now appears while neither the hero (the element with id
 * "hero") nor an in-page Reserve Now (marked data-cta) is on screen, so two never show at once. The label comes in
 * as a prop from the server (Chrome.tsx), so this client module carries no site copy: the root not-found renders
 * the header too, and its tree ships with every page, the NDA gate included.
 * Before it, the Feel and Handle choices (`view`, their words passed in the same way; ViewControl): on /, /reserve and
 * /reserved, shown wherever the hero is not on screen (the hero has its own), whatever the compact Reserve Now does, so
 * they are one tap away anywhere on the page (owner, 2026-11-03; DESIGN.md "Feel toggle"). Reserve Now carries the
 * chosen feel into checkout (?feel=).
 */
export function HeaderClient({ ctaLabel, view }: { ctaLabel?: string; view?: ViewCopy }) {
  const compactCta = Boolean(ctaLabel);
  const { chosen } = useFeel();
  const ref = useRef<HTMLElement>(null);
  const [scrolled, setScrolled] = useState(false);
  const [showCta, setShowCta] = useState(false);
  // Pages without a hero (/reserve, /reserved) show the view control from the first paint; / once the hero has gone.
  const [heroOnScreen, setHeroOnScreen] = useState(compactCta);
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
    if (hero) {
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
          setHeroOnScreen(onScreen.has(hero));
        },
        { threshold: 0, rootMargin: `-${top}px 0px 0px 0px` },
      );
      for (const el of [hero, ...(compactCta ? document.querySelectorAll("[data-cta]") : [])]) io.observe(el);
    } else {
      setHeroOnScreen(false);
    }
    return () => io?.disconnect();
  }, [compactCta, chromeH]);

  return (
    <header ref={ref} className={styles.header} data-scrolled={scrolled}>
      <div className={styles.row}>
        <Link href="/" className={styles.wordmark} aria-label="KINETIQ home">
          KINETIQ
        </Link>
        {compactCta || view ? (
          <div className={styles.end}>
            {view ? <ViewControl copy={view} visible={!heroOnScreen} /> : null}
            {compactCta ? (
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
            ) : null}
          </div>
        ) : null}
      </div>
    </header>
  );
}
