"use client";

import { useRef } from "react";
import { SweetSpotEdge } from "@/components/graphics/SweetSpotEdge";
import { SweetSpotField, addSweetSpotReveal } from "@/components/graphics/SweetSpotField";
import { Still, hasStill } from "@/components/media/Still";
import { useMotion } from "@/components/motion/MotionProvider";
import { PinnedChapter } from "@/components/motion/PinnedChapter";
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

/** Where the phone crop of K14 applies: below the pinned layout's 900 px, as the stacked layout's 4:5 frame. */
const PHONE = "(max-width: 899px)";

/** Already at or past a reveal's line when the page hydrates (a reload mid-page, a hash link): leave it be. */
const past = (el: Element, pct: number) => el.getBoundingClientRect().top < (window.innerHeight * pct) / 100;

/**
 * Sweet spot, the payoff (owner, 2026-10-28: a climactic rise), and since 2026-11-03 a pinned chapter (owner: "When
 * scrolling down sweet spot section the page doesn't pause and there is no animation?"). From 900 px, with motion: the
 * page holds on one screen while the face comes up out of the dark (K14 settles, 1.1 to 1), a soft band of warm light
 * sweeps across the weave from the sweet spot out to the rim (a colour-dodge layer, so it lights only the lit carbon
 * and never the studio beyond the edge), the amber 1 mm line draws along the rim where the flat face ends (traced from
 * the render, SweetSpotEdge), and the two numbers arrive in turn, "Nearly 99%" with the light, "1 mm" with the line.
 * The heading is on screen from the first frame. Below 900 px: the headline, the image (its line drawn as it enters),
 * then the words, rising on entry. Reduced motion and the server render: the final state, every word visible, the
 * line drawn. Its Skip link lands on Surface.
 */
export function SweetSpot() {
  const beat = useRef<HTMLDivElement>(null);
  const { motionOn } = useMotion();

  // Below the pin (phones, tablets): no scrub; the image settles and its line draws as it enters, the words rise.
  useGSAP(
    () => {
      const el = beat.current;
      if (!motionOn || !el) return;
      const q = gsap.utils.selector(el);
      const mm = gsap.matchMedia();
      mm.add("(prefers-reduced-motion: no-preference) and (max-width: 899px)", () => {
        const media = q(`.${styles.media}`)[0];
        if (media && !past(media, 80)) {
          const tl = gsap.timeline({ scrollTrigger: { trigger: media, start: "top 80%", once: true } });
          if (K14) {
            tl.fromTo(q(`.${styles.still}`), { scale: 1.08 }, { scale: 1, duration: 1.6, ease: "power2.out", immediateRender: true }, 0).fromTo(
              q("[data-sweet-line]"),
              { strokeDasharray: 1, strokeDashoffset: -1 },
              { strokeDashoffset: 0, duration: 1.1, ease: "power2.inOut", immediateRender: true },
              0.4,
            );
          } else {
            addSweetSpotReveal(tl, el, "fade", 0);
          }
        }
        for (const b of q("[data-rise]")) {
          if (past(b, 85)) continue;
          gsap.from(b, { opacity: 0, y: 16, duration: 0.7, ease: "power3.out", scrollTrigger: { trigger: b, start: "top 85%", once: true } });
        }
      });
      return () => mm.revert();
    },
    { scope: beat, dependencies: [motionOn], revertOnUpdate: true },
  );

  return (
    <PinnedChapter
      id="sweet-spot"
      nextId="surface"
      labelledBy="sweet-spot-eyebrow sweet-spot-title"
      className={`pin-layered ${styles.chapter}`}
      length={1.4}
      build={(tl) => {
        // Opacity only for the words, never visibility: the claim stays in the accessibility tree before it arrives.
        const shown = { opacity: 1, y: 0, immediateRender: true } as const;
        if (K14) {
          // The face comes up out of the dark as the frame settles.
          tl.fromTo(`.${styles.frame}`, { scale: 1.1 }, { scale: 1, duration: 0.5, ease: "power2.out", immediateRender: true }, 0)
            .fromTo(`.${styles.veil}`, { opacity: 0.62 }, { opacity: 0, duration: 0.3, ease: "power1.out", immediateRender: true }, 0)
            // The light: a soft warm band crossing the weave from the sweet spot out past the rim (transform only).
            .fromTo(`.${styles.light}`, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.06, immediateRender: true }, 0.1)
            .fromTo(`.${styles.light}`, { yPercent: 210 }, { yPercent: -160, duration: 0.46, ease: "power1.inOut", immediateRender: true }, 0.1)
            .to(`.${styles.light}`, { autoAlpha: 0, duration: 0.08 }, 0.5)
            // The 1 mm line draws along the rim, where the flat face ends, from the lit side (the path's end, on the right)
            // back toward the words, as the light reaches the edge.
            .fromTo(`.${styles.edge}`, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.02, immediateRender: true }, 0.34)
            .fromTo(
              `.${styles.edge} [data-sweet-line]`,
              { strokeDasharray: 1, strokeDashoffset: -1 },
              { strokeDashoffset: 0, duration: 0.26, ease: "power1.inOut", immediateRender: true },
              0.34,
            );
        } else {
          if (beat.current) addSweetSpotReveal(tl, beat.current, "scrub", 0);
        }
        // The words: the lines first, then the numbers in turn, the share with the light, the border with the line.
        tl.fromTo(`.${styles.body}`, { opacity: 0, y: 14 }, { ...shown, duration: 0.1 }, 0.16)
          .fromTo(`.${styles.share}`, { opacity: 0, y: 14 }, { ...shown, duration: 0.1 }, 0.46)
          .fromTo(`.${styles.inset}`, { opacity: 0, y: 14 }, { ...shown, duration: 0.1 }, 0.6)
          // It holds while the stage is still pinned, then scrolls on into Surface.
          .to({}, { duration: 0.3 }, 0.7);
      }}
    >
      <div ref={beat} className={`beat ${styles.beat}`} data-media={K14 ? "still" : "graphic"}>
        <div className={styles.media} aria-hidden={K14 ? undefined : true}>
          {K14 ? (
            <div className={styles.frame}>
              <Still id="K14" phoneCrop="portrait" phoneMedia={PHONE} phoneSizes="(min-width: 700px) 560px, 100vw" alt={sweetSpot.imageAlt(SWEET_CLAIM)} className={styles.still} sizes="100vw" />
              <div className={styles.veil} aria-hidden="true" />
              <div className={styles.light} aria-hidden="true" />
              <div className={styles.edge} aria-hidden="true">
                <SweetSpotEdge crop="wide" className={styles.edgeWide} />
                <SweetSpotEdge crop="portrait" className={styles.edgePortrait} />
              </div>
            </div>
          ) : (
            <SweetSpotField className={styles.graphic} />
          )}
        </div>

        <div className={styles.words}>
          <div className={styles.head} data-rise="">
            <p id="sweet-spot-eyebrow" className="t-eyebrow">
              {sweetSpot.eyebrow}
            </p>
            <h2 id="sweet-spot-title" className={`t-h2 ${styles.title}`}>
              {sweetSpot.headline}
            </h2>
          </div>

          <div className={`${styles.body}`} data-rise="">
            <p className="t-lead">{sweetSpot.lines[0]}</p>
            <p className={`t-lead ${styles.bright}`}>{sweetSpot.lines[1]}</p>
          </div>

          {/* The numbers come from the geometry (graphics-sweetspot.ts SWEET_CLAIM), never typed by hand. */}
          <ul className={styles.lockup} data-rise="">
            <li className={`${styles.stat} ${styles.share}`}>
              <span className={`t-stat ${styles.value}`}>
                {/* "Nearly" at the unit's size, its space inside it, so "Nearly 99%" reads as one figure */}
                {SWEET_CLAIM.nearly ? <span className={`t-unit ${styles.nearly}`}>{`${sweetSpot.share.nearly} `}</span> : null}
                {SWEET_CLAIM.share}
                <span className={`t-unit ${styles.pct}`}>{sweetSpot.share.unit}</span>
              </span>{" "}
              <span className={`t-label ${styles.label}`}>{sweetSpot.share.label}</span>
            </li>
            <li className={`${styles.stat} ${styles.inset}`}>
              <span className={`t-stat ${styles.value}`}>
                {SWEET_CLAIM.inset}
                <span className="t-unit">{sweetSpot.inset.unit}</span>
              </span>{" "}
              <span className={`t-label ${styles.label}`}>{sweetSpot.inset.label}</span>
            </li>
          </ul>
        </div>
      </div>
    </PinnedChapter>
  );
}
