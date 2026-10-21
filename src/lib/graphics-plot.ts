// Pure plotting helpers shared by the data graphics (G02 vibration, G03 tolerance, G04 spikes).
// Every graphic draws in a normalised 1000 x 1000 viewBox with preserveAspectRatio="none" and
// non-scaling strokes, so one set of path strings serves every viewport and labels can sit as
// HTML at percentage positions. Output is deterministic: server and client render the same path.

export const VB = 1000;

/** A tiny seeded PRNG (mulberry32): same seed, same sequence, on every machine. */
export function seeded(seed: number) {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/** Round to one decimal and drop a trailing ".0" to keep path strings short. */
export function n1(v: number) {
  const r = Math.round(v * 10) / 10;
  return Object.is(r, -0) ? "0" : String(r);
}

type Fn = (t: number) => number;

type CurveOptions = {
  /** Domain start and end. */
  t0: number;
  t1: number;
  /** Number of cubic segments between t0 and t1. */
  segments: number;
  /** Map domain to viewBox x (0..1000). */
  x: (t: number) => number;
  /** Map value to viewBox y (0..1000, y down). */
  y: (v: number) => number;
  /** From this t onwards the curve is drawn as a straight line to t1 (it has gone quiet). */
  quietAfter?: number;
};

/**
 * A smooth function as a chain of cubic Beziers (cubic Hermite with numerical derivatives).
 * Four to six segments per oscillation are enough for a sine to be visually exact.
 */
export function curvePath(f: Fn, o: CurveOptions): string {
  const end = o.quietAfter !== undefined ? Math.min(o.quietAfter, o.t1) : o.t1;
  const h = (end - o.t0) / o.segments;
  const eps = Math.max(1e-6, h * 1e-3);
  const d = (t: number) => (f(t + eps) - f(t - eps)) / (2 * eps);
  let s = `M${n1(o.x(o.t0))} ${n1(o.y(f(o.t0)))}`;
  for (let i = 0; i < o.segments; i++) {
    const a = o.t0 + i * h;
    const b = a + h;
    const fa = f(a);
    const fb = f(b);
    const c1 = fa + (d(a) * h) / 3;
    const c2 = fb - (d(b) * h) / 3;
    s += `C${n1(o.x(a + h / 3))} ${n1(o.y(c1))} ${n1(o.x(b - h / 3))} ${n1(o.y(c2))} ${n1(o.x(b))} ${n1(o.y(fb))}`;
  }
  if (end < o.t1) s += `L${n1(o.x(o.t1))} ${n1(o.y(f(o.t1)))}`;
  return s;
}

/** A Catmull-Rom spline through points (already in viewBox units), as cubic Beziers. */
export function splinePath(pts: [number, number][], tension = 1): string {
  if (pts.length < 2) return "";
  let s = `M${n1(pts[0][0])} ${n1(pts[0][1])}`;
  for (let i = 0; i < pts.length - 1; i++) {
    const p0 = pts[Math.max(0, i - 1)];
    const p1 = pts[i];
    const p2 = pts[i + 1];
    const p3 = pts[Math.min(pts.length - 1, i + 2)];
    const k = tension / 6;
    const c1x = p1[0] + (p2[0] - p0[0]) * k;
    const c1y = p1[1] + (p2[1] - p0[1]) * k;
    const c2x = p2[0] - (p3[0] - p1[0]) * k;
    const c2y = p2[1] - (p3[1] - p1[1]) * k;
    s += `C${n1(c1x)} ${n1(c1y)} ${n1(c2x)} ${n1(c2y)} ${n1(p2[0])} ${n1(p2[1])}`;
  }
  return s;
}

/** Evenly sampled points of a function in viewBox units, for a glow head to ride. */
export function samplePoints(
  f: Fn,
  t0: number,
  t1: number,
  count: number,
  x: (t: number) => number,
  y: (v: number) => number,
) {
  const out: [number, number][] = [];
  for (let i = 0; i <= count; i++) {
    const t = t0 + ((t1 - t0) * i) / count;
    out.push([x(t), y(f(t))]);
  }
  return out;
}

/** y at a given x on a polyline sampled in increasing x (linear interpolation). */
export function yAt(pts: [number, number][], x: number) {
  if (x <= pts[0][0]) return pts[0][1];
  const last = pts[pts.length - 1];
  if (x >= last[0]) return last[1];
  let lo = 0;
  let hi = pts.length - 1;
  while (hi - lo > 1) {
    const mid = (lo + hi) >> 1;
    if (pts[mid][0] <= x) lo = mid;
    else hi = mid;
  }
  const [x0, y0] = pts[lo];
  const [x1, y1] = pts[hi];
  return y0 + ((y1 - y0) * (x - x0)) / (x1 - x0 || 1);
}

/** Percent string for inline positioning of HTML labels over a viewBox coordinate. */
export function pct(v: number) {
  return `${Math.round((v / VB) * 10000) / 100}%`;
}
