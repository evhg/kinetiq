"use client";

import Link from "next/link";
import { useRef } from "react";
import { Still } from "@/components/media/Still";
import { useMotion } from "@/components/motion/MotionProvider";
import { Hyphens } from "@/components/text/Hyphens";
import { hero, lifeNote } from "@/content/copy";
import { site } from "@/content/site";
import { gsap, useGSAP } from "@/lib/gsap";
import styles from "./Hero.module.css";

/**
 * Hero: K01 rises out of the dark (base, then the beam), one CTA. Wide screens set the words, Reserve Now
 * and the price line in the left seven columns beside the racket, which stands large on the right; phones
 * keep the words above the racket and Reserve Now on the floor below it.
 */
export function Hero() {
  const root = useRef<HTMLElement>(null);
  const { motionOn } = useMotion();

  useGSAP(
    (_, contextSafe) => {
      if (!motionOn) return;
      const mm = gsap.matchMedia();
      mm.add("(prefers-reduced-motion: no-preference)", () => {
        // The frame settles from the scale the CSS painted first (Hero.module.css), so nothing jumps.
        gsap.fromTo(`.${styles.media}`, { scale: 1.035 }, { scale: 1, duration: 2.4, ease: "expo.out" });
        // The beam: the lit render fades over the dark base once its image has decoded, never before.
        const full = root.current?.querySelector<HTMLElement>(`.${styles.full}`);
        const img = full?.querySelector("img");
        let live = true;
        const beam = contextSafe!(() => {
          if (live && full) gsap.fromTo(full, { opacity: 0 }, { opacity: 1, duration: 1.6, delay: 0.2, ease: "power2.out" });
        });
        if (img?.complete && img.naturalWidth > 0) beam();
        else img?.decode().then(beam, beam);
        // Scroll away: the image drifts and a veil darkens it. The words and the button simply scroll
        // with the page, so Reserve Now stays fully opaque.
        const tl = gsap.timeline({
          defaults: { ease: "none" },
          scrollTrigger: { trigger: root.current, start: "top top", end: "bottom top", scrub: 0.4 },
        });
        tl.to(`.${styles.drift}`, { yPercent: 6 }, 0).to(`.${styles.veil}`, { opacity: 0.55 }, 0);
        return () => {
          live = false;
        };
      });
      // Wide screens: the sweet spot's racket rises beside where this one stands, so this one fades out first (between
      // 10% and 32% of the hero scrolled) and the two only cross at low light (SweetSpot.tsx starts its racket late).
      mm.add("(prefers-reduced-motion: no-preference) and (min-width: 1000px)", () => {
        gsap.fromTo(
          `.${styles.drift}`,
          { opacity: 1 },
          { opacity: 0, ease: "none", scrollTrigger: { trigger: root.current, start: "top -10%", end: "top -32%", scrub: 0.4 } },
        );
      });
      return () => mm.revert();
    },
    { scope: root, dependencies: [motionOn], revertOnUpdate: true },
  );

  return (
    <section ref={root} id="hero" className={styles.hero} aria-labelledby="hero-title">
      <div className={styles.drift} aria-hidden="true">
        <div className={styles.media}>
          {/* Wide: the close beam camera (the racket spans 27-80% of the frame). Phones: their own 9:16 master. */}
          <Still id="K01-base" phoneId="K01-hero-base-phone" phoneCrop="portrait" alt="" priority className={styles.base} />
          <Still id="K01-full" phoneId="K01-hero-full-phone" phoneCrop="portrait" alt="" loading="eager" fetchPriority="low" className={styles.full} />
        </div>
      </div>
      <div className={styles.veil} aria-hidden="true" />
      <div className={styles.scrim} aria-hidden="true" />
      <div className={styles.top}>
        <p className={`t-eyebrow ${styles.eyebrow}`}>{hero.eyebrow}</p>
        <h1 id="hero-title" className={`t-h1 ${styles.title}`}>
          {hero.headline}
        </h1>
        <p className={`t-lead ${styles.lead}`}>
          <Hyphens text={hero.lead} />{" "}
          <span className={styles.life}>
            {hero.life}
            <a href={`#${lifeNote.id}`} className="footmark" aria-label={lifeNote.label}>
              {lifeNote.mark}
            </a>
          </span>
        </p>
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
