"use client";

import { useId, useRef } from "react";
import { useMotion } from "@/components/motion/MotionProvider";
import { precision } from "@/content/copy";
import { gsap, useGSAP } from "@/lib/gsap";
import { VB, pct, yAt } from "@/lib/graphics-plot";
import { LENGTH_MM, X, Y, tolerance } from "@/lib/graphics-tolerance";
import styles from "./ToleranceGraph.module.css";

const MINUS = "−";

/** Strings this graphic adds on top of precision.graph (copy.ts). */
export const LABELS = {
  yAxis: "Deviation, µm",
  xAxis: "Position along the racket, mm",
  limitTop: `+${precision.graph.limitLabel}`,
  limitBottom: `${MINUS}${precision.graph.limitLabel}`,
  summary:
    "Illustrative graph. Along the full 455 mm of the racket, the KINETIQ surface stays inside the plus or minus 15 micron limit. For scale, a human hair is 70 microns and a sheet of paper 100 microns.",
};

const um = (v: number) => (v > 0 ? `+${v}` : v < 0 ? `${MINUS}${Math.abs(v)}` : "0");

type Props = {
  className?: string;
  /** Show the "Illustrative" caption under the plot. Default true. */
  caption?: boolean;
};

const V = `0 0 ${VB} ${VB}`;

/**
 * G03, Precision chapter part B. Surface deviation along the racket against the ±15 µm limit,
 * with a human hair and a sheet of paper for scale. Server render and reduced motion show the
 * finished graph; motion fades the limits in, then wipes the trace on behind a glow head.
 */
export function ToleranceGraph({ className, caption = true }: Props) {
  const root = useRef<HTMLElement>(null);
  const { motionOn } = useMotion();
  const gid = useId().replace(/:/g, "");

  useGSAP(
    () => {
      if (!motionOn || !root.current) return;
      const el = root.current;
      const mm = gsap.matchMedia();
      mm.add("(prefers-reduced-motion: no-preference)", () => {
        const q = gsap.utils.selector(el);
        const [wipe] = q("[data-wipe]");
        const [inner] = q("[data-wipe-inner]");
        const [track] = q("[data-head-track]");
        const head = q("[data-head]");
        const limits = q("[data-limit]");
        const refs = q("[data-ref]");
        const pts = tolerance.head;

        const setWipe = gsap.quickSetter(wipe, "xPercent");
        const setInner = gsap.quickSetter(inner, "xPercent");
        const setHeadX = gsap.quickSetter(track, "xPercent");
        const setHeadY = gsap.quickSetter(track, "yPercent");
        const state = { p: 0 };
        const render = () => {
          const p = state.p;
          setWipe((p - 1) * 100);
          setInner((1 - p) * 100);
          setHeadX(p * 100);
          setHeadY((yAt(pts, p * VB) / VB) * 100);
        };
        render();
        gsap.set(limits, { opacity: 0 });
        gsap.set(refs, { opacity: 0 });
        gsap.set(head, { opacity: 0 });

        gsap
          .timeline({ scrollTrigger: { trigger: el, start: "top 75%", once: true } })
          .to(limits, { opacity: 1, duration: 0.2, ease: "power2.out" }, 0)
          .to(refs, { opacity: 1, duration: 0.3, ease: "power2.out", stagger: 0.06 }, 0.1)
          .to(head, { opacity: 1, duration: 0.15, ease: "power1.out" }, 0.25)
          .to(state, { p: 1, duration: 1.2, ease: "power2.out", onUpdate: render }, 0.25)
          .to(head, { opacity: 0, duration: 0.35, ease: "power2.out" }, 1.25);
      });
      return () => mm.revert();
    },
    { scope: root, dependencies: [motionOn], revertOnUpdate: true },
  );

  const rulesAll = Array.from(new Set([...tolerance.rules, ...tolerance.rulesPhone])).sort((a, b) => b - a);
  const yTicks = [...rulesAll, 0].sort((a, b) => b - a);
  const isPhoneRule = (v: number) => tolerance.rulesPhone.includes(v) || v === 0;
  const isDeskRule = (v: number) => tolerance.rules.includes(v) || v === 0;
  const refs = precision.graph.references;

  return (
    <figure ref={root} className={`${styles.root}${className ? ` ${className}` : ""}`}>
      <div className={styles.chart} aria-hidden="true">
        <span className={styles.yTitle}>{LABELS.yAxis}</span>

        <div className={styles.yTicks}>
          {yTicks.map((v) => (
            <span
              key={v}
              className={`${styles.yTick}${isDeskRule(v) ? "" : ` ${styles.phoneOnly}`}${isPhoneRule(v) ? "" : ` ${styles.deskOnly}`}`}
              style={{ top: pct(Y(v)) }}
            >
              {um(v)}
            </span>
          ))}
        </div>

        <div className={styles.plot}>
          <svg className={styles.layer} viewBox={V} preserveAspectRatio="none" focusable="false">
            {rulesAll.map((v) => (
              <line
                key={v}
                className={`${styles.rule}${isDeskRule(v) ? "" : ` ${styles.phoneOnly}`}${isPhoneRule(v) ? "" : ` ${styles.deskOnly}`}`}
                x1="0"
                x2={VB}
                y1={Y(v)}
                y2={Y(v)}
              />
            ))}
            {tolerance.ticks.map((mm) => (
              <line
                key={mm}
                className={`${styles.vrule}${tolerance.ticksPhone.includes(mm) ? "" : ` ${styles.deskOnly}`}`}
                x1={X(mm)}
                x2={X(mm)}
                y1="0"
                y2={VB}
              />
            ))}
            <line className={styles.axis} x1="0" x2={VB} y1={VB} y2={VB} />
          </svg>

          {refs.map((r) => (
            <div key={r.label} className={styles.ref} style={{ top: pct(Y(r.um)) }} data-ref>
              <span className={styles.refLabel}>{`${r.label}, ${r.um} µm`}</span>
            </div>
          ))}

          <div
            className={styles.band}
            style={{ top: pct(tolerance.top), bottom: pct(VB - tolerance.bottom) }}
            data-limit
          />
          <svg className={styles.layer} viewBox={V} preserveAspectRatio="none" focusable="false" data-limit>
            <line className={styles.limit} x1="0" x2={VB} y1={tolerance.top} y2={tolerance.top} />
            <line className={styles.limit} x1="0" x2={VB} y1={tolerance.bottom} y2={tolerance.bottom} />
          </svg>
          <span
            className={`${styles.limitLabel} ${styles.limitTop}`}
            style={{ bottom: pct(VB - tolerance.top) }}
            data-limit
          >
            {LABELS.limitTop}
          </span>
          <span
            className={`${styles.limitLabel} ${styles.limitBottom}`}
            style={{ top: pct(tolerance.bottom) }}
            data-limit
          >
            {LABELS.limitBottom}
          </span>

          <div className={styles.wipe} data-wipe>
            <div className={styles.wipeInner} data-wipe-inner>
              <svg
                className={`${styles.layer} ${styles.halo}`}
                viewBox={V}
                preserveAspectRatio="none"
                focusable="false"
              >
                <path d={tolerance.trace} />
              </svg>
              <svg
                className={`${styles.layer} ${styles.glow}`}
                viewBox={V}
                preserveAspectRatio="none"
                focusable="false"
              >
                <path d={tolerance.trace} />
              </svg>
              <svg className={styles.layer} viewBox={V} preserveAspectRatio="none" focusable="false">
                <defs>
                  <linearGradient id={`${gid}-trace`} gradientUnits="userSpaceOnUse" x1="0" y1="0" x2={VB} y2="0">
                    <stop offset="0" stopColor="var(--amber)" />
                    <stop offset="0.5" stopColor="var(--amber-hot)" />
                    <stop offset="1" stopColor="var(--amber)" />
                  </linearGradient>
                </defs>
                <path className={styles.core} d={tolerance.trace} stroke={`url(#${gid}-trace)`} />
              </svg>
            </div>
          </div>

          <div className={styles.marks}>
            {tolerance.marks.map((m) => (
              <i key={m.x} className={m.major ? styles.major : undefined} style={{ left: pct(m.x) }} />
            ))}
          </div>

          <div className={styles.headTrack} data-head-track>
            <span className={styles.head} data-head />
          </div>
        </div>

        <div className={styles.xTicks}>
          {tolerance.ticks.map((mm) => (
            <span
              key={mm}
              className={`${styles.xTick}${mm === 0 ? ` ${styles.first}` : ""}${mm === LENGTH_MM ? ` ${styles.last}` : ""}${tolerance.ticksPhone.includes(mm) ? "" : ` ${styles.deskOnly}`}`}
              style={{ left: pct(X(mm)) }}
            >
              {mm}
            </span>
          ))}
        </div>
        <span className={styles.xTitle}>{LABELS.xAxis}</span>
      </div>

      <figcaption className={styles.caption}>
        {caption ? <span className={styles.captionText}>{precision.graph.caption}</span> : null}
        <span className="visually-hidden">{LABELS.summary}</span>
      </figcaption>
    </figure>
  );
}
