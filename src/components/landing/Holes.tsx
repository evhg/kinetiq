"use client";

import { useRef } from "react";
import { DrilledVsMoulded } from "@/components/graphics/DrilledVsMoulded";
import { Still } from "@/components/media/Still";
import { useMotion } from "@/components/motion/MotionProvider";
import { PinnedChapter } from "@/components/motion/PinnedChapter";
import { holes } from "@/content/copy";
import { gsap, useGSAP } from "@/lib/gsap";
import { Reveal } from "./Reveal";
import styles from "./Holes.module.css";

/** Below the pin (phones, tablets): the macro settles as it scrolls through, without a pin. */
const FLOW = "(max-width: 899px) and (prefers-reduced-motion: no-preference)";

/**
 * 42 moulded holes, the visual peak of the page (owner, 2026-10-28: "Only with this one I feel something"). Pinned from
 * 900 px for 1.4 screens: K04 fills the screen alone, close on the lit hole, and slowly draws back while the ring of
 * light around the bore comes up; only then the shade and the words arrive over its left side, and the screen holds.
 * Phones and tablets: K04 large (its whole card crop at the full width on phones), settling as it scrolls through,
 * then the words. Then drilled against moulded (G06). The sealed core follows (SealedCore.tsx): the lined holes are
 * what keep the core closed. Reduced motion and the server render: the final state, every word visible.
 */
export function Holes() {
  const flow = useRef<HTMLDivElement>(null);
  const { motionOn } = useMotion();

  useGSAP(
    () => {
      if (!motionOn) return;
      const mm = gsap.matchMedia();
      mm.add(FLOW, () => {
        const band = flow.current;
        if (!band) return;
        gsap
          .timeline({ defaults: { ease: "none" }, scrollTrigger: { trigger: band, start: "top bottom", end: "bottom 40%", scrub: 0.6 } })
          .fromTo(band.querySelectorAll(`.${styles.layer}`), { scale: 1.14 }, { scale: 1, duration: 1 }, 0)
          .fromTo(band.querySelector(`.${styles.ring}`), { opacity: 0 }, { opacity: 1, duration: 0.5 }, 0.2);
      });
      return () => mm.revert();
    },
    { scope: flow, dependencies: [motionOn], revertOnUpdate: true },
  );

  return (
    <>
      <PinnedChapter
        id="holes"
        nextId="holes-pair"
        labelledBy="holes-title"
        className={styles.chapter}
        length={1.4}
        build={(tl) => {
          const show = { autoAlpha: 1, y: 0, immediateRender: true } as const;
          gsap.set(`.${styles.copy} > *`, { autoAlpha: 0, y: 16 });
          gsap.set(`.${styles.shade}`, { autoAlpha: 0 });
          // The macro alone first, close on the lit hole, drawing back over almost the whole pin; the ring of light comes
          // up as it does. Then the shade and the words, and the screen holds.
          tl.fromTo(`.${styles.media}`, { scale: 1.22 }, { scale: 1, duration: 0.7, ease: "power1.out", immediateRender: true }, 0)
            .fromTo(`.${styles.ring}`, { opacity: 0 }, { opacity: 1, duration: 0.3, immediateRender: true }, 0.08)
            .fromTo(`.${styles.shade}`, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.12, immediateRender: true }, 0.42)
            .fromTo(`.${styles.copy} > *`, { autoAlpha: 0, y: 16 }, { ...show, stagger: 0.04, duration: 0.1 }, 0.46)
            .to({}, { duration: 0.24 });
        }}
      >
        <div ref={flow} className={styles.band}>
          <div className={styles.media} aria-hidden="true">
            <Still id="K04-base" phoneCrop="card" alt="" sizes="100vw" className={styles.layer} />
            <Still id="K04-full" phoneCrop="card" alt="" sizes="100vw" className={`${styles.layer} ${styles.ring}`} />
          </div>
          <div className={styles.shade} aria-hidden="true" />
          <Reveal className={styles.copy} media={FLOW}>
            <p className="t-eyebrow">{holes.eyebrow}</p>
            <h2 id="holes-title" className="t-h2">
              {holes.headline}
            </h2>
            <p className="t-lead">{holes.body}</p>
            {/* The owner's point (2026-10-23): no drilling, no exposed foam and a smooth wrap, together on no other racket. */}
            <p className={`t-lead ${styles.only}`}>{holes.only}</p>
            <dl className={styles.stats}>
              {holes.stats.map((s) => (
                <div key={s.label} className={styles.stat}>
                  <dt className={`t-label ${styles.statLabel}`}>{s.label}</dt>
                  <dd className={`t-stat ${styles.statValue}`}>{s.value}</dd>
                </div>
              ))}
            </dl>
          </Reveal>
        </div>
      </PinnedChapter>
      <section id="holes-pair" tabIndex={-1} className={`lift ${styles.pair}`} aria-label="Drilled holes compared with moulded holes">
        <DrilledVsMoulded />
      </section>
    </>
  );
}
