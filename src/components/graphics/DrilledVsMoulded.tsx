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
  mouldedCallout: "Fibre wraps the wall",
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

/** Leader geometry in plate units: from the label shoulder to the target. */
const LEAD = {
  drilled: { x0: 120, x1: 330, y: 126, target: D.target },
  moulded: { x0: 980, x1: 770, y: 126, target: [CX + R * Math.cos(-Math.PI / 4) + 6, CY + R * Math.sin(-Math.PI / 4) - 6] as [number, number] },
};

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
        gsap.set([...walls, ...lines, ...glow, ...ticks, ...loose, ...notes], { opacity: 0 });
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
          .to(glow, { opacity: 1, duration: 0.9, ease: "power2.out" }, wallCount * STEP + 0.1)
          // Then the drilled side's cut ticks snap in, in no particular order.
          .to(ticks, { opacity: 1, duration: 0.2, ease: "power2.out", stagger: { each: 0.018, from: "random" } }, ">-0.35")
          .to(loose, { opacity: 1, duration: 0.3, ease: "power2.out" }, "<0.2")
          .to(notes, { opacity: 1, duration: 0.5, ease: "power3.out", stagger: 0.08 }, ">-0.1");
      });
      return () => mm.revert();
    },
    { scope: root, dependencies: [motionOn], revertOnUpdate: true },
  );

  const [dl, ml] = [LEAD.drilled, LEAD.moulded];
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
                <radialGradient id={`${uid}-v`} gradientUnits="userSpaceOnUse" cx={CX} cy={CY} r={W * 0.56}>
                  <stop offset="0.35" stopColor="#fff" />
                  <stop offset="0.8" stopColor="#fff" stopOpacity="0.35" />
                  <stop offset="1" stopColor="#fff" stopOpacity="0.12" />
                </radialGradient>
                <filter id={`${uid}-soft`} x="-20%" y="-60%" width="140%" height="220%">
                  <feGaussianBlur stdDeviation="10" />
                </filter>
                <mask id={`${uid}-md`} maskUnits="userSpaceOnUse" x="0" y="0" width={W} height={H}>
                  <rect width={W} height={H} fill={`url(#${uid}-v)`} />
                  {callouts ? <rect x={dl.x0 - 24} y={dl.y - 74} width={300} height={66} fill="#000" filter={`url(#${uid}-soft)`} /> : null}
                </mask>
              </defs>
              <g mask={`url(#${uid}-md)`}>
                {D.lines.map((l, i) => (
                  <path key={i} d={l.d} className={l.cut ? styles.towCut : styles.tow} style={{ opacity: l.o }} />
                ))}
              </g>
              <circle cx={CX} cy={CY} r={R} className={styles.boreFill} />
              <path d={D.wall} className={styles.dWall} />
              <path d={D.rim} className={styles.dRim} />
              <path d={D.loose} className={styles.loose} data-loose />
              {D.ticks.map((t, i) => (
                <path key={i} d={t} className={styles.tick} data-tick />
              ))}
              <Crosshair />
              {callouts ? (
                <g data-note>
                  <polyline className={styles.leader} points={`${dl.x0},${dl.y} ${dl.x1},${dl.y} ${dl.target[0] - 6},${dl.target[1] - 6}`} />
                  <circle className={styles.dot} cx={dl.target[0] - 3} cy={dl.target[1] - 3} r="3.5" />
                </g>
              ) : null}
            </svg>
            {callouts ? (
              <span className={`${styles.note} ${styles.noteLeft}`} style={pos(dl.x0, dl.y)} data-note>
                {LABELS.drilledCallout}
              </span>
            ) : null}
          </div>
          <p className={styles.caption}>
            <span className={styles.rule} aria-hidden="true" />
            <span className={styles.term}>{term1}</span> {rest1}
          </p>
        </div>

        {/* ---------------- Moulded ---------------- */}
        <div className={`${styles.panel} ${styles.mouldedPanel}`}>
          <div className={styles.plate}>
            <svg className={`${styles.svg} ${styles.glow}`} viewBox={VIEW} preserveAspectRatio="xMidYMid slice" aria-hidden="true" focusable="false" data-glow>
              {M.lines
                .filter((l) => l.rank < 0.2)
                .map((l, i) => (
                  <path key={i} d={l.d} className={styles.glowLine} />
                ))}
              <circle cx={CX} cy={CY} r={R} className={styles.glowRim} />
            </svg>
            <svg className={styles.svg} viewBox={VIEW} preserveAspectRatio="xMidYMid slice" aria-hidden="true" focusable="false">
              <defs>
                <radialGradient id={`${uid}-v2`} gradientUnits="userSpaceOnUse" cx={CX} cy={CY} r={W * 0.56}>
                  <stop offset="0.35" stopColor="#fff" />
                  <stop offset="0.8" stopColor="#fff" stopOpacity="0.35" />
                  <stop offset="1" stopColor="#fff" stopOpacity="0.12" />
                </radialGradient>
                <mask id={`${uid}-mm`} maskUnits="userSpaceOnUse" x="0" y="0" width={W} height={H}>
                  <rect width={W} height={H} fill={`url(#${uid}-v2)`} />
                  {callouts ? <rect x={ml.x0 - 276} y={ml.y - 74} width={300} height={66} fill="#000" filter={`url(#${uid}-soft)`} /> : null}
                </mask>
                <radialGradient id={`${uid}-bore`} gradientUnits="userSpaceOnUse" cx={CX} cy={CY} r={R}>
                  <stop offset="0" stopColor="var(--amber)" stopOpacity="0.2" />
                  <stop offset="0.55" stopColor="var(--amber)" stopOpacity="0.06" />
                  <stop offset="1" stopColor="var(--amber)" stopOpacity="0" />
                </radialGradient>
              </defs>
              <g mask={`url(#${uid}-mm)`}>
                {M.lines.map((l, i) => (
                  <path
                    key={i}
                    d={l.d}
                    className={l.rank < 0.12 ? styles.flowHot : styles.flow}
                    style={{ opacity: Math.max(0.3, 0.95 - 0.7 * l.rank) }}
                    data-flow
                    data-order={l.order}
                  />
                ))}
              </g>
              <circle cx={CX} cy={CY} r={R} className={styles.boreFill} />
              <circle cx={CX} cy={CY} r={R} fill={`url(#${uid}-bore)`} />
              {M.walls.map((wl, i) => (
                <circle key={i} cx={CX} cy={CY} r={wl.r} className={i === 0 ? styles.mRim : styles.mWall} style={i === 0 ? undefined : { opacity: wl.o }} data-wall />
              ))}
              <Crosshair />
              {callouts ? (
                <g data-note>
                  <polyline className={styles.leader} points={`${ml.x0},${ml.y} ${ml.x1},${ml.y} ${ml.target[0] + 4},${ml.target[1] - 4}`} />
                  <circle className={styles.dot} cx={ml.target[0] + 1} cy={ml.target[1] - 1} r="3.5" />
                </g>
              ) : null}
            </svg>
            {callouts ? (
              <span className={`${styles.note} ${styles.noteRight}`} style={pos(ml.x0, ml.y)} data-note>
                {LABELS.mouldedCallout}
              </span>
            ) : null}
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
