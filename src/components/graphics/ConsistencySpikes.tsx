"use client";

import { useId, useRef } from "react";
import { useMotion } from "@/components/motion/MotionProvider";
import { identical } from "@/content/copy";
import { gsap, useGSAP } from "@/lib/gsap";
import { VB, pct } from "@/lib/graphics-plot";
import { SPIKES, spikeGeometry } from "@/lib/graphics-spikes";
import styles from "./ConsistencySpikes.module.css";

const MINUS = "−";

/** Strings this graphic adds on top of identical.stats and identical.graphCaption (copy.ts). */
export const LABELS = {
  axis: { mass: "Mass", balance: "Balance" },
  summary:
    "Illustrative graph. Every racket's mass sits within 1.0 g of the 355.0 g reference, and its balance within 1.0 mm of 250.4 mm: a tall, narrow spike well inside each tolerance window.",
};

type Props = {
  className?: string;
  /** "row" puts the two graphs side by side from tablet up; "stack" always stacks them. */
  layout?: "row" | "stack";
  /** Show the "Illustrative" caption. Default true. */
  caption?: boolean;
};

const V = `0 0 ${VB} ${VB}`;
const fmt = (v: number) => v.toFixed(1);

/**
 * G04, Identical chapter. Two small multiples: mass and balance, each a glowing distribution
 * spike inside its ±1.0 window, under a large stat numeral. Server render and reduced motion
 * show the finished graphs; motion lets each spike rise once on entry.
 */
export function ConsistencySpikes({ className, layout = "row", caption = true }: Props) {
  const root = useRef<HTMLElement>(null);
  const { motionOn } = useMotion();
  const gid = useId().replace(/:/g, "");

  useGSAP(
    () => {
      if (!motionOn || !root.current) return;
      const el = root.current;
      const mm = gsap.matchMedia();
      mm.add("(prefers-reduced-motion: no-preference)", () => {
        // Already past the trigger when motion switches on (above the fold, or a reload mid-page):
        // keep the finished graph instead of hiding it and drawing it again.
        if (el.getBoundingClientRect().top < window.innerHeight * 0.75) return;
        const spikes = el.querySelectorAll("[data-spike]");
        gsap.fromTo(
          spikes,
          { scaleY: 0.92, opacity: 0, transformOrigin: "50% 100%" },
          {
            scaleY: 1,
            opacity: 1,
            duration: 0.4,
            ease: "power3.out",
            stagger: 0.08,
            scrollTrigger: { trigger: el, start: "top 75%", once: true },
          },
        );
      });
      return () => mm.revert();
    },
    { scope: root, dependencies: [motionOn], revertOnUpdate: true },
  );

  return (
    <figure
      ref={root}
      className={`${styles.root} ${layout === "stack" ? styles.stack : ""}${className ? ` ${className}` : ""}`}
    >
      <div className={styles.pair}>
        {SPIKES.map((s, i) => {
          const g = spikeGeometry(s);
          const stat = identical.stats[i];
          const id = `${gid}-${s.id}`;
          return (
            <div key={s.id} className={styles.multiple}>
              <p className={styles.stat}>
                <span className={`t-stat ${styles.value}`}>
                  {stat.value}
                  <span className="t-unit">{stat.unit}</span>
                </span>
                <span className={styles.statLabel}>{stat.label}</span>
              </p>

              <div className={styles.graph} aria-hidden="true">
                <div className={styles.plot}>
                  <svg className={styles.layer} viewBox={V} preserveAspectRatio="none" focusable="false">
                    {g.rules.map((y) => (
                      <line key={y} className={styles.rule} x1="0" x2={VB} y1={y} y2={y} />
                    ))}
                    {g.minor.map((x) => (
                      <line key={x} className={styles.vrule} x1={x} x2={x} y1="0" y2={VB} />
                    ))}
                    <rect className={styles.window} x={g.windowLo} width={g.windowHi - g.windowLo} y="0" height={VB} />
                    <line className={styles.refLine} x1={g.centre} x2={g.centre} y1="0" y2={VB} />
                    <line className={styles.axis} x1="0" x2={VB} y1={VB} y2={VB} />
                  </svg>

                  <div className={styles.spike} data-spike>
                    <svg
                      className={`${styles.layer} ${styles.glow}`}
                      viewBox={V}
                      preserveAspectRatio="none"
                      focusable="false"
                    >
                      <path d={g.line} />
                    </svg>
                    <svg className={styles.layer} viewBox={V} preserveAspectRatio="none" focusable="false">
                      <defs>
                        <linearGradient id={`${id}-fill`} x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0" stopColor="var(--amber)" stopOpacity="0.42" />
                          <stop offset="0.7" stopColor="var(--amber)" stopOpacity="0.08" />
                          <stop offset="1" stopColor="var(--amber)" stopOpacity="0" />
                        </linearGradient>
                        <linearGradient id={`${id}-core`} gradientUnits="userSpaceOnUse" x1="0" y1={VB} x2="0" y2="0">
                          <stop offset="0" stopColor="var(--amber)" />
                          <stop offset="0.6" stopColor="var(--amber)" />
                          <stop offset="1" stopColor="var(--amber-hot)" />
                        </linearGradient>
                      </defs>
                      <path className={styles.area} d={g.area} fill={`url(#${id}-fill)`} />
                      <path className={styles.core} d={g.line} stroke={`url(#${id}-core)`} />
                      {g.rug.map((x, k) => (
                        <line key={k} className={styles.rug} x1={x} x2={x} y1={VB} y2={VB - 55} />
                      ))}
                    </svg>
                  </div>

                  <svg className={styles.layer} viewBox={V} preserveAspectRatio="none" focusable="false">
                    <line className={styles.limit} x1={g.windowLo} x2={g.windowLo} y1="0" y2={VB} />
                    <line className={styles.limit} x1={g.windowHi} x2={g.windowHi} y1="0" y2={VB} />
                  </svg>

                  <span className={`${styles.limitLabel} ${styles.limitLo}`} style={{ right: pct(VB - g.windowLo) }}>
                    {`${MINUS}${fmt(s.window)} ${s.unit}`}
                  </span>
                  <span className={`${styles.limitLabel} ${styles.limitHi}`} style={{ left: pct(g.windowHi) }}>
                    {`+${fmt(s.window)} ${s.unit}`}
                  </span>
                </div>

                <div className={styles.ticks}>
                  {g.minor.map((x) => (
                    <i key={x} className={styles.tickMark} style={{ left: pct(x) }} />
                  ))}
                  <span className={styles.tickLo}>{fmt(g.lo)}</span>
                  <span className={styles.tickRef} style={{ left: pct(g.centre) }}>
                    {`${fmt(s.reference)} ${s.unit}`}
                  </span>
                  <span className={styles.tickHi}>{fmt(g.hi)}</span>
                </div>
                <span className={styles.axisTitle}>{LABELS.axis[s.id]}</span>
              </div>
            </div>
          );
        })}
      </div>
      <figcaption className={styles.caption}>
        {caption ? <span className={styles.captionText}>{identical.graphCaption}</span> : null}
        <span className="visually-hidden">{LABELS.summary}</span>
      </figcaption>
    </figure>
  );
}
