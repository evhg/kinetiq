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
 * /reserved, so they are one tap away anywhere on the page (owner, 2026-11-03; DESIGN.md "Feel toggle"). On / they
 * show as soon as the hero's own toggle row (marked data-view-toggles) is no longer wholly in view below the header,
 * so at every scroll position one set or the other can be tapped (the whole hero watched instead left a dead band
 * while its last screen scrolled away); /reserve and /reserved show them from the first paint. While the compact Reserve
 * Now is hidden the control slides flush to the row's end (a transform, so nothing reflows). Reserve Now carries the
 * chosen feel into checkout (?feel=).
 */
/** "Wholly in view": a sub-pixel sliver lost to rounding still counts as whole (less than 1 px of a 44 px row). */
const WHOLE = 0.98;

export function HeaderClient({ ctaLabel, view }: { ctaLabel?: string; view?: ViewCopy }) {
  const compactCta = Boolean(ctaLabel);
  const { chosen } = useFeel();
  const ref = useRef<HTMLElement>(null);
  const [scrolled, setScrolled] = useState(false);
  const [showCta, setShowCta] = useState(false);
  // Pages without a hero (/reserve, /reserved) show the view control from the first paint; / once the hero's toggle
  // row is not wholly in view below the header.
  const [heroTogglesInView, setHeroTogglesInView] = useState(compactCta);
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
        },
        { threshold: 0, rootMargin: `-${top}px 0px 0px 0px` },
      );
      for (const el of [hero, ...(compactCta ? document.querySelectorAll("[data-cta]") : [])]) io.observe(el);
    }
    return () => io?.disconnect();
  }, [compactCta, chromeH]);

  // The hero's toggle row, wholly in view below the header (the same root as above), or not: the header's own choices
  // show the moment its first pixel slips under the header or past the screen's foot. Without the row (a hero without
  // toggles), the whole hero stands in for it.
  const hasView = Boolean(view);
  useEffect(() => {
    if (!hasView) return;
    const hero = document.getElementById("hero");
    if (!hero) return; // no hero (/reserve, /reserved): shown from the first paint
    const row = hero.querySelector("[data-view-toggles]") ?? hero;
    const top = chromeH || (ref.current?.offsetHeight ?? 0);
    const whole = row === hero ? 0 : WHOLE;
    const io = new IntersectionObserver(
      ([e]) => setHeroTogglesInView(e.isIntersecting && e.intersectionRatio >= whole),
      { threshold: row === hero ? 0 : [0, WHOLE, 1], rootMargin: `-${top}px 0px 0px 0px` },
    );
    io.observe(row);
    return () => io.disconnect();
  }, [hasView, chromeH]);

  // How far the view control slides right while the compact Reserve Now is hidden: its width and the gap before it,
  // kept on the row's end group as --view-shift (ViewControl.module.css reads it).
  const end = useRef<HTMLDivElement>(null);
  const cta = useRef<HTMLAnchorElement>(null);
  useEffect(() => {
    const group = end.current;
    const link = cta.current;
    if (!group || !link) return;
    const measure = () => {
      const gap = parseFloat(getComputedStyle(group).columnGap) || 0;
      group.style.setProperty("--view-shift", `${link.offsetWidth + gap}px`);
    };
    measure();
    const ro = new ResizeObserver(measure);
    ro.observe(link);
    ro.observe(group);
    return () => ro.disconnect();
  }, []);

  return (
    <header ref={ref} className={styles.header} data-scrolled={scrolled}>
      <div className={styles.row}>
        <Link href="/" className={styles.wordmark} aria-label="KINETIQ home">
          KINETIQ
        </Link>
        {compactCta || view ? (
          <div ref={end} className={styles.end}>
            {view ? <ViewControl copy={view} visible={!heroTogglesInView} flush={compactCta && !showCta} /> : null}
            {compactCta ? (
              <Link
                ref={cta}
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
