"use client";

import { useRef } from "react";
import { ReserveLink } from "@/components/chrome/ReserveLink";
import { useMotion } from "@/components/motion/MotionProvider";
import { Still } from "@/components/media/Still";
import { finale } from "@/content/copy";
import { site } from "@/content/site";
import { gsap, useGSAP } from "@/lib/gsap";
import styles from "@/components/landing/Finale.module.css";
import own from "./WordFinale.module.css";

/**
 * Effect 5, the words light up: the page's closing line, word by word, as you read it in. The Finale of /, its layout
 * unchanged; each word (a phrase held by no-break spaces counts as one) goes from dim to full as the section comes up
 * the screen, then the price and Reserve Now follow. Any screen size; reduced motion and the server render:
 * the whole line lit. The words stay plain text in order, so a screen reader reads one sentence.
 */
export function WordFinale() {
  const root = useRef<HTMLElement>(null);
  const { motionOn } = useMotion();
  const words = finale.headline.split(" ");

  useGSAP(
    () => {
      if (!motionOn) return;
      const mm = gsap.matchMedia();
      mm.add("(prefers-reduced-motion: no-preference)", () => {
        const els = gsap.utils.toArray<HTMLElement>(`.${own.word}`);
        // From the section's top at 70% of the screen to the end of the page ("max": the footer is below, so the
        // section's own bottom never reaches the screen's). The words light in the first 70%, then the price and
        // Reserve Now rise in, so both are lit and visible whenever the visitor stops at the foot of the page.
        const tl = gsap.timeline({
          defaults: { ease: "none" },
          scrollTrigger: { trigger: root.current, start: "top 70%", end: "max", scrub: 0.4 },
        });
        tl.fromTo(els, { opacity: 0.16 }, { opacity: 1, duration: 0.22, stagger: 0.48 / Math.max(1, els.length - 1), immediateRender: true }, 0)
          .fromTo(`.${own.after}`, { autoAlpha: 0, y: 14 }, { autoAlpha: 1, y: 0, duration: 0.15, immediateRender: true }, 0.72)
          .to({}, { duration: 0.13 });
      });
      return () => mm.revert();
    },
    { scope: root, dependencies: [motionOn], revertOnUpdate: true },
  );

  return (
    <section ref={root} id="finale" className={`${styles.section} ${own.section}`} aria-labelledby="finale-title">
      <div className={styles.media} aria-hidden="true">
        <Still id="K01-finale" phoneCrop="card" phoneMedia="(max-width: 699px) and (min-height: 741px), (max-width: 699px) and (orientation: landscape)" alt="" phoneSizes="100vw" className={styles.still} />
      </div>
      <div className={styles.copy}>
        <h2 id="finale-title" className={`t-h2 ${own.line}`}>
          {words.map((w, i) => (
            <span key={i} className={own.word}>
              {w}
              {i < words.length - 1 ? " " : ""}
            </span>
          ))}
        </h2>
        <div className={own.after}>
          <p className="t-lead">{finale.sub}</p>
          <ReserveLink href="/reserve" className={`btn btn-primary ${styles.cta}`} data-cta="">
            {site.ctaLabel}
          </ReserveLink>
        </div>
      </div>
    </section>
  );
}
