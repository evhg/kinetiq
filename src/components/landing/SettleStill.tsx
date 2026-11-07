"use client";

import { useRef } from "react";
import { hasStill, Still } from "@/components/media/Still";
import { useMotion } from "@/components/motion/MotionProvider";
import { gsap, useGSAP } from "@/lib/gsap";
import styles from "./SettleStill.module.css";

/** The settle runs only with motion; reduced motion and the server render show the final state. */
const SETTLE = "(prefers-reduced-motion: no-preference)";

type Props = {
  /** The render's id: its two passes are `<id>-base` and `<id>-full` (e.g. "K11-single" has "K11-single-base"). */
  id: string;
  crop?: string;
  phoneCrop?: string;
  sizes?: string;
  phoneSizes?: string;
  /** The frame: a positioned box with a fixed ratio that clips its contents (the caller's CSS). */
  className?: string;
  /** Added to each pass's <picture> (the caller's object-fit, position and masks). */
  stillClassName?: string;
  /**
   * The base pass's sizes (default: `sizes`). It is seen only while the frame settles, under the full pass coming up,
   * so on phones it asks for about two thirds of the full pass's width or less (a 2x rung on a 3x phone) (the phone load budget; DESIGN.md "Stills").
   */
  baseSizes?: string;
  basePhoneSizes?: string;
  /** The scale the frame enters at (default 1.12, the edition cards'). */
  from?: number;
};

/**
 * A whole-racket render in K04's language (owner, 2026-11-07: "make the whole racket renders look more like the moulded
 * holes graphic including the animation"; Holes.tsx's FLOW is the model): as the frame scrolls in, the render settles
 * from close (scale 1.12) to rest, scrubbed by scroll (0.6), from the frame's top at the screen's foot to 35% down,
 * and its full pass (the warm glow in the bores, the throat and along the edge) comes up over its base pass (the raking
 * light alone), as K04's ring of light does. Both passes are one render, pixel-registered, exported with the same crops,
 * each with its "-pace" and "-nogrip" twins by the usual names; where only one still is exported for the crop, it
 * settles alone. Transform and opacity only, on layers inside the caller's fixed-ratio frame, so nothing shifts. Server
 * render and reduced motion: the full pass at scale 1. Used by the edition cards, Choose your feel (K08) and Identical
 * (K07). The section reads without the image (Still renders nothing until a still is exported).
 */
export function SettleStill({
  id,
  crop = "wide",
  phoneCrop,
  sizes,
  phoneSizes,
  className,
  stillClassName,
  baseSizes,
  basePhoneSizes,
  from = 1.12,
}: Props) {
  const root = useRef<HTMLDivElement>(null);
  const { motionOn } = useMotion();
  const layered =
    hasStill(`${id}-base`, crop) && hasStill(`${id}-full`, crop) && (!phoneCrop || (hasStill(`${id}-base`, phoneCrop) && hasStill(`${id}-full`, phoneCrop)));
  const still = `${styles.layer}${stillClassName ? ` ${stillClassName}` : ""}`;

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
        tl.fromTo(frame.querySelector(`.${styles.settle}`), { scale: from }, { scale: 1, duration: 1 }, 0);
        const full = frame.querySelector(`.${styles.full}`);
        if (full) tl.fromTo(full, { opacity: 0 }, { opacity: 1, duration: 0.55 }, 0.2);
      });
      return () => mm.revert();
    },
    { scope: root, dependencies: [motionOn], revertOnUpdate: true },
  );

  const pass = (key: string, extra = "", sz = sizes, phoneSz = phoneSizes) => (
    <Still id={key} crop={crop} phoneCrop={phoneCrop} alt="" sizes={sz} phoneSizes={phoneSz} className={`${still}${extra}`} />
  );
  return (
    <div ref={root} className={className} aria-hidden="true">
      <div className={styles.settle}>
        {layered ? (
          <>
            {/* reduced motion never shows the base (the full pass is at rest), so it is not laid out or fetched */}
            {pass(`${id}-base`, ` ${styles.base}`, baseSizes ?? sizes, basePhoneSizes ?? phoneSizes)}
            {pass(`${id}-full`, ` ${styles.full}`)}
          </>
        ) : (
          pass(id)
        )}
      </div>
    </div>
  );
}
