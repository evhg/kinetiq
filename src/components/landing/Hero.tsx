"use client";

import Link from "next/link";
import { useRef } from "react";
import { Still } from "@/components/media/Still";
import { useMotion } from "@/components/motion/MotionProvider";
import { hero } from "@/content/copy";
import { site } from "@/content/site";
import { gsap, useGSAP } from "@/lib/gsap";
import styles from "./Hero.module.css";

/** Hero: K01 rises out of the dark (base, then the beam), centred text, one CTA. */
export function Hero() {
  const root = useRef<HTMLElement>(null);
  const { motionOn } = useMotion();

  useGSAP(
    () => {
      if (!motionOn) return;
      const mm = gsap.matchMedia();
      mm.add("(prefers-reduced-motion: no-preference)", () => {
        // The beam: the lit render fades over the dark base while the frame settles.
        gsap.fromTo(`.${styles.full}`, { opacity: 0 }, { opacity: 1, duration: 1.6, delay: 0.2, ease: "power2.out" });
        gsap.fromTo(`.${styles.media}`, { scale: 1.035 }, { scale: 1, duration: 2.4, ease: "expo.out" });
        // Scroll away: the image drifts, a veil darkens it, the words leave first.
        const tl = gsap.timeline({
          defaults: { ease: "none" },
          scrollTrigger: { trigger: root.current, start: "top top", end: "bottom top", scrub: 0.4 },
        });
        tl.to(`.${styles.drift}`, { yPercent: 6 }, 0)
          .to(`.${styles.veil}`, { opacity: 0.55 }, 0)
          .to(`.${styles.top}`, { opacity: 0, y: -40, duration: 0.45 }, 0)
          .to(`.${styles.bottom}`, { opacity: 0, duration: 0.35 }, 0.05);
      });
      return () => mm.revert();
    },
    { scope: root, dependencies: [motionOn], revertOnUpdate: true },
  );

  return (
    <section ref={root} id="hero" className={styles.hero} aria-labelledby="hero-title">
      <div className={styles.drift} aria-hidden="true">
        <div className={styles.media}>
          <Still id="K01-base" phoneCrop="portrait" alt="" priority className={styles.base} />
          <Still id="K01-full" phoneCrop="portrait" alt="" className={styles.full} />
        </div>
      </div>
      <div className={styles.veil} aria-hidden="true" />
      <div className={styles.top}>
        <p className={`t-eyebrow ${styles.eyebrow}`}>{hero.eyebrow}</p>
        <h1 id="hero-title" className={`t-h1 ${styles.title}`}>
          {hero.headline}
        </h1>
        <p className={`t-lead ${styles.lead}`}>{hero.lead}</p>
      </div>
      <div className={styles.bottom}>
        <Link href="/reserve" className={`btn btn-primary ${styles.cta}`}>
          {site.ctaLabel}
        </Link>
        <p className={`t-label ${styles.note}`}>{hero.ctaNote}</p>
      </div>
    </section>
  );
}
