"use client";

import { useRef, type ReactNode } from "react";
import { useMotion } from "@/components/motion/MotionProvider";
import { gsap, useGSAP } from "@/lib/gsap";

type Props = {
  id?: string;
  className?: string;
  "aria-labelledby"?: string;
  /** Scroll range of the scrub, as ScrollTrigger start/end. */
  start?: string;
  end?: string;
  /** Add tweens to the scrubbed timeline (selectors are scoped to this section). */
  build: (tl: gsap.core.Timeline) => void;
  children: ReactNode;
};

/** A section whose tweens are scrubbed by its own passage through the viewport (no pin). */
export function Scrub({ id, className, start = "top bottom", end = "bottom top", build, children, ...rest }: Props) {
  const root = useRef<HTMLElement>(null);
  const { motionOn } = useMotion();
  useGSAP(
    () => {
      if (!motionOn) return;
      const mm = gsap.matchMedia();
      mm.add("(prefers-reduced-motion: no-preference)", () => {
        const tl = gsap.timeline({
          defaults: { ease: "none" },
          scrollTrigger: { trigger: root.current, start, end, scrub: 0.5 },
        });
        build(tl);
      });
      return () => mm.revert();
    },
    { scope: root, dependencies: [motionOn], revertOnUpdate: true },
  );
  return (
    <section ref={root} id={id} tabIndex={id ? -1 : undefined} className={className} {...rest}>
      {children}
    </section>
  );
}
