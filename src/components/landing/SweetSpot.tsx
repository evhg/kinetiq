"use client";

import { useRef } from "react";
import { SweetSpotField, addSweetSpotReveal } from "@/components/graphics/SweetSpotField";
import { Still, hasStill } from "@/components/media/Still";
import { useMotion } from "@/components/motion/MotionProvider";
import { sweetSpot } from "@/content/copy";
import { SWEET_CLAIM } from "@/lib/graphics-sweetspot";
import { gsap, useGSAP } from "@/lib/gsap";
import styles from "./SweetSpot.module.css";

/**
 * K14 (a raking-light macro of the face running out to the rim, in the K04 language the owner feels) takes the
 * image's place once scripts/stills.mjs has exported it; until then G15, the drawing. The upright K12 racket is off the
 * landing (owner, 2026-10-28: "I dont like the edge to edge hero"); /reserve keeps K12-base.
 */
const K14 = hasStill("K14");

/** Already at or past a reveal's line when the page hydrates (a reload mid-page, a hash link): leave it be. */
const past = (el: Element, pct: number) => el.getBoundingClientRect().top < (window.innerHeight * pct) / 100;

/**
 * The words rise once, staggered: the eyebrow and headline, the two lines, then the numbers. Opacity only, never
 * visibility: the claim stays in the accessibility tree before the section is scrolled to.
 */
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
 * Sweet spot, the payoff (owner, 2026-10-28: a climactic rise): after how it is made, from the unibody to the sealed
 * core, "Edge to edge." says what all of it gives the player. With G15: on wide screens the words take the left five
 * columns and the drawing stands on the right; as the section scrolls in, the light spreads across its face to 4 mm
 * from the edge, then the words arrive. With K14: the macro full bleed across the top, settling as it scrolls in, the
 * words and the numbers under it. Phones: the headline, the image, then the words. Not pinned. Reduced motion and the
 * server render: the final state.
 */
export function SweetSpot() {
  const root = useRef<HTMLElement>(null);
  const { motionOn } = useMotion();

  useGSAP(
    () => {
      const el = root.current;
      if (!motionOn || !el) return;
      const q = gsap.utils.selector(el);
      const media = q(`.${styles.media}`)[0];
      const blocks = q("[data-rise]");
      const mm = gsap.matchMedia();
      const image = (tl: gsap.core.Timeline, scrub: boolean) => {
        if (K14) {
          // the macro settles as it arrives (scale only: it carries the alt text, so it is never hidden)
          tl.fromTo(q(`.${styles.still}`), { scale: 1.08 }, { scale: 1, duration: scrub ? 1 : 1.6, ease: scrub ? "none" : "power2.out", immediateRender: true }, 0);
        } else {
          addSweetSpotReveal(tl, el, scrub ? "scrub" : "fade", 0);
        }
      };
      mm.add("(prefers-reduced-motion: no-preference) and (min-width: 1000px)", () => {
        // From the section's top at 85% of the screen to its centre at the screen's centre.
        const tl = gsap.timeline({
          defaults: { ease: "none" },
          scrollTrigger: { trigger: el, start: "top 85%", end: "center center", scrub: 0.5 },
        });
        image(tl, true);
        tl.to({}, { duration: 0.05 }); // a short hold at the end, so the detail lands before the scrub runs out
        rise(blocks, blocks[0], 55);
      });
      mm.add("(prefers-reduced-motion: no-preference) and (max-width: 999px)", () => {
        // Phones: no scrub. The image fades in on entry, the words rise block by block.
        if (media && !past(media, 80)) {
          image(gsap.timeline({ scrollTrigger: { trigger: media, start: "top 80%", once: true } }), false);
        }
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
      id="sweet-spot"
      tabIndex={-1}
      data-media={K14 ? "still" : "graphic"}
      aria-labelledby="sweet-spot-eyebrow sweet-spot-title"
    >
      <div className={styles.head} data-rise="">
        <p id="sweet-spot-eyebrow" className="t-eyebrow">
          {sweetSpot.eyebrow}
        </p>
        <h2 id="sweet-spot-title" className={`t-h2 ${styles.title}`}>
          {sweetSpot.headline}
        </h2>
      </div>

      <div className={styles.media}>
        {K14 ? (
          <div className={styles.frame}>
            <Still id="K14" phoneCrop="portrait" alt={sweetSpot.imageAlt(SWEET_CLAIM)} className={styles.still} sizes="100vw" />
          </div>
        ) : (
          <SweetSpotField className={styles.graphic} />
        )}
      </div>

      <div className={styles.body} data-rise="">
        <p className="t-lead">{sweetSpot.lines[0]}</p>
        <p className={`t-lead ${styles.bright}`}>{sweetSpot.lines[1]}</p>
      </div>

      {/* The numbers come from the geometry (graphics-sweetspot.ts SWEET_CLAIM), never typed by hand. */}
      <ul className={styles.lockup} data-rise="">
        <li className={styles.stat}>
          <span className={`t-stat ${styles.value}`}>
            {/* "Nearly" at the unit's size, its space inside it, so "Nearly 94%" reads as one figure */}
            {SWEET_CLAIM.nearly ? <span className={`t-unit ${styles.nearly}`}>{`${sweetSpot.share.nearly} `}</span> : null}
            {SWEET_CLAIM.share}
            <span className={`t-unit ${styles.pct}`}>{sweetSpot.share.unit}</span>
          </span>{" "}
          <span className={`t-label ${styles.label}`}>{sweetSpot.share.label}</span>
        </li>
        <li className={styles.stat}>
          <span className={`t-stat ${styles.value}`}>
            {SWEET_CLAIM.inset}
            <span className="t-unit">{sweetSpot.inset.unit}</span>
          </span>{" "}
          <span className={`t-label ${styles.label}`}>{sweetSpot.inset.label}</span>
        </li>
      </ul>
    </section>
  );
}
