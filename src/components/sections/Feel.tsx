"use client";

import { useRef } from "react";
import { gsap, useGSAP } from "@/lib/gsap";
import { useMotion } from "@/components/motion/MotionProvider";
import { claims } from "@/content/claims";

// Two impact signals: one passing through glue lines (ragged, slow to settle),
// one through a single piece (clean, settles fast). Illustrative, not measured.
function wave(kind: "glued" | "one") {
  const pts: string[] = [];
  for (let i = 0; i <= 240; i++) {
    const x = i * 2.5;
    const t = i / 240;
    const decay = kind === "one" ? Math.exp(-t * 6) : Math.exp(-t * 2.4);
    const base = Math.sin(t * Math.PI * 18) * decay;
    const noise = kind === "glued" ? Math.sin(t * 97) * 0.35 * decay + Math.sin(t * 43 + 1) * 0.25 * decay : 0;
    pts.push(`${x.toFixed(1)},${(50 - (base + noise) * 40).toFixed(1)}`);
  }
  return `M${pts.join(" L")}`;
}

export function Feel() {
  const root = useRef<HTMLElement>(null);
  const { motionOn } = useMotion();

  useGSAP(
    () => {
      if (!motionOn) return;
      const mm = gsap.matchMedia();
      mm.add("(prefers-reduced-motion: no-preference)", () => {
        gsap.from(".wave-path", {
          drawSVG: 0,
          ease: "none",
          stagger: 0.2,
          scrollTrigger: { trigger: ".waves", start: "top 80%", end: "bottom 45%", scrub: 0.5 },
        });
      });
      return () => mm.revert();
    },
    { scope: root, dependencies: [motionOn], revertOnUpdate: true },
  );

  return (
    <section ref={root} id="feel" className="section feel" aria-labelledby="feel-title" tabIndex={-1}>
      <h2 id="feel-title" className="display-2">
        Feel the ball, not the racket.
      </h2>
      <div className="waves" aria-hidden="true">
        <figure className="wave">
          <figcaption>Glued racket</figcaption>
          <svg viewBox="0 0 600 100" preserveAspectRatio="none">
            <path className="wave-path wave-path--glued" d={wave("glued")} />
          </svg>
        </figure>
        <figure className="wave">
          <figcaption>KINETIQ, one piece</figcaption>
          <svg viewBox="0 0 600 100" preserveAspectRatio="none">
            <path className="wave-path wave-path--one" d={wave("one")} />
          </svg>
        </figure>
      </div>
      <div className="feel-points">
        {claims.feel.map((f) => (
          <div className="feel-point" key={f.title}>
            <h3>{f.title}</h3>
            <p>{f.body}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
