"use client";

import { useRef, type MouseEvent, type ReactNode } from "react";
import { gsap, useGSAP } from "@/lib/gsap";
import { useMotion } from "./MotionProvider";

type Props = {
  id: string;
  nextId: string;
  labelledBy: string;
  className?: string;
  /** Scroll length while pinned, in viewport heights. */
  length?: number;
  /** Build the scrubbed timeline. Selectors are scoped to this chapter. */
  build: (tl: gsap.core.Timeline) => void | (() => void);
  children: ReactNode;
};

/**
 * A pinned, scrubbed chapter with a visible Skip link. With motion off it is a
 * normal section: no pin, no scrub, and the CSS shows the final state.
 */
export function PinnedChapter({ id, nextId, labelledBy, className = "", length = 2, build, children }: Props) {
  const root = useRef<HTMLElement>(null);
  const { motionOn } = useMotion();

  useGSAP(
    () => {
      if (!motionOn) return;
      const mm = gsap.matchMedia();
      mm.add("(prefers-reduced-motion: no-preference)", () => {
        const tl = gsap.timeline({
          defaults: { ease: "none" },
          scrollTrigger: {
            trigger: ".pin-stage",
            start: "top top",
            end: () => `+=${window.innerHeight * length}`,
            pin: true,
            scrub: 0.6,
            invalidateOnRefresh: true,
          },
        });
        const cleanup = build(tl);
        return () => cleanup?.();
      });
      return () => mm.revert();
    },
    { scope: root, dependencies: [motionOn], revertOnUpdate: true },
  );

  // Instant jump (keyboard-driven, so no animation) and move focus.
  const skip = (e: MouseEvent<HTMLAnchorElement>) => {
    const target = document.getElementById(nextId);
    if (!target) return;
    e.preventDefault();
    if (window.__lenis) window.__lenis.scrollTo(target, { immediate: true, force: true });
    else target.scrollIntoView({ behavior: "instant", block: "start" });
    target.focus({ preventScroll: true });
    history.replaceState(null, "", `#${nextId}`);
  };

  return (
    <section ref={root} id={id} tabIndex={-1} className={`pin ${className}`} aria-labelledby={labelledBy} data-motion-on={motionOn}>
      <div className="pin-stage">
        <a className="skip-link" href={`#${nextId}`} onClick={skip}>
          Skip this chapter
        </a>
        {children}
      </div>
    </section>
  );
}
