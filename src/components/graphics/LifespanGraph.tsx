"use client";

import { useId, useRef, type CSSProperties } from "react";
import { useMotion } from "@/components/motion/MotionProvider";
import { durability } from "@/content/copy";
import { gsap, useGSAP } from "@/lib/gsap";
import { VB, pct } from "@/lib/graphics-plot";
import styles from "./LifespanGraph.module.css";

const { graph } = durability;

/** Strings this graphic adds on top of durability.graph (copy.ts). */
export const LABELS = {
  summary:
    "Graph on a five-year axis. Most padel rackets are spent between one and two years of recreational play, by brand and retailer guidance. KINETIQ is built to last five years at two 90-minute sessions a week, about 160,000 ball strikes in all. An independent lab will run fatigue tests to that count before we ship.",
};

/* ---------- geometry (normalised 1000 x 1000 viewBox, y down) ---------- */

const YEARS = 5;
const X = (years: number) => (years / YEARS) * VB;
/** Lane heights: the typical racket above, KINETIQ below with room for its numeral. */
const LANE = { typical: 360, kinetiq: 780 } as const;
/** Where most padel rackets are spent: one to two years. */
const SPENT = { from: X(1), to: X(2) };

/**
 * The typical lane: whole to one year, then it frays out across the spent window in shorter, fainter dashes.
 * Each dash ends on its cell's right edge, so a clear gap follows the solid line at one year and the last
 * dash ends exactly at two: the fray spans the window it labels.
 */
const FRAY_N = 8;
const FRAY = Array.from({ length: FRAY_N }, (_, i) => {
  const step = (SPENT.to - SPENT.from) / FRAY_N;
  const k = i / (FRAY_N - 1);
  const end = SPENT.from + (i + 1) * step;
  return { x1: end - step * (0.62 - k * 0.42), x2: end, opacity: 0.8 * (1 - k) + 0.12 };
});

const yearRules = Array.from({ length: YEARS - 1 }, (_, i) => X(i + 1));
const halfRules = Array.from({ length: YEARS }, (_, i) => X(i + 0.5));
const months = Array.from({ length: YEARS * 12 + 1 }, (_, m) => ({ x: X(m / 12), major: m % 12 === 0 }));
const years = Array.from({ length: YEARS + 1 }, (_, i) => i);

const V = `0 0 ${VB} ${VB}`;
const KINETIQ_PATH = `M0 ${LANE.kinetiq}H${VB}`;

type Props = {
  className?: string;
};

/**
 * G14, Durability section. A lifespan comparison on a five-year axis: the typical racket's line frays out
 * across the one-to-two-year window where most padel rackets are spent, while the KINETIQ line runs on to
 * five years. Server render and reduced motion show the finished graph; motion draws the typical lane,
 * then the KINETIQ trace behind a glow head, and sets the five-year numeral once the head arrives.
 */
export function LifespanGraph({ className }: Props) {
  const root = useRef<HTMLElement>(null);
  const { motionOn } = useMotion();
  const gid = useId().replace(/:/g, "");

  useGSAP(
    () => {
      if (!motionOn || !root.current) return;
      const el = root.current;
      const mm = gsap.matchMedia();
      mm.add("(prefers-reduced-motion: no-preference)", () => {
        // Already past the trigger when motion switches on (a reload mid-page, a hash link): keep the
        // finished graph instead of hiding it and drawing it again.
        if (el.getBoundingClientRect().top < window.innerHeight * 0.75) return;
        const q = gsap.utils.selector(el);

        // A wipe is a clipped box sliding in from the left with its contents counter-sliding, so the
        // line appears to draw while only transforms move.
        const wiper = (name: string) => {
          const [outer] = q(`[data-wipe="${name}"]`);
          const [inner] = q(`[data-wipe="${name}"] > [data-wipe-inner]`);
          const setOuter = gsap.quickSetter(outer, "xPercent");
          const setInner = gsap.quickSetter(inner, "xPercent");
          const state = { p: 0 };
          const render = () => {
            setOuter((state.p - 1) * 100);
            setInner((1 - state.p) * 100);
          };
          render();
          return { state, render };
        };
        const typical = wiper("typical");
        const kinetiq = wiper("kinetiq");
        // The head sits at the track's right end and the track slides in from the left, so at rest the
        // track is back in the plot and nothing hangs past the page edge.
        const [track] = q("[data-head-track]");
        const setHead = gsap.quickSetter(track, "xPercent");
        const head = q("[data-head]");
        const drawKinetiq = () => {
          kinetiq.render();
          setHead((kinetiq.state.p - 1) * 100);
        };
        setHead(-100);

        const spentWindow = q("[data-window]");
        const typicalSpan = q("[data-span='typical']");
        const finish = q("[data-finish]");
        gsap.set(spentWindow, { opacity: 0 });
        gsap.set(typicalSpan, { opacity: 0, y: 10 });
        gsap.set(finish, { opacity: 0, y: 12 });
        gsap.set(head, { opacity: 0 });

        gsap
          .timeline({ scrollTrigger: { trigger: el, start: "top 75%", once: true } })
          .to(spentWindow, { opacity: 1, duration: 0.4, ease: "power2.out" }, 0)
          .to(typical.state, { p: 1, duration: 0.7, ease: "power2.out", onUpdate: typical.render }, 0.1)
          .to(typicalSpan, { opacity: 1, y: 0, duration: 0.45, ease: "power3.out" }, 0.5)
          .to(head, { opacity: 1, duration: 0.2, ease: "power1.out" }, 0.55)
          .to(kinetiq.state, { p: 1, duration: 1.5, ease: "power2.inOut", onUpdate: drawKinetiq }, 0.55)
          .to(finish, { opacity: 1, y: 0, duration: 0.5, ease: "power3.out", stagger: 0.06 }, 1.9)
          .to(head, { opacity: 0, duration: 0.4, ease: "power2.out" }, 2.0);
      });
      return () => mm.revert();
    },
    { scope: root, dependencies: [motionOn], revertOnUpdate: true },
  );

  return (
    <figure ref={root} className={`${styles.root}${className ? ` ${className}` : ""}`}>
      <div className={styles.chart} aria-hidden="true">
        <div className={styles.plot} style={{ "--lane-t": pct(LANE.typical), "--lane-k": pct(LANE.kinetiq) } as CSSProperties}>
          {/* The window where most padel rackets are spent, one to two years, lit like G04's tolerance window. */}
          <div className={styles.window} style={{ left: pct(SPENT.from), width: pct(SPENT.to - SPENT.from) }} data-window />

          {/* The vertical rules break where the lane labels and the KINETIQ note sit (.rules and .window in the CSS), so no
              line strikes through a word. */}
          <svg className={`${styles.layer} ${styles.rules}`} viewBox={V} preserveAspectRatio="none" focusable="false">
            {halfRules.map((x) => (
              <line key={x} className={`${styles.rule} ${styles.half} ${styles.deskOnly}`} x1={x} x2={x} y1="0" y2={VB} />
            ))}
            {yearRules.map((x) => (
              <line key={x} className={styles.rule} x1={x} x2={x} y1="0" y2={VB} />
            ))}
            <line className={styles.axis} x1="0" x2={VB} y1={VB} y2={VB} />
          </svg>

          {/* Most padel rackets: whole to one year, then fraying out by two. */}
          <div className={styles.wipe} data-wipe="typical">
            <div className={styles.wipeInner} data-wipe-inner>
              <svg className={styles.layer} viewBox={V} preserveAspectRatio="none" focusable="false">
                <line className={styles.typical} x1="0" x2={SPENT.from} y1={LANE.typical} y2={LANE.typical} />
                {FRAY.map((f) => (
                  <line
                    key={f.x1}
                    className={styles.typical}
                    style={{ strokeOpacity: f.opacity }}
                    x1={f.x1}
                    x2={f.x2}
                    y1={LANE.typical}
                    y2={LANE.typical}
                  />
                ))}
              </svg>
            </div>
          </div>
          <span className={`${styles.ring} ${styles.ringTypical}`} style={{ top: pct(LANE.typical) }} />
          <span className={`${styles.laneLabel} ${styles.typicalLabel}`} style={{ top: pct(LANE.typical) }}>
            {graph.typical}
          </span>
          <p
            className={`${styles.span} ${styles.spanTypical}`}
            style={{ left: pct(SPENT.from), bottom: pct(VB - LANE.typical) }}
            data-span="typical"
          >
            <span className={styles.spanValue}>{graph.typicalSpan.value}</span>
            <span className={styles.spanUnit}>{graph.typicalSpan.unit}</span>
          </p>

          {/* KINETIQ: one amber trace, on to five years. */}
          <div className={styles.wipe} data-wipe="kinetiq">
            <div className={styles.wipeInner} data-wipe-inner>
              <svg className={`${styles.layer} ${styles.halo}`} viewBox={V} preserveAspectRatio="none" focusable="false">
                <path d={KINETIQ_PATH} />
              </svg>
              <svg className={`${styles.layer} ${styles.glow}`} viewBox={V} preserveAspectRatio="none" focusable="false">
                <path d={KINETIQ_PATH} />
              </svg>
              {/* Light spilling from the trace onto the floor of the plot. */}
              <div className={styles.spill} style={{ top: pct(LANE.kinetiq) }} />
              <svg className={styles.layer} viewBox={V} preserveAspectRatio="none" focusable="false">
                <defs>
                  <linearGradient id={`${gid}-trace`} gradientUnits="userSpaceOnUse" x1="0" y1="0" x2={VB} y2="0">
                    <stop offset="0" stopColor="var(--amber)" />
                    <stop offset="0.7" stopColor="var(--amber)" />
                    <stop offset="1" stopColor="var(--amber-hot)" />
                  </linearGradient>
                </defs>
                <path className={styles.core} d={KINETIQ_PATH} stroke={`url(#${gid}-trace)`} />
              </svg>
            </div>
          </div>
          <span className={`${styles.ring} ${styles.ringKinetiq}`} style={{ top: pct(LANE.kinetiq) }} />
          <span className={`${styles.laneLabel} ${styles.kinetiqLabel}`} style={{ top: pct(LANE.kinetiq) }}>
            {graph.kinetiq}
          </span>
          <span className={styles.end} style={{ top: pct(LANE.kinetiq) }} data-finish />
          <p className={`${styles.span} ${styles.spanKinetiq}`} style={{ bottom: pct(VB - LANE.kinetiq) }} data-finish>
            <span className={styles.spanValue}>{graph.kinetiqSpan.value}</span>
            <span className={styles.spanUnit}>{graph.kinetiqSpan.unit}</span>
          </p>
          <span className={styles.note} style={{ top: pct(LANE.kinetiq) }} data-finish>
            {graph.kinetiqNote}
          </span>

          <div className={styles.headTrack} style={{ top: pct(LANE.kinetiq) }} data-head-track>
            <span className={styles.head} data-head />
          </div>

          <div className={styles.marks}>
            {months.map((m) => (
              <i key={m.x} className={m.major ? styles.major : undefined} style={{ left: pct(m.x) }} />
            ))}
          </div>
        </div>

        <div className={styles.xTicks}>
          {years.map((y) => (
            <span
              key={y}
              className={`${styles.xTick}${y === 0 ? ` ${styles.first}` : ""}${y === YEARS ? ` ${styles.last}` : ""}`}
              style={{ left: pct(X(y)) }}
            >
              {y}
            </span>
          ))}
        </div>
        <span className={styles.xTitle}>{graph.xAxis}</span>
      </div>

      <figcaption>
        <span className="visually-hidden">{LABELS.summary}</span>
      </figcaption>
    </figure>
  );
}
