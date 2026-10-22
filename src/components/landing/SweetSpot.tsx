"use client";

import { useRef } from "react";
import { SweetSpotField, addSweetSpotReveal } from "@/components/graphics/SweetSpotField";
import { Still, hasStill } from "@/components/media/Still";
import { useMotion } from "@/components/motion/MotionProvider";
import { sweetNote, sweetSpot } from "@/content/copy";
import { SWEET_CLAIM } from "@/lib/graphics-sweetspot";
import { gsap, useGSAP } from "@/lib/gsap";
import styles from "./SweetSpot.module.css";

/** K12 takes the image's place once scripts/stills.mjs has exported both its passes; until then, G15. */
const K12 = hasStill("K12-base") && hasStill("K12-full");

/** Already at or past a reveal's line when the page hydrates (a reload mid-page, a hash link): leave it be. */
const past = (el: Element, pct: number) => el.getBoundingClientRect().top < (window.innerHeight * pct) / 100;

/**
 * The words rise once, staggered: the eyebrow and headline, the two lines, the numbers, the fine print. Opacity
 * only, never visibility: the claim, its ‡ marks and the fine print stay in the accessibility tree and in the tab
 * order before the section is scrolled to (a focus inside it finishes the rise at once, SweetSpot below).
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
 * Sweet spot, the first idea after the hero: "Edge to edge." On wide screens the words take the left five
 * columns and the racket stands face-on on the right, where the hero's racket stood; as the section scrolls in,
 * the racket rises and the light spreads across its face to 4 mm from the edge, then the words arrive. Phones:
 * the headline, the image, then the words. Not pinned. The image is K12 (base, then the lit pass crossfading
 * over it) once exported, G15 until then. Reduced motion and the server render: the final state.
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
      const words: (gsap.core.Tween | undefined)[] = [];
      const mm = gsap.matchMedia();
      const image = (tl: gsap.core.Timeline, scrub: boolean) => {
        // Wide screens: the racket rises only as the hero's fades out (Hero.tsx, gone at 32% of the hero scrolled), so
        // the two cross in a short, low-light fade and are never both seen whole (0.12 here is about 0.1 of a screen).
        const at = scrub ? 0.12 : 0;
        if (K12) {
          // the base carries the alt text: opacity only, so it stays in the accessibility tree
          tl.fromTo(q(`.${styles.base}`), { opacity: 0, scale: 1.03 }, { opacity: 1, scale: 1, duration: scrub ? 0.25 : 0.8, ease: scrub ? "none" : "power2.out", immediateRender: true }, at)
            // the lit pass: the sweet spot lights up over the dark racket
            .fromTo(q(`.${styles.full}`), { autoAlpha: 0 }, { autoAlpha: 1, duration: scrub ? 0.45 : 1.2, ease: scrub ? "none" : "power2.inOut", immediateRender: true }, scrub ? at + 0.25 : 0.5);
        } else {
          addSweetSpotReveal(tl, el, scrub ? "scrub" : "fade", at);
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
        words.push(rise(blocks, blocks[0], 55));
      });
      mm.add("(prefers-reduced-motion: no-preference) and (max-width: 999px)", () => {
        // Phones: no scrub. The image fades in on entry, the words rise block by block.
        if (media && !past(media, 80)) {
          image(gsap.timeline({ scrollTrigger: { trigger: media, start: "top 80%", once: true } }), false);
        }
        for (const b of blocks) words.push(rise([b], b, 85));
      });
      // Keyboard: Tab can reach a ‡ mark before the section has been scrolled to. Focus finishes the words' rise at
      // once (no animation on keyboard-triggered moves), so a focused mark is never invisible.
      const settle = () => {
        for (const t of words) t?.progress(1);
      };
      el.addEventListener("focusin", settle);
      return () => {
        el.removeEventListener("focusin", settle);
        mm.revert();
      };
    },
    { scope: root, dependencies: [motionOn], revertOnUpdate: true },
  );

  const mark = (
    <a href={`#${sweetNote.id}`} className="footmark" aria-label={sweetNote.label}>
      {sweetNote.mark}
    </a>
  );

  return (
    <section
      ref={root}
      id="sweet-spot"
      className={styles.section}
      data-media={K12 ? "still" : "graphic"}
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
        {K12 ? (
          <div className={styles.still}>
            <Still id="K12-base" phoneCrop="portrait" alt={sweetSpot.imageAlt(SWEET_CLAIM)} className={styles.base} sizes="100vw" phoneSizes="100vw" />
            <Still id="K12-full" phoneCrop="portrait" alt="" className={styles.full} sizes="100vw" phoneSizes="100vw" />
          </div>
        ) : (
          <SweetSpotField className={styles.graphic} />
        )}
        <p className={`t-fine ${styles.caption}`}>{sweetSpot.caption}</p>
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
          <span className={`t-label ${styles.label}`}>
            {sweetSpot.share.label}
            {mark}
          </span>
        </li>
        <li className={styles.stat}>
          <span className={`t-stat ${styles.value}`}>
            {SWEET_CLAIM.inset}
            <span className="t-unit">{sweetSpot.inset.unit}</span>
          </span>{" "}
          <span className={`t-label ${styles.label}`}>
            {sweetSpot.inset.label}
            {mark}
          </span>
        </li>
      </ul>

      <p id={sweetNote.id} className={`t-fine ${styles.fine}`} data-rise="">
        <span className={styles.mark}>{sweetNote.mark}</span>
        {sweetSpot.fine(SWEET_CLAIM)}
      </p>
    </section>
  );
}
