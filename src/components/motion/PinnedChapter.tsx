"use client";

import { useRef, type CSSProperties, type FocusEvent, type MouseEvent, type ReactNode } from "react";
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
 * A pinned, scrubbed chapter with a Skip link that appears on keyboard focus (globals.css `.skip-link`: visually
 * hidden until it takes focus, then shown at once at the top of the stage). With motion off it is a normal section:
 * no pin, no scrub, and the CSS shows the final state.
 */
export const PIN_MEDIA = "(min-width: 900px) and (prefers-reduced-motion: no-preference)";

export function PinnedChapter({ id, nextId, labelledBy, className = "", length = 2, build, media = PIN_MEDIA, children }: Props) {
  // `length` reaches the CSS as --pin-len, which sizes the sticky scroll range.
  const root = useRef<HTMLElement>(null);
  const { motionOn } = useMotion();

  useGSAP(
    () => {
      if (!motionOn) return;
      const mm = gsap.matchMedia();
      mm.add(media, () => {
        // The pin itself is CSS (globals.css: the section is one screen plus `length` screens tall and the
        // stage is position: sticky), so the timeline only scrubs while the stage is stuck.
        const tl = gsap.timeline({
          defaults: { ease: "none" },
          scrollTrigger: {
            trigger: root.current,
            start: "top top",
            end: "bottom bottom",
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

  // The link only shows on keyboard focus (globals.css), at the top of the stage. If the stage is not at the top of
  // the window (the chapter is still below, or already behind), jump to the chapter's first screen, so the link
  // appears just below the header with the chapter opening behind it instead of at the foot of the window. Instant,
  // like the skip itself; the browser's own focus scroll then has nothing left to do.
  const reveal = (e: FocusEvent<HTMLAnchorElement>) => {
    const section = root.current;
    const stage = e.currentTarget.parentElement;
    if (!section || !stage || Math.abs(stage.getBoundingClientRect().top) < 1) return;
    const y = Math.round(section.getBoundingClientRect().top + window.scrollY);
    if (window.__lenis) window.__lenis.scrollTo(y, { immediate: true, force: true });
    else window.scrollTo({ top: y, behavior: "instant" });
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
        <a className="skip-link" href={`#${nextId}`} onClick={skip} onFocus={reveal}>
          Skip this chapter
        </a>
        {children}
      </div>
    </section>
  );
}
