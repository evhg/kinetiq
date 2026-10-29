"use client";

import { useRef } from "react";
import { Still, hasStill } from "@/components/media/Still";
import { useMotion } from "@/components/motion/MotionProvider";
import { holes } from "@/content/copy";
import { gsap, useGSAP } from "@/lib/gsap";
import styles from "./HolesRender.module.css";

/** K16 exists once the render team's pair is exported; without it the pair section reads whole on G06. */
export const K16 = hasStill("K16-base", "left");

/**
 * K16 (owner, 2026-10-29: "one 2D and one 3D visualization"): the same white twill plate at the same scale, a drilled
 * hole (left) beside a moulded one (right), rendered in K04's language with one camera and one light. Two crops of one
 * master per pass. As the pair scrolls through, the light comes up through the moulded hole only (K16-full's right
 * half fades in over the base) and both frames settle; the drilled hole stays as it is. Reduced motion and the server
 * render: the lit pass at rest. Side by side from 700 px, stacked on phones.
 */
export function HolesRender() {
  const root = useRef<HTMLDivElement>(null);
  const { motionOn } = useMotion();
  useGSAP(
    () => {
      if (!motionOn || !root.current) return;
      const mm = gsap.matchMedia();
      mm.add("(prefers-reduced-motion: no-preference)", () => {
        const el = root.current!;
        const q = gsap.utils.selector(el);
        // one scrub per frame (they stack on phones): settle as it enters; the moulded glow from 0.25 to 0.75
        q(`.${styles.frame}`).forEach((frame) => {
          const tl = gsap.timeline({
            defaults: { ease: "none" },
            scrollTrigger: { trigger: frame, start: "top 95%", end: "bottom 30%", scrub: 0.6 },
          });
          tl.fromTo(frame.querySelectorAll(`.${styles.layer}`), { scale: 1.06 }, { scale: 1, duration: 1 }, 0);
          const glow = frame.querySelector(`.${styles.glow}`);
          if (glow) tl.fromTo(glow, { opacity: 0 }, { opacity: 1, duration: 0.5, ease: "power1.inOut" }, 0.25);
        });
      });
      return () => mm.revert();
    },
    { scope: root, dependencies: [motionOn], revertOnUpdate: true },
  );
  if (!K16) return null;
  const { drilled, moulded } = holes.render;
  return (
    <div ref={root} className={styles.pair}>
      <figure className={styles.item}>
        <div className={styles.frame}>
          <Still id="K16-base" crop="left" alt={drilled.alt} sizes="(min-width: 700px) 50vw, 100vw" className={styles.layer} />
        </div>
        <figcaption className={styles.label}>
          <span className={styles.rule} aria-hidden="true" />
          {drilled.label}
        </figcaption>
      </figure>
      <figure className={styles.item}>
        <div className={styles.frame}>
          <Still id="K16-base" crop="right" alt={moulded.alt} sizes="(min-width: 700px) 50vw, 100vw" className={styles.layer} />
          <Still id="K16-full" crop="right" alt="" sizes="(min-width: 700px) 50vw, 100vw" className={`${styles.layer} ${styles.glow}`} />
        </div>
        <figcaption className={styles.label}>
          <span className={`${styles.rule} ${styles.ruleAmber}`} aria-hidden="true" />
          {moulded.label}
        </figcaption>
      </figure>
    </div>
  );
}
