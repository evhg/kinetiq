"use client";

import { useId, useRef, type CSSProperties } from "react";
import { useMotion } from "@/components/motion/MotionProvider";
import { holes } from "@/content/copy";
import { gsap, useGSAP } from "@/lib/gsap";
import { PLATE, drilled, moulded } from "@/lib/graphics-bores";
import styles from "./DrilledVsMoulded.module.css";

/** Strings this graphic adds on top of holes.pair (copy.ts). */
export const LABELS = {
  drilledCallout: "Cut fibre ends",
  mouldedCallout: "Unbroken fibre",
  summary:
    "Two magnified holes at the same scale. Left, a drilled hole: straight fibres stop dead at the bore, cut, with a frayed edge. Right, a moulded hole: every fibre bends around the bore and carries on, and the wall is lined with continuous fibre.",
};

type Props = {
  className?: string;
  /** Show the callouts with leaders inside each plate. Default true. */
  callouts?: boolean;
};

const { w: W, h: H, cx: CX, cy: CY, r: R } = PLATE;
const VIEW = `0 0 ${W} ${H}`;

// Geometry is deterministic: computed once per module, identical on server and client.
const D = drilled();
const M = moulded();

/**
 * Callouts sit in the same place on both plates (upper left, 120 degrees round the bore), so the
 * pair reads as one comparison. The label is right-aligned on its elbow and set on a knockout
 * (fibres stop at its edges, as a drafting background mask does), underlined to the elbow, and a
 * plumb leader drops from the elbow straight down to the target. Plate units.
 */
const ELBOW_Y = 112;
const LEAD = { drilled: D.target, moulded: M.target };

/** Opacity for inline styles, rounded so server and client markup match exactly (Math.pow and
 * friends may differ in the last bit between Node and the browser). */
const op = (v: number) => String(Math.round(v * 1000) / 1000);

const pos = (x: number, y: number) => ({ "--x": String(x - CX), "--y": String(y - CY) }) as CSSProperties;

/**
 * G06, drilled against moulded. Two magnified bores at the same scale as a 50/50 pair: straight
 * steel tows cut dead at a frayed drilled bore, and amber streamlines that part around a moulded
 * bore and run down its wall. Server render and reduced motion show the finished pair.
 */
export function DrilledVsMoulded({ className, callouts = true }: Props) {
  const root = useRef<HTMLElement>(null);
  const { motionOn } = useMotion();
  const uid = useId().replace(/:/g, "");

  useGSAP(
    () => {
      if (!motionOn || !root.current) return;
      const el = root.current;
      const mm = gsap.matchMedia();
      mm.add("(prefers-reduced-motion: no-preference)", () => {
        const q = gsap.utils.selector(el);
        const walls = q("[data-wall]");
        const lines = q("[data-flow]");
        const glow = q("[data-glow]");
        const ticks = q("[data-tick]");
        const loose = q("[data-loose]");
        const notes = q("[data-note]");
        const STEP = 0.03;
        const wallCount = walls.length;
        // Per-line weights live in stroke-opacity, so element opacity can run 0 -> 1 and land on the
        // server-rendered state. The glow layer keeps its CSS opacity (a from-tween).
        gsap.set([...walls, ...lines, ...ticks, ...loose, ...notes], { opacity: 0 });
        const tl = gsap.timeline({ scrollTrigger: { trigger: el, start: "top 75%", once: true } });
        // Inside out: down the wall first (innermost ring), then the streamlines from the bore outward.
        tl.to(walls, {
          opacity: 1,
          duration: 0.5,
          ease: "power3.out",
          stagger: (i: number) => (wallCount - 1 - i) * STEP,
        })
          .to(
            lines,
            {
              opacity: 1,
              duration: 0.6,
              ease: "power3.out",
              stagger: (_i: number, t: Element) => Number((t as SVGElement).dataset.order) * STEP,
            },
            wallCount * STEP,
          )
          .from(glow, { opacity: 0, duration: 0.9, ease: "power2.out" }, wallCount * STEP + 0.1)
          // Then the drilled side's cut ticks snap in, in no particular order.
          .to(ticks, { opacity: 1, duration: 0.2, ease: "power2.out", stagger: { each: 0.018, from: "random" } }, ">-0.35")
          .to(loose, { opacity: 1, duration: 0.3, ease: "power2.out" }, "<0.2")
          .to(notes, { opacity: 1, duration: 0.5, ease: "power3.out", stagger: 0.08 }, ">-0.1");
      });
      return () => mm.revert();
    },
    { scope: root, dependencies: [motionOn], revertOnUpdate: true },
  );

  const { drilled: dl, moulded: ml } = LEAD;
  const [term1, rest1] = split(holes.pair.drilled);
  const [term2, rest2] = split(holes.pair.moulded);

  return (
    <figure ref={root} className={`${styles.root}${className ? ` ${className}` : ""}`}>
      <div className={styles.pair}>
        {/* ---------------- Drilled ---------------- */}
        <div className={styles.panel}>
          <div className={styles.plate}>
            <svg className={styles.svg} viewBox={VIEW} preserveAspectRatio="xMidYMid slice" aria-hidden="true" focusable="false">
              <defs>
                <Vignette id={`${uid}-ds`} color="var(--steel)" />
              </defs>
              {D.lines.map((l, i) => (
                <path key={i} d={l.d} className={styles.tow} stroke={`url(#${uid}-ds)`} style={{ strokeOpacity: op(l.o) }} />
              ))}
              <path d={D.rim} className={styles.boreFill} />
              {D.walls.map((wl, i) => (
                <path key={i} d={wl.d} className={styles.dWall} style={{ strokeOpacity: op(wl.o) }} />
              ))}
              <path d={D.rim} className={styles.dRim} />
              <path d={D.loose} className={styles.loose} data-loose />
              {D.ticks.map((t, i) => (
                <path key={i} d={t} className={styles.tick} data-tick />
              ))}
              <Crosshair />
              {callouts ? <Leader to={dl} /> : null}
            </svg>
            {callouts ? <Note to={dl}>{LABELS.drilledCallout}</Note> : null}
          </div>
          <p className={styles.caption}>
            <span className={styles.rule} aria-hidden="true" />
            <span className={styles.term}>{term1}</span> {rest1}
          </p>
        </div>

        {/* ---------------- Moulded ---------------- */}
        <div className={styles.panel}>
          <div className={styles.plate}>
            <svg className={`${styles.svg} ${styles.glow}`} viewBox={VIEW} preserveAspectRatio="xMidYMid slice" aria-hidden="true" focusable="false" data-glow>
              <defs>
                <radialGradient id={`${uid}-gv`} gradientUnits="userSpaceOnUse" cx={CX} cy={CY} r={R * 2.1}>
                  <stop offset="0.45" stopColor="var(--amber)" />
                  <stop offset="1" stopColor="var(--amber)" stopOpacity="0" />
                </radialGradient>
              </defs>
              {M.lines
                .filter((l) => l.rank < 0.14)
                .map((l, i) => (
                  <path key={i} d={l.d} className={styles.glowLine} stroke={`url(#${uid}-gv)`} />
                ))}
              <circle cx={CX} cy={CY} r={R} className={styles.glowRim} />
            </svg>
            <svg className={styles.svg} viewBox={VIEW} preserveAspectRatio="xMidYMid slice" aria-hidden="true" focusable="false">
              <defs>
                <Vignette id={`${uid}-ma`} color="var(--amber)" />
                <Vignette id={`${uid}-mh`} color="var(--amber-hot)" />
                <radialGradient id={`${uid}-bore`} gradientUnits="userSpaceOnUse" cx={CX} cy={CY} r={R}>
                  <stop offset="0" stopColor="var(--amber)" stopOpacity="0.2" />
                  <stop offset="0.55" stopColor="var(--amber)" stopOpacity="0.06" />
                  <stop offset="1" stopColor="var(--amber)" stopOpacity="0" />
                </radialGradient>
              </defs>
              {M.lines.map((l, i) => (
                <path
                  key={i}
                  d={l.d}
                  className={styles.flow}
                  stroke={`url(#${uid}-${l.rank < 0.12 ? "mh" : "ma"})`}
                  style={{ strokeOpacity: op(Math.max(0.3, 0.95 - 0.7 * l.rank)) }}
                  data-flow
                  data-order={l.order}
                />
              ))}
              <circle cx={CX} cy={CY} r={R} className={styles.boreFill} />
              <circle cx={CX} cy={CY} r={R} fill={`url(#${uid}-bore)`} />
              {M.walls.map((wl, i) => (
                <circle key={i} cx={CX} cy={CY} r={wl.r} className={i === 0 ? styles.mRim : styles.mWall} style={i === 0 ? undefined : { strokeOpacity: op(wl.o) }} data-wall />
              ))}
              <Crosshair />
              {callouts ? <Leader to={ml} /> : null}
            </svg>
            {callouts ? <Note to={ml}>{LABELS.mouldedCallout}</Note> : null}
          </div>
          <p className={styles.caption}>
            <span className={`${styles.rule} ${styles.ruleAmber}`} aria-hidden="true" />
            <span className={styles.term}>{term2}</span> {rest2}
          </p>
        </div>
      </div>
      <figcaption className="visually-hidden">{LABELS.summary}</figcaption>
    </figure>
  );
}

/** "Drilled: every fibre ..." -> ["Drilled:", "every fibre ..."] */
function split(s: string): [string, string] {
  const i = s.indexOf(":");
  return i < 0 ? ["", s] : [s.slice(0, i + 1), s.slice(i + 1).trim()];
}

/** Plumb leader from the label elbow (directly above the target) down to it. */
function Leader({ to }: { to: [number, number] }) {
  const [tx, ty] = to;
  return <line className={styles.leader} x1={tx} y1={ELBOW_Y} x2={tx} y2={ty} data-note />;
}

/**
 * The callout label (HTML, so it never shrinks) and its target dot, a fixed size in px at every
 * viewport (an SVG dot would scale down with the plate to about 1 px on phones).
 */
function Note({ to, children }: { to: [number, number]; children: string }) {
  return (
    <>
      <span className={styles.note} style={pos(to[0], ELBOW_Y)} data-note>
        {children}
      </span>
      <span className={styles.target} style={pos(to[0], to[1])} aria-hidden="true" data-note />
    </>
  );
}

/**
 * Stroke paint that fades the fibres towards the plate corners (a radial vignette). A gradient paint
 * costs nothing to repaint; an SVG mask is re-rasterised on every animation frame.
 */
function Vignette({ id, color }: { id: string; color: string }) {
  return (
    <radialGradient id={id} gradientUnits="userSpaceOnUse" cx={CX} cy={CY} r={W * 0.56}>
      <stop offset="0.35" stopColor={color} />
      <stop offset="0.8" stopColor={color} stopOpacity="0.35" />
      <stop offset="1" stopColor={color} stopOpacity="0.12" />
    </radialGradient>
  );
}

/** Dash-dot centrelines through the bore (ISO 128), a little past the rim. */
function Crosshair() {
  const e = R + 46;
  return (
    <g className={styles.centre}>
      <line x1={CX - e} x2={CX + e} y1={CY} y2={CY} />
      <line x1={CX} x2={CX} y1={CY - e} y2={CY + e} />
    </g>
  );
}
