// G02 vibration model (illustrative, not measured). Two damped responses after impact:
// a glued racket that rings, beats and decays slowly, and KINETIQ, which settles under 5%
// in a third of the time. Fans show the same response at different impact points.
import { VB, curvePath, n1, samplePoints, seeded } from "./graphics-plot";

/** Time window: a short lead-in before impact, then 0..1. */
export const T_MIN = -0.03;
export const T_MAX = 1;
/** Value range shown on the y axis (symmetric). */
export const V_MAX = 1;

const LN20 = Math.log(20);
/** Where each response falls under 5% of its starting envelope. */
export const SETTLE_GLUED = 0.97;
export const SETTLE_KINETIQ = SETTLE_GLUED / 3;
const TAU_G = SETTLE_GLUED / LN20;
const TAU_K = SETTLE_KINETIQ / LN20;
const F = 13; // ringing cycles across the window

export const X = (t: number) => ((t - T_MIN) / (T_MAX - T_MIN)) * VB;
export const Y = (v: number) => VB / 2 - (v / V_MAX) * (VB / 2);

type Var = { a: number; f: number; ph: number; tau: number; beat: number };
const BASE: Var = { a: 1, f: 1, ph: 0, tau: 1, beat: 1 };

function glued(p: Var) {
  return (t: number) => {
    if (t <= 0) return 0;
    const w = 2 * Math.PI * F * p.f * t;
    // Two close modes beat against each other: the echo of the joints.
    const ring = 0.8 * Math.sin(w + p.ph) + 0.2 * Math.sin(w * (1 + 0.085 * p.beat) + p.ph * 1.4);
    const env = Math.exp(-t / (TAU_G * p.tau)) * (1 - Math.exp(-t / 0.004));
    return 0.8 * p.a * env * ring;
  };
}

function kinetiq(p: Var) {
  return (t: number) => {
    if (t <= 0) return 0;
    const w = 2 * Math.PI * F * 1.06 * p.f * t;
    const env = Math.exp(-t / (TAU_K * p.tau)) * (1 - Math.exp(-t / 0.004));
    return 0.72 * p.a * env * Math.sin(w + p.ph);
  };
}

const LEAD = `M${n1(X(T_MIN))} ${n1(Y(0))}L${n1(X(0))} ${n1(Y(0))}`;
const seg = (cycles: number, perCycle = 4) => Math.ceil(cycles * perCycle);
const GLUED_SEGS = seg(F * 1.1);
// KINETIQ is visually flat (under a fifth of a pixel) well before the window ends.
const K_QUIET = 0.66;
const K_SEGS = seg(F * 1.1 * K_QUIET);

function gluedPath(p: Var) {
  const f = glued(p);
  return LEAD + curvePath(f, { t0: 0, t1: T_MAX, segments: GLUED_SEGS, x: X, y: Y }).replace(/^M[^C]+/, "");
}

function kinetiqPath(p: Var) {
  const f = kinetiq(p);
  return (
    LEAD + curvePath(f, { t0: 0, t1: T_MAX, segments: K_SEGS, x: X, y: Y, quietAfter: K_QUIET }).replace(/^M[^C]+/, "")
  );
}

/** Indices kept on phones (9 of each fan), spread evenly across the family. */
function phoneSet(count: number, keep = 9) {
  const s = new Set<number>();
  for (let i = 0; i < keep; i++) s.add(Math.round((i * (count - 1)) / (keep - 1)));
  return s;
}

export type FanLine = { d: string; r: number; phone: boolean };

function gluedFan(): FanLine[] {
  const rnd = seeded(20261021);
  const n = 13;
  const keep = phoneSet(n);
  return Array.from({ length: n }, (_, i) => {
    const u = i / (n - 1) - 0.5; // edge (-0.5) to edge (+0.5) through centre
    const p: Var = {
      a: 1 + u * 0.46 + (rnd() - 0.5) * 0.06,
      f: 1 + u * 0.075 + (rnd() - 0.5) * 0.02,
      ph: (rnd() - 0.5) * 1.1,
      tau: 1 + (rnd() - 0.5) * 0.34,
      beat: 0.7 + rnd() * 0.8,
    };
    return { d: gluedPath(p), r: p.a, phone: keep.has(i) };
  });
}

function kinetiqFan(): FanLine[] {
  const rnd = seeded(4271);
  const n = 21;
  const keep = phoneSet(n);
  return Array.from({ length: n }, (_, i) => {
    const u = i / (n - 1) - 0.5;
    const p: Var = {
      a: 1 + u * 0.15 + (rnd() - 0.5) * 0.02,
      f: 1 + (rnd() - 0.5) * 0.014,
      ph: (rnd() - 0.5) * 0.08,
      tau: 1 + (rnd() - 0.5) * 0.08,
      beat: 1,
    };
    return { d: kinetiqPath(p), r: p.a, phone: keep.has(i) };
  });
}

export const vibration = {
  glued: gluedPath(BASE),
  kinetiq: kinetiqPath(BASE),
  gluedFan: gluedFan(),
  kinetiqFan: kinetiqFan(),
  /** Points along the KINETIQ line (viewBox units) for the travelling glow head. */
  head: samplePoints(kinetiq(BASE), T_MIN, T_MAX, 720, X, Y),
  settleX: X(SETTLE_KINETIQ),
  settleY: Y(kinetiq(BASE)(SETTLE_KINETIQ)),
  zeroY: Y(0),
  /** Time ticks along the bottom rule: every 5% of the window, major every 25%. */
  ticks: Array.from({ length: 21 }, (_, i) => ({ x: X(i / 20), major: i % 5 === 0 })),
  /** Eight full-width rules, symmetric about the rest line. */
  rules: [-1, -0.75, -0.5, -0.25, 0.25, 0.5, 0.75, 1].map((v) => Y(v)),
};

/** Envelope as a share of the glued racket's starting vibration, for the table fallback. */
export function envelopeTable(steps = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]) {
  return steps.map((t) => ({
    t,
    glued: Math.round(Math.exp(-t / TAU_G) * 100),
    kinetiq: Math.round(0.9 * Math.exp(-t / TAU_K) * 100),
  }));
}
