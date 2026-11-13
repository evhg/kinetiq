"use client";

import { useRef, type CSSProperties, type FocusEvent, type MouseEvent, type ReactNode } from "react";
import { PIN_MEDIA } from "@/components/motion/PinnedChapter";
import { useMotion } from "@/components/motion/MotionProvider";
import { gsap, useGSAP } from "@/lib/gsap";

/** Below the pin (phones, portrait tablets): the chapter is not pinned, and its timeline runs as `flow` crosses the screen. */
export const FLOW_MEDIA = "(max-width: 899px) and (prefers-reduced-motion: no-preference)";

type Props = {
  id: string;
  nextId: string;
  labelledBy: string;
  className?: string;
  /** Scroll length while pinned, in screens (the CSS reads it as --pin-len). */
  length?: number;
  /**
   * The scrubbed timeline. `mode` "pin": the stage is stuck (from 900 px) and the timeline runs over the pin's whole
   * scroll; "flow": below 900 px, over the `flow` element's passage through the screen.
   */
  build: (tl: gsap.core.Timeline, mode: "pin" | "flow") => void | (() => void);
  /** The element whose passage drives the timeline below the pin (a selector inside the chapter). Omitted: no flow. */
  flow?: string;
  /** The flow's ScrollTrigger range (default: from its top at 85% of the screen to its bottom at 25%). */
  flowStart?: string;
  flowEnd?: string;
  children: ReactNode;
};

/**
 * /v2's chapter: PinnedChapter (the same CSS pin, the same Skip link) plus a timeline below the pin, so the Apple-style
 * effects also play on phones, scrubbed by the frame's passage instead of a pin (CLAUDE.md: pins only from 900 px).
 * Reduced motion: neither runs, and the CSS shows the final state.
 */
export function V2Chapter({ id, nextId, labelledBy, className = "", length = 2, build, flow, flowStart = "top 85%", flowEnd = "bottom 25%", children }: Props) {
  const root = useRef<HTMLElement>(null);
  const { motionOn } = useMotion();

  useGSAP(
    () => {
      if (!motionOn) return;
      const mm = gsap.matchMedia();
      mm.add(PIN_MEDIA, () => {
        const tl = gsap.timeline({
          defaults: { ease: "none" },
          scrollTrigger: { trigger: root.current, start: "top top", end: "bottom bottom", scrub: 0.6, invalidateOnRefresh: true },
        });
        const cleanup = build(tl, "pin");
        return () => cleanup?.();
      });
      if (flow) {
        mm.add(FLOW_MEDIA, () => {
          const el = root.current?.querySelector(flow);
          if (!el) return;
          const tl = gsap.timeline({
            defaults: { ease: "none" },
            scrollTrigger: { trigger: el, start: flowStart, end: flowEnd, scrub: 0.5, invalidateOnRefresh: true },
          });
          const cleanup = build(tl, "flow");
          return () => cleanup?.();
        });
      }
      return () => mm.revert();
    },
    { scope: root, dependencies: [motionOn], revertOnUpdate: true },
  );

  const skip = (e: MouseEvent<HTMLAnchorElement>) => {
    const target = document.getElementById(nextId);
    if (!target) return;
    e.preventDefault();
    if (window.__lenis) window.__lenis.scrollTo(target, { immediate: true, force: true });
    else target.scrollIntoView({ behavior: "instant", block: "start" });
    target.focus({ preventScroll: true });
    history.replaceState(null, "", `#${nextId}`);
  };
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
