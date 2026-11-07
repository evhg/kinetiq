"use client";

import { useRef } from "react";
import { hasStill, Still } from "@/components/media/Still";
import { useMotion } from "@/components/motion/MotionProvider";
import { gsap, useGSAP } from "@/lib/gsap";
import styles from "./Editions.module.css";

/** The settle runs only with motion; reduced motion and the server render show the final state. */
const SETTLE = "(prefers-reduced-motion: no-preference)";

type Props = { id: string; crop: string; sizes: string };

/**
 * An edition card's racket, in K04's language (owner, 2026-11-07: "make the whole racket renders look more like the
 * moulded holes graphic including the animation"; Holes.tsx's FLOW is the model): as the card scrolls in, the frame
 * settles from close (scale 1.12) to rest, scrubbed by scroll. Where the render has two passes exported for this crop
 * (`<id>-base` and `<id>-full`, e.g. "K11-single-base" and "K11-single-full", each with its "-pace" and "-nogrip" twins
 * by the usual names), the base pass lies under the full one and the full pass comes up during the settle, as K04's
 * ring of light does; otherwise the single still settles alone. Transform and opacity only, on layers inside the
 * card's fixed-ratio frame, so nothing shifts. Server render and reduced motion: the full pass at scale 1. The card
 * reads without the image (Still renders nothing until a still is exported).
 */
export function EditionStill({ id, crop, sizes }: Props) {
  const root = useRef<HTMLDivElement>(null);
  const { motionOn } = useMotion();
  const layered = hasStill(`${id}-base`, crop) && hasStill(`${id}-full`, crop);

  useGSAP(
    () => {
      if (!motionOn) return;
      const mm = gsap.matchMedia();
      mm.add(SETTLE, () => {
        const frame = root.current;
        if (!frame) return;
        const tl = gsap.timeline({
          defaults: { ease: "none" },
          scrollTrigger: { trigger: frame, start: "top bottom", end: "top 35%", scrub: 0.6 },
        });
        tl.fromTo(frame.querySelector(`.${styles.settle}`), { scale: 1.12 }, { scale: 1, duration: 1 }, 0);
        const full = frame.querySelector(`.${styles.full}`);
        if (full) tl.fromTo(full, { opacity: 0 }, { opacity: 1, duration: 0.55 }, 0.2);
      });
      return () => mm.revert();
    },
    { scope: root, dependencies: [motionOn], revertOnUpdate: true },
  );

  return (
    <div ref={root} className={styles.media} aria-hidden="true">
      <div className={styles.settle}>
        {layered ? (
          <>
            <Still id={`${id}-base`} crop={crop} alt="" sizes={sizes} className={styles.still} />
            <Still id={`${id}-full`} crop={crop} alt="" sizes={sizes} className={`${styles.still} ${styles.full}`} />
          </>
        ) : (
          <Still id={id} crop={crop} alt="" sizes={sizes} className={styles.still} />
        )}
      </div>
    </div>
  );
}
