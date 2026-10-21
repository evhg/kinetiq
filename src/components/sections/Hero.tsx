"use client";

import { useRef } from "react";
import { gsap, useGSAP } from "@/lib/gsap";
import { heroState } from "@/lib/scene-state";
import { useMotion } from "@/components/motion/MotionProvider";
import { LazyHeroScene } from "@/components/three/LazyHeroScene";
import { RacketSvg } from "@/components/RacketSvg";
import { Cta } from "@/components/Cta";
import { claims } from "@/content/claims";

const stats = [
  { value: "1", label: "piece" },
  { value: "15 µm", label: "precision" },
  { value: "0", label: "drilled holes" },
  { value: "100%", label: "Swiss Made" },
];

export function Hero() {
  const root = useRef<HTMLElement>(null);
  const { motionOn } = useMotion();

  useGSAP(
    () => {
      if (!motionOn) return;
      const mm = gsap.matchMedia();
      mm.add("(prefers-reduced-motion: no-preference)", () => {
        // The headline stays put (it is the LCP). Supporting lines arrive with the racket.
        gsap.from(".hero-sub, .hero .cta-wrap", { autoAlpha: 0, y: 16, duration: 0.8, ease: "power3.out", delay: 1.1, stagger: 0.08 });
        gsap.from(".stat", { autoAlpha: 0, y: 12, duration: 0.6, ease: "power3.out", delay: 1.5, stagger: 0.06 });
        gsap.to(heroState, {
          scroll: 1,
          ease: "none",
          scrollTrigger: { trigger: root.current, start: "top top", end: "bottom top", scrub: true },
        });
      });
      return () => {
        heroState.scroll = 0;
        mm.revert();
      };
    },
    { scope: root, dependencies: [motionOn], revertOnUpdate: true },
  );

  return (
    <section ref={root} className="hero" aria-labelledby="hero-title">
      <LazyHeroScene>
        <RacketSvg className="hero-svg" title="The KINETIQ racket: one piece of black carbon with 42 round holes" />
      </LazyHeroScene>
      <div className="hero-copy">
        <h1 id="hero-title" className="display">
          {claims.worldFirstOnePiece}
        </h1>
        <p className="hero-sub">
          {claims.swissMade} Moulded in a single piece of carbon, accurate to 15 microns.
        </p>
        <Cta />
      </div>
      <dl className="stats">
        {stats.map((s) => (
          <div className="stat" key={s.label}>
            <dt>{s.label}</dt>
            <dd>{s.value}</dd>
          </div>
        ))}
      </dl>
    </section>
  );
}
