"use client";

import { useRef } from "react";
import { GripContact } from "@/components/graphics/GripContact";
import { SliceBounce } from "@/components/graphics/SliceBounce";
import { Still, hasStill } from "@/components/media/Still";
import { useMotion } from "@/components/motion/MotionProvider";
import { surface } from "@/content/copy";
import { gsap, useGSAP } from "@/lib/gsap";
import styles from "./Surface.module.css";

/** K17, the roughness macro (a padel ball pressed on the face at the instant of a slice); the section reads without it. */
const K17 = hasStill("K17-full");

/** Already at or past a reveal's line when the page hydrates (a reload mid-page, a hash link): leave it be. */
const past = (el: Element, pct: number) => el.getBoundingClientRect().top < (window.innerHeight * pct) / 100;

/** The words rise once, staggered. Opacity and a short rise only: the claim stays in the accessibility tree. */
function rise(targets: Element[], trigger: Element, pct: number) {
  if (!targets.length || past(trigger, pct)) return;
  return gsap.from(targets, {
    opacity: 0,
    y: 16,
    duration: 0.7,
    ease: "power3.out",
    stagger: 0.06,
    scrollTrigger: { trigger, start: `top ${pct}%`, once: true },
  });
}

/**
 * Surface (owner, 2026-11-02: "unique surface roughness"), the second payoff after the sweet spot and before Feel: what
 * the face does to the ball. K17 full bleed (the felt dragged across the moulded texture at the instant of a slice),
 * the words and the two numbers under it, then G17 (SliceBounce): the same slice after the bounce, off a standard face
 * and off ours, scrubbed by scroll. Not pinned (no Skip link). Phones: the headline, K17's 4:5 crop, the words, the
 * numbers, then G17's portrait framing. Reduced motion and the server render: the final state.
 */
export function Surface() {
  const root = useRef<HTMLElement>(null);
  const { motionOn } = useMotion();

  useGSAP(
    () => {
      const el = root.current;
      if (!motionOn || !el) return;
      const q = gsap.utils.selector(el);
      const media = q(`.${styles.media}`)[0];
      const still = q(`.${styles.still}`);
      const blocks = q("[data-rise]");
      const mm = gsap.matchMedia();
      mm.add("(prefers-reduced-motion: no-preference) and (min-width: 1000px)", () => {
        // K17 settles as the section scrolls in (scale only: it carries the alt text, so it is never hidden).
        if (media && still.length)
          gsap.fromTo(
            still,
            { scale: 1.08 },
            { scale: 1, ease: "none", immediateRender: true, scrollTrigger: { trigger: media, start: "top 85%", end: "bottom 40%", scrub: 0.5 } },
          );
        for (const b of blocks) rise([b], b, 85);
      });
      mm.add("(prefers-reduced-motion: no-preference) and (max-width: 999px)", () => {
        if (media && still.length && !past(media, 80))
          gsap.fromTo(still, { scale: 1.08 }, { scale: 1, duration: 1.6, ease: "power2.out", scrollTrigger: { trigger: media, start: "top 80%", once: true } });
        for (const b of blocks) rise([b], b, 85);
      });
      return () => mm.revert();
    },
    { scope: root, dependencies: [motionOn], revertOnUpdate: true },
  );

  return (
    <section
      ref={root}
      className={styles.section}
      id="surface"
      tabIndex={-1}
      data-media={K17 ? "still" : "none"}
      aria-labelledby="surface-eyebrow surface-title"
    >
      <div className={styles.head} data-rise="">
        <p id="surface-eyebrow" className="t-eyebrow">
          {surface.eyebrow}
        </p>
        <h2 id="surface-title" className={`t-h2 ${styles.title}`}>
          {surface.headline}
        </h2>
      </div>

      {K17 ? (
        <div className={styles.media}>
          <div className={styles.frame}>
            <Still
              id="K17-full"
              phoneCrop="phone"
              phoneMedia="(max-width: 999px)"
              phoneSizes="(min-width: 700px) 560px, 100vw"
              alt={surface.imageAlt}
              className={styles.still}
              sizes="100vw"
            />
          </div>
        </div>
      ) : null}

      <div className={styles.body} data-rise="">
        <p className="t-lead">{surface.lead}</p>
        <p className={`t-lead ${styles.bright}`}>{surface.bright}</p>
        <p className={`t-body ${styles.quiet}`}>{surface.texture}</p>
      </div>

      {/* G18 (how the face grips: the mechanism under K17), then the numbers, which come from specs.ts (provisional
          until the factory's), never typed here. Wide: both in the right-hand column, beside the words. */}
      <div className={styles.aside}>
      <GripContact legend={surface.contact} className={styles.contact} />
      <ul className={styles.lockup} data-rise="">
        {surface.stats.map((s) => (
          <li key={s.label} className={styles.stat}>
            <span className={`t-stat ${styles.value}`}>
              {s.value}
              {s.unit ? <span className="t-unit">{s.unit}</span> : null}
            </span>{" "}
            <span className={`t-label ${styles.label}`}>{s.label}</span>
          </li>
        ))}
      </ul>
      </div>

      <div className={styles.graph}>
        <h3 className={`t-h3 ${styles.graphTitle}`} data-rise="">
          {surface.graphic.title}
        </h3>
        <SliceBounce className={styles.slice} />
      </div>
    </section>
  );
}
