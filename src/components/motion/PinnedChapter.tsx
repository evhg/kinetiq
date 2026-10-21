"use client";

import { useRef, type CSSProperties, type MouseEvent, type ReactNode } from "react";
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
  /**
   * Media query for pinning. Keep it in step with the CSS that layers the beats (see `.pin-layered`
   * in globals.css): below it, or with reduced motion, the beats simply stack.
   */
  media?: string;
  children: ReactNode;
};

/**
 * A pinned, scrubbed chapter with a visible Skip link. With motion off it is a
 * normal section: no pin, no scrub, and the CSS shows the final state.
 */
export const PIN_MEDIA = "(min-width: 900px) and (prefers-reduced-motion: no-preference)";

export function PinnedChapter({ id, nextId, labelledBy, className = "", length = 2, build, media = PIN_MEDIA, children }: Props) {
  const root = useRef<HTMLElement>(null);
  const { motionOn } = useMotion();

  useGSAP(
    () => {
      if (!motionOn) return;
      const mm = gsap.matchMedia();
      mm.add(media, () => {
        // globals.css reserves the pinned length as the section's padding-bottom before JS runs (PIN_MEDIA),
        // so the pin adds no spacing of its own and releases exactly where the next section starts.
        const reserved = () => parseFloat(getComputedStyle(root.current!).paddingBottom) || 0;
        const tl = gsap.timeline({
          defaults: { ease: "none" },
          scrollTrigger: {
            trigger: ".pin-stage",
            start: "top top",
            end: () => `+=${reserved() || window.innerHeight * length}`,
            pin: true,
            pinSpacing: reserved() === 0,
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

  // Instant jump (keyboard-driven, so no animation) and move focus. The target stops below the fixed
  // header: Lenis and scrollIntoView both honour html's scroll-padding-top (globals.css).
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
    <section
      ref={root}
      id={id}
      tabIndex={-1}
      className={`pin ${className}`}
      style={{ "--pin-len": length } as CSSProperties}
      aria-labelledby={labelledBy}
      data-motion-on={motionOn}
    >
      <div className="pin-stage">
        <a className="skip-link" href={`#${nextId}`} onClick={skip}>
          Skip this chapter
        </a>
        {children}
      </div>
    </section>
  );
}
