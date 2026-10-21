"use client";

import { useRef, type ElementType, type ReactNode } from "react";
import { useMotion } from "@/components/motion/MotionProvider";
import { gsap, useGSAP } from "@/lib/gsap";

type Props = {
  as?: ElementType;
  className?: string;
  children: ReactNode;
  /** Selector (inside this element) for the pieces that rise in, staggered. Default: direct children. */
  items?: string;
  y?: number;
  stagger?: number;
  start?: string;
  id?: string;
  "aria-labelledby"?: string;
};

/**
 * Plays a short fade-and-rise once when the block enters the viewport. Server render and
 * reduced motion show the final state; only transform and opacity move.
 */
export function Reveal({ as: Tag = "div", className, children, items = ":scope > *", y = 16, stagger = 0.06, start = "top 78%", ...rest }: Props) {
  const root = useRef<HTMLElement>(null);
  const { motionOn } = useMotion();
  useGSAP(
    () => {
      if (!motionOn || !root.current) return;
      const mm = gsap.matchMedia();
      mm.add("(prefers-reduced-motion: no-preference)", () => {
        const targets = root.current!.querySelectorAll(items);
        gsap.from(targets, {
          opacity: 0,
          y,
          duration: 0.7,
          ease: "power3.out",
          stagger,
          scrollTrigger: { trigger: root.current, start, once: true },
        });
      });
      return () => mm.revert();
    },
    { scope: root, dependencies: [motionOn], revertOnUpdate: true },
  );
  return (
    <Tag ref={root} className={className} {...rest}>
      {children}
    </Tag>
  );
}
