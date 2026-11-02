"use client";

import { useId, useRef } from "react";
import { useMotion } from "@/components/motion/MotionProvider";
import { surface } from "@/content/copy";
import { gsap, useGSAP } from "@/lib/gsap";
import { sliceScene, type SliceScene } from "@/lib/graphics-slice";
import styles from "./SliceBounce.module.css";

type Props = {
  className?: string;
  /** "auto": the portrait framing below 700 px, the wide one from 700 px. The lab shows each alone. */
  variant?: "auto" | "wide" | "portrait";
  /** Scrubbed by its own scroll position (the landing); false plays once on entry (the lab). */
  scrub?: boolean;
};

const SCENES = { wide: sliceScene("wide"), portrait: sliceScene("portrait") };

type Ball = { x: number; y: number; r: number };
/** A point part-way along a sampled path (t in 0..1), interpolated between its samples. */
function along(pts: Ball[], t: number): Ball {
  const f = Math.min(1, Math.max(0, t)) * (pts.length - 1);
  const i = Math.min(pts.length - 2, Math.floor(f));
  const k = f - i;
  const a = pts[i];
  const b = pts[i + 1];
  return { x: a.x + (b.x - a.x) * k, y: a.y + (b.y - a.y) * k, r: a.r + (b.r - a.r) * k };
}
const place = (el: Element | undefined, p: Ball) =>
  el?.setAttribute("transform", `translate(${p.x.toFixed(1)} ${p.y.toFixed(1)}) scale(${p.r.toFixed(2)})`);

/**
 * G17 "After the bounce" (owner, 2026-11-02: "an animated render or graphic of a ball bouncing off a slice shot, and
 * changing direction dramatically upon landing"). One sliced shot, seen from above the side of the court (a small 3D
 * scene projected in graphics-slice.ts, so the arcs, their shadows on the floor and the court lines agree): the ball
 * crosses the net and lands past the service line; off a standard face it bounces up and runs on near its line (steel),
 * off the KINETIQ face it skids low and kicks to the side (amber). The shadows show the turn on the floor, so the kick
 * reads even where the arcs overlap on screen.
 * Scrubbed by scroll: the flight draws with the ball travelling along it, the bounce ripples, then the two exits draw
 * together, each with its ball, and the labels arrive. Server render and reduced motion: the final state (both exits
 * drawn, each ball at its end, the labels shown). Labels are HTML (15 px and up); the drawing is aria-hidden and the
 * figure carries its description.
 */
export function SliceBounce({ className, variant = "auto", scrub = true }: Props) {
  const root = useRef<HTMLElement>(null);
  const { motionOn } = useMotion();
  const gid = useId().replace(/:/g, "");

  useGSAP(
    () => {
      const el = root.current;
      if (!motionOn || !el) return;
      const mm = gsap.matchMedia();
      mm.add("(prefers-reduced-motion: no-preference)", () => {
        // Already past it when the page hydrates (a reload mid-page): keep the final state.
        if (!scrub && el.getBoundingClientRect().top < window.innerHeight * 0.7) return;
        const q = gsap.utils.selector(el);
        const frames = q("[data-frame]") as HTMLElement[];
        const draw = (sel: string) => q(sel);
        // Draw-on dashes, measured: these strokes keep their width at any size (non-scaling), and browsers disagree on
        // whether such a stroke's dashes count in the drawing's units or the screen's. A dash as long as the larger of
        // the two lengths (and a gap as long) is whole at offset 0 and hidden at offset = dash either way. Only while
        // animating: the server render and reduced motion draw solid lines, no dash at all.
        for (const path of el.querySelectorAll<SVGPathElement>("path[data-draw]")) {
          const user = path.getTotalLength();
          const ctm = path.getScreenCTM();
          const len = Math.ceil(Math.max(user, user * (ctm ? Math.hypot(ctm.a, ctm.b) : 1)) * 1.02) + 2;
          gsap.set(path, { strokeDasharray: `${len} ${len}`, strokeDashoffset: len });
        }
        gsap.set(draw("[data-ball]"), { opacity: 0 });
        gsap.set(draw("[data-mark]"), { opacity: 0 });
        // the ripple grows about the bounce point itself (its own centre, in the SVG's coordinates)
        for (const r of draw("[data-ripple]")) gsap.set(r, { opacity: 0, svgOrigin: `${r.getAttribute("cx")} ${r.getAttribute("cy")}` });
        // the labels' inner text rises; their positions (CSS translate on the outer span) are never touched
        gsap.set(draw("[data-label]"), { opacity: 0, y: 10 });

        const state = { fly: 0, out: 0 };
        const move = () => {
          for (const f of frames) {
            const s = SCENES[f.dataset.frame as keyof typeof SCENES] as SliceScene;
            const b = (k: string) => f.querySelector(`[data-ball="${k}"]`) ?? undefined;
            place(b("flight"), along(s.flightPts, state.fly));
            place(b("standard"), along(s.standardPts, state.out));
            place(b("kinetiq"), along(s.kinetiqPts, state.out));
          }
        };
        move();
        const tl = gsap.timeline({
          defaults: { ease: "none" },
          scrollTrigger: scrub
            ? { trigger: el, start: "top 85%", end: "bottom 55%", scrub: 0.6 }
            : { trigger: el, start: "top 75%", once: true },
        });
        // the flight: the line draws and the ball rides its head
        tl.to(draw('[data-ball="flight"]'), { opacity: 1, duration: 0.05 }, 0)
          .to(draw('[data-draw="flight"]'), { strokeDashoffset: 0, duration: 1 }, 0)
          .to(state, { fly: 1, duration: 1, onUpdate: move }, 0)
          // the bounce: the mark lands, a ripple runs out from it, the incoming ball hands over to the two exits
          .to(draw("[data-mark]"), { opacity: 1, duration: 0.12, ease: "power2.out" }, 0.98)
          .fromTo(draw("[data-ripple]"), { opacity: 0.9, scale: 0.95 }, { opacity: 0, scale: 2.4, duration: 0.45, ease: "power2.out" }, 0.98)
          .to(draw('[data-ball="flight"]'), { opacity: 0, duration: 0.04 }, 1.0)
          .to(draw('[data-ball="standard"], [data-ball="kinetiq"]'), { opacity: 1, duration: 0.04 }, 1.0)
          // the two exits together, each ball at its line's head
          .to(draw('[data-draw="standard"], [data-draw="kinetiq"]'), { strokeDashoffset: 0, duration: 1.1 }, 1.02)
          .to(state, { out: 1, duration: 1.1, ease: "power1.out", onUpdate: move }, 1.02)
          .to(draw("[data-label]"), { opacity: 1, y: 0, duration: 0.3, stagger: 0.06, ease: "power2.out" }, 1.7)
          .to({}, { duration: 0.25 });
        return () => {
          state.fly = 1;
          state.out = 1;
          move();
        };
      });
      return () => mm.revert();
    },
    { scope: root, dependencies: [motionOn, scrub], revertOnUpdate: true },
  );

  const frame = (name: "wide" | "portrait") => {
    const s = SCENES[name];
    const end = (p: Ball[]) => p[p.length - 1];
    const pos = (a: { x: number; y: number }) => ({ left: `${(a.x * 100).toFixed(2)}%`, top: `${(a.y * 100).toFixed(2)}%` });
    const ball = (k: string, p: Ball) => (
      <g data-ball={k} transform={`translate(${p.x} ${p.y}) scale(${p.r})`} className={styles[`ball_${k}`]}>
        <circle r="1" />
      </g>
    );
    const g = `${gid}-${name}`;
    return (
      <div className={styles.frame} data-frame={name} style={{ aspectRatio: `${s.vw} / ${s.vh}` }}>
        <svg viewBox={`0 0 ${s.vw} ${s.vh}`} className={styles.svg} focusable="false">
          <defs>
            <linearGradient id={`${g}-floor`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0" stopColor="rgb(36 36 41)" />
              <stop offset="1" stopColor="rgb(52 52 58)" />
            </linearGradient>
          </defs>
          <path d={s.glass} className={styles.glass} />
          <path d={s.floor} className={styles.floor} style={{ fill: `url(#${g}-floor)` }} />
          <path d={s.lines} className={styles.lines} />
          <path d={s.net} className={styles.net} />
          <path d={s.flightShadow} className={styles.shadow} data-draw="flight" />
          <path d={s.standardShadow} className={styles.shadow} data-draw="standard" />
          <path d={s.kinetiqShadow} className={`${styles.shadow} ${styles.shadowK}`} data-draw="kinetiq" />
          <path d={s.flight} className={styles.flight} data-draw="flight" />
          <path d={s.standard} className={styles.standard} data-draw="standard" />
          <path d={s.kinetiq} className={styles.kinetiqGlow} data-draw="kinetiq" />
          <path d={s.kinetiq} className={styles.kinetiq} data-draw="kinetiq" />
          <ellipse cx={s.bounce.x} cy={s.bounce.y} rx={s.bounce.rx} ry={s.bounce.ry} className={styles.mark} data-mark="" />
          <ellipse cx={s.bounce.x} cy={s.bounce.y} rx={s.bounce.rx} ry={s.bounce.ry} className={styles.ripple} data-ripple="" />
          {ball("flight", end(s.flightPts))}
          {ball("standard", end(s.standardPts))}
          {ball("kinetiq", end(s.kinetiqPts))}
        </svg>
        <span className={`${styles.label} ${styles.bounce}`} style={pos(s.anchors.bounce)}>
          <span className={styles.inner} data-label="">
            {surface.graphic.bounce}
          </span>
        </span>
        <span className={`${styles.label} ${styles.std}`} style={pos(s.anchors.standard)}>
          <span className={styles.inner} data-label="">
            <span className={styles.name}>{surface.graphic.standard.name}</span>
            <span className={styles.note}>{surface.graphic.standard.note}</span>
          </span>
        </span>
        <span className={`${styles.label} ${styles.kq}`} style={pos(s.anchors.kinetiq)}>
          <span className={styles.inner} data-label="">
            <span className={styles.name}>{surface.graphic.kinetiq.name}</span>
            <span className={styles.note}>{surface.graphic.kinetiq.note}</span>
          </span>
        </span>
      </div>
    );
  };

  return (
    <figure ref={root} className={`${styles.root}${className ? ` ${className}` : ""}`} data-variant={variant}>
      <div className={styles.stage} aria-hidden="true">
        {variant !== "portrait" ? frame("wide") : null}
        {variant !== "wide" ? frame("portrait") : null}
      </div>
      <figcaption className="visually-hidden">{surface.graphic.alt}</figcaption>
    </figure>
  );
}
