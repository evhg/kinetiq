"use client";

import { useId, useRef, type RefObject } from "react";
import { useMotion } from "@/components/motion/MotionProvider";
import { feel } from "@/content/copy";
import { gsap, useGSAP } from "@/lib/gsap";
import { VB, pct, yAt } from "@/lib/graphics-plot";
import { envelopeTable, vibration } from "@/lib/graphics-vibration";
import styles from "./VibrationGraph.module.css";

/** Strings this graphic adds on top of feel.graph (copy.ts). */
export const LABELS = {
  yAxis: "Vibration",
  xAxis: "Time after impact",
  summary: `Graph. After impact, the ${feel.graph.glued.toLowerCase()} keeps ringing and only settles at the end of the window. KINETIQ settles under 5% of its starting vibration in about a third of the time.`,
  tableCaption: `Vibration left after impact, as a share of the ${feel.graph.glued.toLowerCase()}'s starting vibration`,
  tableTime: "Time after impact, share of the window",
};

type Props = {
  className?: string;
  /**
   * Scroll-driven instead of playing once on entry. With `timelineRef` the timeline is handed
   * to the parent (which pins the chapter and sets `progress()`); without it the graph scrubs
   * itself between entering the viewport and its centre.
   */
  scrub?: boolean;
  timelineRef?: RefObject<gsap.core.Timeline | null>;
  /**
   * Fill the parent's height instead of the plot's own width-based height (the pinned Feel chapter, where the
   * headline, the graph and the three points share one screen). The parent must have a definite height.
   */
  fill?: boolean;
};

const V = `0 0 ${VB} ${VB}`;
/** How far each amber fan line swings out before the fan snaps together. */
const OPEN = 5.5;

/**
 * G02, the Feel chapter centrepiece. A glued racket rings and decays slowly (grey line and a
 * wide fan of impact points); KINETIQ settles in a third of the time and its fan collapses onto
 * one line. Server render and reduced motion show the finished graph.
 */
export function VibrationGraph({ className, scrub = false, timelineRef, fill = false }: Props) {
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
        if (!scrub && el.getBoundingClientRect().top < window.innerHeight * 0.75) return;
        const q = gsap.utils.selector(el);
        const [wipe] = q("[data-wipe]");
        const [inner] = q("[data-wipe-inner]");
        const [track] = q("[data-head-track]");
        const head = q("[data-head]");
        const fan = q("[data-kfan] path");
        const labels = q("[data-label]");
        const marker = q("[data-marker]");
        const pts = vibration.head;

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
        gsap.set(fan, { svgOrigin: `0 ${vibration.zeroY}` });
        gsap.set(head, { opacity: 0 });
        gsap.set(labels, { opacity: 0, y: 8 });
        gsap.set(marker, { opacity: 0, y: -24 });

        const handOver = scrub && !!timelineRef;
        const tl = gsap.timeline({
          paused: handOver,
          scrollTrigger: handOver
            ? undefined
            : scrub
              ? { trigger: el, start: "top 80%", end: "center 45%", scrub: 0.6 }
              : { trigger: el, start: "top 75%", once: true },
        });
        tl.to(state, { p: 1, duration: 1.2, ease: "power3.out", onUpdate: render }, 0)
          .to(head, { opacity: 1, duration: 0.15, ease: "power1.out" }, 0)
          .to(
            fan,
            {
              scaleY: (_i: number, t: Element) => {
                const r = Number((t as SVGElement).dataset.r) || 1;
                return (1 + OPEN * (r - 1)) / r;
              },
              duration: 0.45,
              ease: "power2.out",
            },
            0.04,
          )
          .to(fan, { scaleY: 1, duration: 0.7, ease: "expo.out" }, 0.55)
          .to(labels, { opacity: 1, y: 0, duration: 0.5, ease: "power3.out", stagger: 0.08 }, 0.85)
          .to(head, { opacity: 0, duration: 0.4, ease: "power2.out" }, 1.0)
          .to(marker, { opacity: 1, y: 0, duration: 0.5, ease: "expo.out" }, 1.2);
        if (handOver && timelineRef) timelineRef.current = tl;
        return () => {
          if (handOver && timelineRef) timelineRef.current = null;
        };
      });
      return () => mm.revert();
    },
    { scope: root, dependencies: [motionOn, scrub], revertOnUpdate: true },
  );

  const rows = envelopeTable();

  return (
    <figure ref={root} className={`${styles.root}${className ? ` ${className}` : ""}`} data-fill={fill || undefined}>
      <div className={styles.chart} aria-hidden="true">
        <span className={styles.yTitle}>{LABELS.yAxis}</span>
        <div className={styles.plot}>
          <svg className={styles.layer} viewBox={V} preserveAspectRatio="none" focusable="false">
            {vibration.rules.map((y) => (
              <line key={y} className={styles.rule} x1="0" x2={VB} y1={y} y2={y} />
            ))}
            <line className={styles.zero} x1="0" x2={VB} y1={vibration.zeroY} y2={vibration.zeroY} />
          </svg>

          <div className={styles.wipe} data-wipe>
            <div className={styles.wipeInner} data-wipe-inner>
              <svg className={styles.layer} viewBox={V} preserveAspectRatio="none" focusable="false">
                <g className={styles.gluedFan}>
                  {vibration.gluedFan.map((l, i) => (
                    <path key={i} d={l.d} className={l.phone ? undefined : styles.extra} />
                  ))}
                </g>
                <path className={styles.glued} d={vibration.glued} />
                <g className={styles.kFan} data-kfan>
                  {vibration.kinetiqFan.map((l, i) => (
                    <path key={i} d={l.d} data-r={l.r.toFixed(4)} className={l.phone ? undefined : styles.extra} />
                  ))}
                </g>
              </svg>
              <svg
                className={`${styles.layer} ${styles.halo}`}
                viewBox={V}
                preserveAspectRatio="none"
                focusable="false"
              >
                <path d={vibration.kinetiq} />
              </svg>
              <svg
                className={`${styles.layer} ${styles.glow}`}
                viewBox={V}
                preserveAspectRatio="none"
                focusable="false"
              >
                <path d={vibration.kinetiq} />
              </svg>
              <svg className={styles.layer} viewBox={V} preserveAspectRatio="none" focusable="false">
                <defs>
                  <linearGradient id={`${gid}-core`} gradientUnits="userSpaceOnUse" x1="0" y1="0" x2={VB} y2="0">
                    <stop offset="0" stopColor="var(--amber-hot)" />
                    <stop offset="0.3" stopColor="var(--amber-hot)" />
                    <stop offset="0.55" stopColor="var(--amber)" />
                    <stop offset="1" stopColor="var(--amber)" />
                  </linearGradient>
                </defs>
                <path className={styles.core} d={vibration.kinetiq} stroke={`url(#${gid}-core)`} />
              </svg>
            </div>
          </div>

          <div className={styles.marker} style={{ left: pct(vibration.settleX) }} data-marker>
            <span className={styles.markerLabel}>{feel.graph.settled}</span>
            <span className={styles.markerRing} style={{ top: pct(vibration.settleY) }} />
          </div>
          <span className={`${styles.label} ${styles.labelGlued}`} data-label>
            {feel.graph.glued}
          </span>
          <span className={`${styles.label} ${styles.labelK}`} data-label>
            {feel.graph.kinetiq}
          </span>
          <div className={styles.ticks}>
            {vibration.ticks.map((t) => (
              <i key={t.x} className={t.major ? styles.major : undefined} style={{ left: pct(t.x) }} />
            ))}
          </div>
          <div className={styles.headTrack} data-head-track>
            <span className={styles.head} data-head />
          </div>
        </div>
        <span className={styles.xTitle}>{LABELS.xAxis}</span>
      </div>

      <figcaption>
        <span className="visually-hidden">{LABELS.summary}</span>
        <div className="visually-hidden">
          <table>
            <caption>{LABELS.tableCaption}</caption>
            <thead>
              <tr>
                <th scope="col">{LABELS.tableTime}</th>
                <th scope="col">{feel.graph.glued}</th>
                <th scope="col">{feel.graph.kinetiq}</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.t}>
                  <th scope="row">{`${Math.round(r.t * 100)}%`}</th>
                  <td>{`${r.glued}%`}</td>
                  <td>{`${r.kinetiq}%`}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </figcaption>
    </figure>
  );
}
