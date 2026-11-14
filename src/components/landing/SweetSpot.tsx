"use client";

import { useRef, type CSSProperties } from "react";
import { SweetSpotField, addSweetSpotReveal } from "@/components/graphics/SweetSpotField";
import { Still, hasStill } from "@/components/media/Still";
import { useMotion } from "@/components/motion/MotionProvider";
import { PinnedChapter } from "@/components/motion/PinnedChapter";
import { sweetSpot } from "@/content/copy";
import { SWEET_CLAIM } from "@/lib/graphics-sweetspot";
import { gsap, useGSAP } from "@/lib/gsap";
import styles from "./SweetSpot.module.css";

/**
 * The image (owner, 2026-11-14: option C of the Edge to edge preview, "a ball at the very edge makes most sense"): a
 * padel ball struck at the face's widest point, right at the edge, then soft rings across the face, then the camera
 * pulls back to the whole racket. Three pixel-matched renders stacked (E2E-C-full, E2E-C-rings, E2E-Cwide-rings), each
 * with its Pace twin; the whole racket also has its Naked twin (the Grip toggle). The drawing (G15) stands in until the
 * renders are exported. It replaced K14, the raking-light macro, and its traced 1 mm line.
 */
const E2E = hasStill("E2E-C-full", "ewide") && hasStill("E2E-C-rings", "ewide") && hasStill("E2E-Cwide-rings", "ewide");

/** The three layers, bottom to top; the top one is the final frame (reduced motion, the server render). */
const LAYERS: { id: string; bare?: { id: string } | false; pos?: string }[] = [
  { id: "E2E-C-full", bare: false, pos: "30% 50%" },
  { id: "E2E-C-rings", bare: false, pos: "30% 50%" },
  { id: "E2E-Cwide-rings", bare: { id: "E2E-Cwide-nogrip-rings" } },
];

/** Where the phone frames (2160 x 3840, reframed round the ball) apply: below the pinned layout's 900 px. */
const PHONE = "(max-width: 899px)";
const layer = (i: number) => `.${styles.layer}[data-layer="${i}"]`;

/** The scrubbed sequence (0 to 1), pinned from 900 px and, below it, while the image crosses the screen. */
function play(tl: gsap.core.Timeline) {
  tl.fromTo([layer(0), layer(1)], { scale: 1.06 }, { scale: 1, duration: 0.4, ease: "power2.out", immediateRender: true }, 0)
    // the rings come up over the face
    .fromTo(layer(1), { opacity: 0 }, { opacity: 1, duration: 0.22, ease: "power1.inOut", immediateRender: true }, 0.12)
    // then the camera pulls back: the close frame grows and goes, the whole racket settles in
    .to([layer(0), layer(1)], { scale: 1.12, duration: 0.3, ease: "power1.in" }, 0.48)
    .fromTo(layer(2), { opacity: 0, scale: 1.18 }, { opacity: 1, scale: 1, duration: 0.3, ease: "power2.out", immediateRender: true }, 0.5);
}

/** Runs once when the element's top reaches the middle of the screen. */
function onceAtMiddle(el: Element, onEnter: () => void) {
  gsap.timeline({ scrollTrigger: { trigger: el, start: "top 50%", once: true, onEnter } });
}

/** Already at or past a reveal's line when the page hydrates (a reload mid-page, a hash link): leave it be. */
const past = (el: Element, pct: number) => el.getBoundingClientRect().top < (window.innerHeight * pct) / 100;

/**
 * Sweet spot, the payoff (owner, 2026-10-28: a climactic rise), a pinned chapter since 2026-11-03. From 900 px, with
 * motion: the page holds on one screen while the ball meets the face at its edge, soft rings come up across the face,
 * and the camera pulls back to the whole racket, the two numbers arriving in turn, "Nearly 99%" with the rings, "1 mm"
 * with the whole racket. The heading is on screen from the first frame. Below 900 px: the headline, the image (the
 * same sequence, played once as it comes into view), then the words, rising on entry. Reduced motion and the
 * server render: the final frame and every word. Its Skip link lands on Surface.
 */
export function SweetSpot() {
  const beat = useRef<HTMLDivElement>(null);
  const { motionOn } = useMotion();

  // Below the pin (phones, tablets): the sequence plays once as the image comes into view; the words rise.
  useGSAP(
    () => {
      const el = beat.current;
      if (!motionOn || !el) return;
      const q = gsap.utils.selector(el);
      const mm = gsap.matchMedia();
      mm.add("(prefers-reduced-motion: no-preference) and (max-width: 899px)", () => {
        const media = q(`.${styles.media}`)[0];
        if (media && E2E) {
          // Played once as the image comes into view, not scrubbed: a phone screen scrolls the 4:5 frame past in less
          // than a screen, so a scrub would pull back to the whole racket only as it leaves.
          if (!past(media, 50)) {
            const tl = gsap.timeline({ paused: true });
            play(tl);
            tl.timeScale(0.32);
            onceAtMiddle(media, () => tl.play());
          }
        } else if (media && !past(media, 80)) {
          const tl = gsap.timeline({ scrollTrigger: { trigger: media, start: "top 80%", once: true } });
          addSweetSpotReveal(tl, el, "fade", 0);
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
      length={1.8}
      build={(tl) => {
        // Opacity only for the words, never visibility: the claim stays in the accessibility tree before it arrives.
        const shown = { opacity: 1, y: 0, immediateRender: true } as const;
        if (E2E) play(tl);
        else if (beat.current) addSweetSpotReveal(tl, beat.current, "scrub", 0);
        // The words: the lines first, then the numbers in turn, the share with the rings, the border with the racket.
        tl.fromTo(`.${styles.body}`, { opacity: 0, y: 14 }, { ...shown, duration: 0.1 }, 0.14)
          .fromTo(`.${styles.share}`, { opacity: 0, y: 14 }, { ...shown, duration: 0.1 }, 0.3)
          .fromTo(`.${styles.inset}`, { opacity: 0, y: 14 }, { ...shown, duration: 0.1 }, 0.68)
          // It holds while the stage is still pinned, then scrolls on into Surface.
          .to({}, { duration: 0.2 }, 0.8);
      }}
    >
      <div ref={beat} className={`beat ${styles.beat}`} data-media={E2E ? "still" : "graphic"}>
        <div className={styles.media} aria-hidden={E2E ? undefined : true}>
          {E2E ? (
            <div className={styles.frame}>
              {LAYERS.map((l, i) => (
                <div key={l.id} className={styles.layer} data-layer={i} style={l.pos ? ({ "--pos": l.pos } as CSSProperties) : undefined}>
                  <Still
                    id={l.id}
                    crop="ewide"
                    phoneCrop="ephone"
                    phoneMedia={PHONE}
                    phoneSizes="(min-width: 700px) 560px, 100vw"
                    sizes="100vw"
                    bare={l.bare}
                    // Only the final frame is described; the two under it are the same moment, closer in.
                    alt={i === LAYERS.length - 1 ? sweetSpot.imageAlt : ""}
                    className={styles.still}
                  />
                </div>
              ))}
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
