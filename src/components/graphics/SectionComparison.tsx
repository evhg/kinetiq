"use client";

import { useId, useRef, type CSSProperties, type RefObject } from "react";
import { useMotion } from "@/components/motion/MotionProvider";
import { unibody } from "@/content/copy";
import { gsap, useGSAP } from "@/lib/gsap";
import {
  DRIFT,
  boreRects,
  centrelines,
  ROW,
  VB,
  WINDOW,
  hatchBox,
  kinetiq,
  pctX,
  pctY,
  tubular,
  twoLines,
  viewBox,
  type Callout,
} from "@/lib/graphics-section";
import styles from "./SectionComparison.module.css";

const { left, right } = unibody.section;
const [partTube, partFace] = left.parts;
const [lineShell, lineEdge, lineBalance] = right.lines;

/** Strings this graphic adds on top of unibody.section (copy.ts). */
export const LABELS = {
  tubularSummary:
    "Section through a tubular racket: a separate frame tube at each edge, joined to the faces and the core at a bond line on each side. The drilled hole cuts through the core and leaves it open to the air.",
  kinetiqSummary:
    "Section through KINETIQ at the same scale: no frame tube. One continuous carbon shell runs around both edges and lines every hole wall, sealing the core inside it.",
};

/** Narrow containers (phones, side by side) switch to the one-edge layout. Keep in step with the CSS. */
const HALF_BELOW = 340;

type Variant = "tubular" | "kinetiq";
type Set = { full: Callout[]; half: Callout[] };

// ------------------------------------------------------------------ callouts (mm, see graphics-section.ts)

const TUBULAR: Set = {
  full: [
    { key: "tube", text: partTube, at: [8, 1.1], anchor: [0, ROW.top1], side: "left", band: "top" },
    { key: "face-top", text: partFace, at: [66, -0.6], anchor: [62, ROW.top1], side: "left", band: "top" },
    { key: "bond-right", text: left.glue, at: [92.9, 10], anchor: [99, ROW.top1], side: "left", band: "top", tone: "bond" },
    { key: "bond-left", text: left.glue, at: [19.1, 28], anchor: [13.5, ROW.bottom1], side: "right", band: "bottom", tone: "bond" },
    // the core's bare wall, where the drilled hole cuts it open
    { key: "core", text: left.core, at: [28.7, 25], anchor: [24, ROW.bottom1], side: "left", band: "bottom" },
    { key: "face-bottom", text: partFace, at: [66, 38.6], anchor: [62, ROW.bottom1], side: "left", band: "bottom" },
  ],
  half: [
    { key: "tube", text: partTube, at: [8, 1.1], anchor: [-3, ROW.top2], side: "left", band: "top" },
    { key: "face-top", text: partFace, at: [47, -0.6], anchor: [57, ROW.top1], side: "right", band: "top" },
    { key: "bond-left", text: left.glue, at: [19.1, 30], anchor: [10.5, ROW.bottom1], side: "right", band: "bottom", tone: "bond" },
    { key: "core", text: left.core, at: [28.7, 25], anchor: [21.5, ROW.bottom1], side: "left", band: "bottom" },
  ],
};

const KINETIQ: Set = {
  full: [
    { key: "shell", text: lineShell, at: [66, 0], anchor: [58, ROW.top1], side: "right", band: "top", tone: "shell" },
    { key: "edge", text: lineEdge, at: [108.78, 3.22], anchor: [115, ROW.top1], side: "right", band: "top", tone: "shell", wrap: true },
    { key: "balance", text: lineBalance, at: [2.2, 24], anchor: [-1.5, ROW.bottom1], side: "left", band: "bottom", tone: "shell" },
    { key: "core", text: right.core, at: [95, 22], anchor: [80, ROW.bottom1], side: "left", band: "bottom", tone: "shell" },
  ],
  half: [
    { key: "shell", text: lineShell, at: [91, 0], anchor: [86.5, ROW.top1], side: "right", band: "top", tone: "shell", wrap: true },
    // One edge has room for three callouts: the sealed core takes the balance line's place (beat B's body
    // still says where the grams go).
    { key: "core", text: right.core, at: [101, 21], anchor: [116.5, ROW.top2], side: "right", band: "top", tone: "shell" },
    { key: "edge", text: lineEdge, at: [108.78, 34.78], anchor: [114.5, ROW.bottom1], side: "right", band: "bottom", tone: "shell", wrap: true },
  ],
};

// ------------------------------------------------------------------ frame geometry (CSS variables)

type Win = { x0: number; x1: number; y0: number; y1: number };
const pc = (v: number) => `${(v * 100).toFixed(4)}%`;
const win = (name: string, wd: Win) => {
  const w = wd.x1 - wd.x0;
  const h = wd.y1 - wd.y0;
  return {
    [`--ar-${name}`]: `${w} / ${h}`,
    [`--cw-${name}`]: pc(VB.w / w),
    [`--ch-${name}`]: pc(VB.h / h),
    [`--cl-${name}`]: pc(-(wd.x0 - VB.x) / w),
    [`--ct-${name}`]: pc(-(wd.y0 - VB.y) / h),
  };
};

/** The frame shows a window onto the full canvas; CSS picks the window by container width. */
function frameVars(variant: Variant): CSSProperties {
  return { ...win("full", WINDOW.full), ...win("wide", WINDOW.wide), ...win("half", WINDOW[variant]) } as CSSProperties;
}

// ------------------------------------------------------------------ pieces

function Leaders({ set }: { set: Set }) {
  const draw = (c: Callout) => (
    <g key={c.key} className={c.tone === "shell" ? styles.leaderShell : c.tone === "bond" ? styles.leaderBond : styles.leaderPart}>
      <path d={`M${c.anchor[0]} ${c.anchor[1]}L${c.at[0]} ${c.at[1]}`} vectorEffect="non-scaling-stroke" />
      <path className={styles.dot} d={`M${c.at[0]} ${c.at[1]}h0.001`} vectorEffect="non-scaling-stroke" />
    </g>
  );
  return (
    <svg className={styles.layer} viewBox={viewBox} focusable="false" aria-hidden="true">
      <g className={styles.full}>{set.full.map(draw)}</g>
      <g className={styles.half}>{set.half.map(draw)}</g>
    </svg>
  );
}

function Labels({ set }: { set: Set }) {
  const put = (c: Callout, which: "full" | "half") => (
    <span
      key={`${which}-${c.key}`}
      className={`${styles.label} ${styles[which]}`}
      data-side={c.side}
      data-band={c.band}
      data-tone={c.tone ?? "part"}
      style={{ left: pctX(c.anchor[0]), top: pctY(c.anchor[1]) }}
    >
      {c.wrap
        ? twoLines(c.text).map((line) => (
            <span key={line} className={styles.line}>
              {line}
            </span>
          ))
        : c.text}
    </span>
  );
  return (
    <div className={styles.labels} aria-hidden="true">
      {set.full.map((c) => put(c, "full"))}
      {set.half.map((c) => put(c, "half"))}
    </div>
  );
}

/** Bore shade and ISO centrelines, shared by both drawings. */
function Construction({ uid }: { uid: string }) {
  const shade = `${uid}-bore`;
  return (
    <>
      <defs>
        <linearGradient id={shade} x1="0" x2="1" y1="0" y2="0">
          <stop offset="0" stopColor="var(--steel)" stopOpacity="0.015" />
          <stop offset="0.38" stopColor="var(--steel)" stopOpacity="0.09" />
          <stop offset="0.62" stopColor="var(--steel)" stopOpacity="0.07" />
          <stop offset="1" stopColor="var(--steel)" stopOpacity="0.01" />
        </linearGradient>
      </defs>
      {boreRects.map((r) => (
        <rect key={r.x} x={r.x} y={r.y} width={r.w} height={r.h} fill={`url(#${shade})`} />
      ))}
      <path className={styles.centre} d={`${centrelines.mid}${centrelines.holes}`} vectorEffect="non-scaling-stroke" />
    </>
  );
}

function TubularDrawing({ uid }: { uid: string }) {
  const clip = `${uid}-core`;
  const glow = `${uid}-glow`;
  return (
    <svg className={`${styles.layer} ${styles.drawing}`} viewBox={viewBox} focusable="false" aria-hidden="true">
      <defs>
        <clipPath id={clip} clipPathUnits="userSpaceOnUse">
          <path d={tubular.coreClip} />
        </clipPath>
        <filter id={glow} filterUnits="userSpaceOnUse" x={VB.x} y={VB.y} width={VB.w} height={VB.h}>
          <feGaussianBlur stdDeviation="0.7" />
        </filter>
      </defs>

      <Construction uid={uid} />
      {/* the core stays put; everything else drifts away from it */}
      <g>
        <path className={styles.bore} d={tubular.bores} vectorEffect="non-scaling-stroke" />
        <path className={styles.hatch} d={hatchBox} clipPath={`url(#${clip})`} vectorEffect="non-scaling-stroke" />
        <path className={styles.part} d={tubular.core} vectorEffect="non-scaling-stroke" />
      </g>
      {tubular.faces.map((f, i) => (
        <g key={i} transform={`translate(${f.drift[0]} ${f.drift[1]})`} data-g07="drift" data-dx={f.drift[0]} data-dy={f.drift[1]}>
          <path className={styles.rim} d={f.rims} vectorEffect="non-scaling-stroke" />
          <path className={`${styles.part} ${styles.solid}`} d={f.d} vectorEffect="non-scaling-stroke" />
        </g>
      ))}
      {tubular.tube.map((t, i) => (
        <g key={i} transform={`translate(${t.drift[0]} ${t.drift[1]})`} data-g07="drift" data-dx={t.drift[0]} data-dy={t.drift[1]}>
          <path className={`${styles.part} ${styles.solid}`} d={t.d} fillRule="evenodd" vectorEffect="non-scaling-stroke" />
        </g>
      ))}

      <g className={styles.bondGlow} filter={`url(#${glow})`} data-g07="bond-glow">
        {tubular.bonds.map((b) => (
          <path key={b.id} d={b.d} vectorEffect="non-scaling-stroke" />
        ))}
      </g>
      <g className={styles.bond} data-g07="bond">
        {tubular.bonds.map((b) => (
          <path key={b.id} d={b.d} vectorEffect="non-scaling-stroke" />
        ))}
      </g>
    </svg>
  );
}

function KinetiqDrawing({ uid }: { uid: string }) {
  const clip = `${uid}-core`;
  const glow = `${uid}-glow`;
  const halo = `${uid}-halo`;
  return (
    <svg className={`${styles.layer} ${styles.drawing}`} viewBox={viewBox} focusable="false" aria-hidden="true">
      <defs>
        <clipPath id={clip} clipPathUnits="userSpaceOnUse">
          <path d={kinetiq.coreClip} />
        </clipPath>
        <filter id={glow} filterUnits="userSpaceOnUse" x={VB.x} y={VB.y} width={VB.w} height={VB.h}>
          <feGaussianBlur stdDeviation="0.55" />
        </filter>
        <filter id={halo} filterUnits="userSpaceOnUse" x={VB.x} y={VB.y} width={VB.w} height={VB.h}>
          <feGaussianBlur stdDeviation="2.4" />
        </filter>
      </defs>

      <Construction uid={uid} />
      <path className={styles.bore} d={kinetiq.bores} vectorEffect="non-scaling-stroke" />
      <path className={`${styles.hatch} ${styles.hatchQuiet}`} d={hatchBox} clipPath={`url(#${clip})`} vectorEffect="non-scaling-stroke" />

      {/* pre-blurred duplicates of the shell, and the skin lining the holes: they fade in once the stroke has drawn */}
      <g data-g07="shell-glow">
        <path className={styles.shellHalo} d={kinetiq.contour} filter={`url(#${halo})`} vectorEffect="non-scaling-stroke" />
        <path className={styles.shellGlow} d={kinetiq.contour} filter={`url(#${glow})`} vectorEffect="non-scaling-stroke" />
        <path className={styles.walls} d={kinetiq.walls} vectorEffect="non-scaling-stroke" />
      </g>
      {/* the one path, the unbroken outer skin: the page's only stroke-dashoffset animation */}
      <path className={styles.shell} d={kinetiq.shell} vectorEffect="non-scaling-stroke" data-g07="shell" />
    </svg>
  );
}

// ------------------------------------------------------------------ motion

let labelCount = 0;

type BuildOptions = {
  /** Where on the parent timeline the sequence starts. Default 0. */
  at?: number | string;
  /** Length of the whole sequence in the parent timeline's units. Default 1. */
  duration?: number;
};

/**
 * Adds G07's motion to a timeline (scrubbed by a pinned chapter, or played once). Final state is
 * the markup itself, so without a driver both drawings are complete.
 * - Tubular: the frame tubes drift about 6 px away from the faces and core; the two joints appear
 *   and their glow pulses once.
 * - KINETIQ: the shell draws itself in one unbroken stroke (DrawSVG on the single path), then its
 *   pre-blurred glow fades in.
 */
export function buildSectionTimeline(tl: gsap.core.Timeline, scope: Element | string, { at = 0, duration = 1 }: BuildOptions = {}) {
  const root = typeof scope === "string" ? document.querySelector(scope) : scope;
  if (!root) return tl;
  const q = gsap.utils.selector(root);
  const d = duration;
  const label = `g07-${++labelCount}`;
  tl.addLabel(label, at);

  q<SVGGElement>('[data-g07="drift"]').forEach((g) => {
    const dx = Number(g.dataset.dx ?? 0);
    const dy = Number(g.dataset.dy ?? 0);
    tl.fromTo(g, { x: 0, y: 0 }, { x: dx, y: dy, duration: 0.45 * d, ease: "power3.out" }, `${label}+=${0.05 * d}`);
  });
  const bonds = q('[data-g07="bond"]');
  const bondGlow = q('[data-g07="bond-glow"]');
  if (bonds.length) {
    tl.fromTo(bonds, { opacity: 0 }, { opacity: 1, duration: 0.2 * d, ease: "power2.out" }, `${label}+=${0.2 * d}`);
    tl.fromTo(bondGlow, { opacity: 0 }, { opacity: 1, duration: 0.15 * d, ease: "power2.out" }, `${label}+=${0.3 * d}`);
    tl.to(bondGlow, { opacity: 0.35, duration: 0.3 * d, ease: "power2.out" }, `${label}+=${0.45 * d}`);
  }

  const shells = q<SVGPathElement>('[data-g07="shell"]');
  shells.forEach((path) => {
    const host = path.closest("[data-g07-root]");
    const half = host ? host.getBoundingClientRect().width < HALF_BELOW : false;
    const glowGroup = host?.querySelector('[data-g07="shell-glow"]');
    const end = half ? kinetiq.halfFraction * 100 : 100;
    tl.fromTo(path, { drawSVG: "0% 0%" }, { drawSVG: `0% ${end}%`, duration: 0.8 * d, ease: "power2.inOut" }, label);
    if (half) tl.set(path, { drawSVG: "0% 100%" }, `${label}+=${0.8 * d}`);
    if (glowGroup) tl.fromTo(glowGroup, { opacity: 0 }, { opacity: 1, duration: 0.25 * d, ease: "power2.out" }, `${label}+=${0.72 * d}`);
  });
  return tl;
}

/** Plays the sequence once on entry (lab and standalone use). The landing page scrubs it instead. */
function usePlayOnce(root: RefObject<HTMLElement | null>, play: boolean) {
  const { motionOn } = useMotion();
  useGSAP(
    () => {
      if (!play || !motionOn || !root.current) return;
      const el = root.current;
      const mm = gsap.matchMedia();
      mm.add("(prefers-reduced-motion: no-preference)", () => {
        const tl = gsap.timeline({ scrollTrigger: { trigger: el, start: "top 75%", once: true } });
        buildSectionTimeline(tl, el, { duration: 1.6 });
      });
      return () => mm.revert();
    },
    { scope: root, dependencies: [motionOn, play], revertOnUpdate: true },
  );
}

// ------------------------------------------------------------------ components

type SectionProps = {
  className?: string;
  /** Show the title row above the drawing. Default true. */
  title?: boolean;
  /** Play the sequence once when scrolled into view. Leave false when a parent timeline drives it. */
  play?: boolean;
};

function Section({ variant, className, title = true, play = false }: SectionProps & { variant: Variant }) {
  const root = useRef<HTMLElement>(null);
  const uid = `g07${useId().replace(/[^a-zA-Z0-9]/g, "")}`;
  usePlayOnce(root, play);
  const isK = variant === "kinetiq";
  return (
    <figure
      ref={root}
      className={`${styles.root}${className ? ` ${className}` : ""}`}
      data-variant={variant}
      data-g07-root=""
    >
      <figcaption className={title ? styles.head : "visually-hidden"}>
        {title ? (
          <span className={styles.title}>
            <span className={styles.swatch} aria-hidden="true" />
            {isK ? right.title : left.title}
          </span>
        ) : null}
        <span className="visually-hidden">{isK ? `${right.title}. ${LABELS.kinetiqSummary} ${[...right.lines, right.core].map((l) => (/[.!?]$/.test(l) ? l : `${l}.`)).join(" ")}` : `${left.title}. ${LABELS.tubularSummary}`}</span>
      </figcaption>
      <div className={styles.frame} style={frameVars(variant)}>
        <div className={styles.canvas}>
          {isK ? <KinetiqDrawing uid={uid} /> : <TubularDrawing uid={uid} />}
          <Leaders set={isK ? KINETIQ : TUBULAR} />
          <Labels set={isK ? KINETIQ : TUBULAR} />
        </div>
      </div>
    </figure>
  );
}

/** G07 left: the tubular racket in section (frame tube, two faces, core, the tube's two joints). */
export function GluedSection(props: SectionProps) {
  return <Section variant="tubular" {...props} />;
}

/** G07 right: KINETIQ in section, one continuous shell. */
export function KinetiqSection(props: SectionProps) {
  return <Section variant="kinetiq" {...props} />;
}

/**
 * G07, Unibody chapter beat B: both sections at matching scale. The parent can place the two
 * drawings itself (GluedSection, KinetiqSection) and drive them with buildSectionTimeline.
 */
export function SectionComparison({ className, play = false, title = true }: SectionProps) {
  const root = useRef<HTMLDivElement>(null);
  usePlayOnce(root, play);
  return (
    <div ref={root} className={`${styles.pair}${className ? ` ${className}` : ""}`}>
      <GluedSection title={title} />
      <KinetiqSection title={title} />
    </div>
  );
}

export { DRIFT as SECTION_DRIFT_MM };
