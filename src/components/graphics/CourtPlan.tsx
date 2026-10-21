"use client";

import { useEffect, useId, useRef, useState, type CSSProperties } from "react";
import { useMotion } from "@/components/motion/MotionProvider";
import { ambassador } from "@/content/lineup";
import { LAYOUT, courtPaths, dimBox, type Aspect } from "@/lib/graphics-court";
import { gsap, useGSAP } from "@/lib/gsap";
import styles from "./CourtPlan.module.css";

const sentence = (s: string) => s.charAt(0).toUpperCase() + s.slice(1);

/** Strings this graphic adds on top of lineup.ts (ambassador). Text only: no logos, likeness or people. */
export const LABELS = {
  who: `One on one with ${ambassador.confirmed ? ambassador.name : ambassador.neutral}`,
  where: sentence(ambassador.event),
  summary: "Plan of a padel court, 20 by 10 metres, with one marked position at the back of the court for the session.",
};

type Props = {
  className?: string;
  /** Gallery slide shape. The court lies across in 16:10 and stands up in 4:5. */
  aspect?: Aspect;
  /**
   * When the parent gallery controls visibility, pass whether this slide is showing; the glow fades
   * in the first time it becomes true. Left undefined, the glow fades in when the plan scrolls into view.
   */
  active?: boolean;
  /** Paint the G10 lift and technical grid behind the plan. Default true. */
  field?: boolean;
};

/**
 * G12, the coaching session on a court plan: hairline court (service lines, net, glass walls and
 * mesh sides as double lines), one glowing amber marker at the back of the court and a Saira
 * caption built from lineup.ts. Server render and reduced motion show the glow lit; with motion,
 * it fades in once (400 ms) when the slide shows.
 */
export function CourtPlan({ className, aspect = "16:10", active, field = true }: Props) {
  const root = useRef<HTMLElement>(null);
  const { motionOn } = useMotion();
  const uid = `g12${useId().replace(/[^a-zA-Z0-9]/g, "")}`;
  const layout = LAYOUT[aspect];
  const p = courtPaths(aspect);
  const { w, h } = layout.vb;
  const [inView, setInView] = useState(false);

  // Without an `active` prop, watch the slide itself (also catches carousels that clip horizontally).
  useEffect(() => {
    if (active !== undefined || !root.current) return;
    const el = root.current;
    const io = new IntersectionObserver(
      ([e]) => {
        if (e.isIntersecting) {
          setInView(true);
          io.disconnect();
        }
      },
      { threshold: 0.5 },
    );
    io.observe(el);
    return () => io.disconnect();
  }, [active]);

  const shown = active ?? inView;

  useGSAP(
    () => {
      if (!motionOn || !root.current) return;
      const glow = root.current.querySelectorAll("[data-g12-glow]");
      const mm = gsap.matchMedia();
      mm.add("(prefers-reduced-motion: no-preference)", () => {
        if (shown) gsap.fromTo(glow, { opacity: 0 }, { opacity: 1, duration: 0.4, ease: "power2.out" });
        else gsap.set(glow, { opacity: 0 });
      });
      return () => mm.revert();
    },
    { scope: root, dependencies: [motionOn, shown], revertOnUpdate: true },
  );

  const pc = (v: number) => `${(v * 100).toFixed(3)}%`;
  const dims = layout.dims.map((d) => ({ ...d, ...dimBox(aspect, d.from, d.to) }));
  const { x: mx, y: my } = p.marker;
  const { caption } = layout;
  const vars = { aspectRatio: `${w} / ${h}`, "--shift-by": `${layout.shift}%` } as CSSProperties;

  return (
    <figure
      ref={root}
      className={`${styles.root}${field ? " lift tech-grid" : ""}${className ? ` ${className}` : ""}`}
      data-aspect={aspect}
      style={vars}
    >
      <svg className={styles.plan} viewBox={`0 0 ${w} ${h}`} aria-hidden="true" focusable="false">
        <defs>
          <filter id={`${uid}-glow`} filterUnits="userSpaceOnUse" x={mx - 4} y={my - 4} width="8" height="8">
            <feGaussianBlur stdDeviation="0.42" />
          </filter>
          <filter id={`${uid}-halo`} filterUnits="userSpaceOnUse" x={mx - 6} y={my - 6} width="12" height="12">
            <feGaussianBlur stdDeviation="1.25" />
          </filter>
        </defs>

        <path className={styles.surface} d={p.surface} />
        <path className={styles.line} d={p.lines} vectorEffect="non-scaling-stroke" />
        <path className={styles.mesh} d={p.meshInner} vectorEffect="non-scaling-stroke" />
        <path className={styles.wall} d={`${p.glass}${p.meshOuter}`} vectorEffect="non-scaling-stroke" />
        <path className={styles.post} d={p.posts} />
        <path className={styles.net} d={p.net} vectorEffect="non-scaling-stroke" />
        <path className={styles.post} d={p.netPosts} />

        <path className={styles.leader} d={`${p.leader}M${mx} ${caption.y}h1.6`} vectorEffect="non-scaling-stroke" />

        <g data-g12-glow="">
          <circle className={styles.halo} cx={mx} cy={my} r="2.1" filter={`url(#${uid}-halo)`} />
          <circle className={styles.glow} cx={mx} cy={my} r="0.62" filter={`url(#${uid}-glow)`} />
        </g>
        <circle className={styles.ring} cx={mx} cy={my} r="0.55" vectorEffect="non-scaling-stroke" />
        <path
          className={styles.ticks}
          d={`M${mx - 1.15} ${my}H${mx - 0.78}M${mx + 0.78} ${my}H${mx + 1.15}M${mx} ${my - 1.15}V${my - 0.78}M${mx} ${my + 0.78}V${my + 1.15}`}
          vectorEffect="non-scaling-stroke"
        />
        <circle className={styles.core} cx={mx} cy={my} r="0.17" />
      </svg>

      {/* dimension lines in HTML: the gap always fits its label, and the ticks stay crisp */}
      {dims.map((d) => (
        <span
          key={d.key}
          className={styles.dim}
          data-vertical={d.vertical ? "" : undefined}
          style={{ "--x": d.x, "--y": d.y, "--len": d.len } as CSSProperties}
          aria-hidden="true"
        >
          <span className={styles.dimLine} />
          <span className={styles.dimText}>{d.text}</span>
          <span className={styles.dimLine} />
        </span>
      ))}

      <figcaption
        className={styles.caption}
        style={{ "--x": pc(caption.x / w), "--y": pc(caption.y / h), "--len": pc(caption.w / w) } as CSSProperties}
      >
        <span className={styles.who}>{LABELS.who}</span>
        <span className={styles.where}>{LABELS.where}</span>
        <span className="visually-hidden">{LABELS.summary}</span>
      </figcaption>
    </figure>
  );
}
