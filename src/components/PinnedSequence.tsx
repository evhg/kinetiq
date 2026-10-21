"use client";

import { useRef, type MouseEvent } from "react";
import { gsap, useGSAP } from "@/lib/gsap";
import { useMotion } from "@/components/motion/MotionProvider";

const steps = [
  { title: "Pinned", body: "This section stays in place while you scroll." },
  { title: "Scrubbed", body: "Each step is tied to the scroll position, forwards and backwards." },
  { title: "Skippable", body: "The Skip link above jumps straight past the whole sequence." },
];

export function PinnedSequence({ afterId }: { afterId: string }) {
  const root = useRef<HTMLElement>(null);
  const { motionOn } = useMotion();

  // Jump instantly (no animation on a keyboard-driven action) and move focus,
  // which Lenis and pinned layouts would otherwise leave behind.
  const skip = (e: MouseEvent<HTMLAnchorElement>) => {
    const target = document.getElementById(afterId);
    if (!target) return;
    e.preventDefault();
    if (window.__lenis) window.__lenis.scrollTo(target, { immediate: true, force: true });
    else target.scrollIntoView({ behavior: "instant", block: "start" });
    target.focus({ preventScroll: true });
    history.replaceState(null, "", `#${afterId}`);
  };

  useGSAP(
    () => {
      if (!motionOn) return;
      const mm = gsap.matchMedia();
      mm.add("(prefers-reduced-motion: no-preference)", () => {
        const items = gsap.utils.toArray<HTMLElement>(".pin-step");
        gsap.set(items.slice(1), { autoAlpha: 0, yPercent: 12 });
        const tl = gsap.timeline({
          defaults: { ease: "none" },
          scrollTrigger: {
            trigger: ".pin-stage",
            start: "top top",
            end: () => `+=${window.innerHeight * 2}`,
            pin: true,
            scrub: 0.6,
            invalidateOnRefresh: true,
          },
        });
        tl.to(".pin-progress__bar", { scaleX: 1, duration: steps.length - 1 }, 0);
        items.forEach((item, i) => {
          if (i === 0) return;
          // Sequential, never overlapping: two half-faded headings are unreadable.
          tl.to(items[i - 1], { autoAlpha: 0, yPercent: -12, duration: 0.3 }, i - 0.7)
            .to(item, { autoAlpha: 1, yPercent: 0, duration: 0.3 }, i - 0.4);
        });
      });
      return () => mm.revert();
    },
    { scope: root, dependencies: [motionOn], revertOnUpdate: true },
  );

  return (
    <section ref={root} className="pin" aria-labelledby="pin-title" data-motion-on={motionOn}>
      <div className="pin-stage">
        {/* Inside the pinned stage so it stays visible for the whole sequence. */}
        <a className="skip-link" href={`#${afterId}`} onClick={skip}>
          Skip this sequence
        </a>
        <h2 id="pin-title" className="pin-title">
          Pinned sequence
        </h2>
        <div className="pin-progress" aria-hidden="true">
          <span className="pin-progress__bar" />
        </div>
        <ol className="pin-steps">
          {steps.map((step) => (
            <li key={step.title} className="pin-step">
              <h3>{step.title}</h3>
              <p>{step.body}</p>
            </li>
          ))}
        </ol>
      </div>
    </section>
  );
}
