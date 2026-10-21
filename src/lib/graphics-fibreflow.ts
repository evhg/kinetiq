// G05 fibre flow field: streamlines of potential flow around the 42 real holes of the racket face.
// Uniform flow plus one doublet per hole (racket-shape.ts HOLES, HOLE_RADIUS), integrated with RK4
// along the normalised velocity so every line keeps its spacing far from the holes, parts around each
// bore and rejoins behind it. Pure and deterministic: the same inputs give the same lines everywhere.
// World units are racket units (1 = 10 cm, y up); output is in CSS pixels of the target box (y down).

import { HOLES, HOLE_RADIUS, type Pt } from "./racket-shape";

/** A world rectangle: x0, y0, x1, y1 (racket units, y up). */
export type Rect = [number, number, number, number];

/** Named framings of the hole field. */
export const FRAMES = {
  /** All 42 holes with a little air around them. */
  field: [-0.97, -0.56, 0.97, 1.4] as Rect,
  /** The centre of the face: three rows either side of the sweet spot. */
  centre: [-0.62, -0.08, 0.62, 0.92] as Rect,
  /**
   * The phone strip: three whole rows (6, 7, 6 holes) centred on the sweet-spot row, with the edges
   * falling between rows so no bore is cut in half by the top or bottom fade.
   */
  strip: [-0.57, -0.08, 0.57, 0.68] as Rect,
} as const;

export type FrameName = keyof typeof FRAMES;

export type FlowOptions = {
  /** Box size in CSS px. */
  width: number;
  height: number;
  /** Flow direction in degrees: 0 runs along +x, positive turns towards +y (up the face). */
  angle?: number;
  /** World rectangle to place in the box. */
  frame?: Rect;
  /** "contain" fits the frame inside fitW x fitH of the box; "cover" fills the box with it. */
  fit?: "contain" | "cover";
  fitW?: number;
  fitH?: number;
  /** Where the frame centre sits, as fractions of the box. */
  focus?: [number, number];
  /** Distance between neighbouring filaments, CSS px. */
  spacing?: number;
  /** Filaments per tow; tows are separated by a one-filament gap. */
  tow?: number;
  /** Upper bound on the number of lines. */
  maxLines?: number;
  /** Largest integration step in px (near holes the step shrinks automatically). */
  maxStep?: number;
  seed?: number;
};

export type FlowLine = {
  /** Interleaved x, y in CSS px. */
  pts: Float32Array;
  /** Cumulative arc length at every point, px. */
  len: Float32Array;
  /** Local flow speed at every point, relative to the free stream (1 far from holes, up to 2 at a bore's shoulder). */
  speed: Float32Array;
  /** Base opacity 0..1 (tow shading and a little per-filament variation). */
  alpha: number;
  /** One of the few hot filaments. */
  hot: boolean;
};

export type FlowField = {
  width: number;
  height: number;
  /** px per world unit. */
  scale: number;
  /** Hole centres in px, interleaved, and the hole radius in px. */
  holes: Float32Array;
  holeR: number;
  /** The framed world rect in px: x0, y0, x1, y1 (y down). */
  frameBox: [number, number, number, number];
  lines: FlowLine[];
};

/** mulberry32: a tiny seeded PRNG. */
export function prng(seed: number) {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const A2 = HOLE_RADIUS * HOLE_RADIUS;
const HX = new Float64Array(HOLES.map((h: Pt) => h[0]));
const HY = new Float64Array(HOLES.map((h: Pt) => h[1]));
const NH = HOLES.length;
/** Doublet window: full strength inside R1, zero beyond R2 (the nearest neighbour bore is 0.208 away). */
const R1 = HOLE_RADIUS * 1.45;
const R2 = 0.2;

/**
 * Builds the field lazily: `step()` integrates one line and returns false when every line is done,
 * so a caller can spread the work over idle slices instead of one long task.
 */
export function createFlowBuilder(opts: FlowOptions) {
  const {
    width: W,
    height: H,
    angle = 0,
    frame = FRAMES.field,
    fit = "contain",
    fitW = 1,
    fitH = 1,
    focus = [0.5, 0.5],
    spacing = 1.6,
    tow = 7,
    maxLines = 900,
    maxStep = 6,
    seed = 42,
  } = opts;

  // World -> px transform: uniform scale, y flipped.
  const fw = frame[2] - frame[0];
  const fh = frame[3] - frame[1];
  const sx = (W * fitW) / fw;
  const sy = (H * fitH) / fh;
  const scale = fit === "cover" ? Math.max(W / fw, H / fh) : Math.min(sx, sy);
  const fcx = (frame[0] + frame[2]) / 2;
  const fcy = (frame[1] + frame[3]) / 2;
  const ox = focus[0] * W - fcx * scale; // px = ox + x * scale
  const oy = focus[1] * H + fcy * scale; // py = oy - y * scale
  const toWx = (px: number) => (px - ox) / scale;
  const toWy = (py: number) => (oy - py) / scale;

  const rad = (angle * Math.PI) / 180;
  const c = Math.cos(rad);
  const s = Math.sin(rad);

  // Stream function: free stream plus one doublet per hole, each windowed to zero before it can
  // reach a neighbouring bore (R2 < pitch - radius). So every bore is an exact streamline, lines are
  // level sets of psi (they can never cross or merge), and far from the holes they run dead straight.
  // psi = -x sin a + y cos a + sum a^2 (dx sin a - dy cos a) / r^2 * W(r)
  // Velocity is the rotated gradient (d psi/dy, -d psi/dx). Writes psi, u, v and the distance to the
  // nearest bore surface into `out` (only holes within R2 are visited, so most points cost nothing).
  const out = new Float64Array(4);
  const vel = (x: number, y: number) => {
    let psi = -x * s + y * c;
    let gx = -s;
    let gy = c;
    let near = Infinity;
    for (let k = 0; k < NH; k++) {
      const dx = x - HX[k];
      const dy = y - HY[k];
      const r2 = dx * dx + dy * dy;
      if (r2 < near) near = r2;
      if (r2 >= R2 * R2) continue;
      const r = Math.sqrt(r2);
      const g = s * dx - c * dy;
      const P = g / r2;
      const r4 = r2 * r2;
      const px = s / r2 - (2 * dx * g) / r4;
      const py = -c / r2 - (2 * dy * g) / r4;
      let w = 1;
      let dw = 0;
      if (r > R1) {
        const t = (r - R1) / (R2 - R1);
        w = 1 - t * t * t * (t * (6 * t - 15) + 10);
        dw = (-30 * t * t * (1 - t) * (1 - t)) / (R2 - R1);
      }
      psi += A2 * P * w;
      gx += A2 * (w * px + (P * dw * dx) / r);
      gy += A2 * (w * py + (P * dw * dy) / r);
    }
    out[0] = gy;
    out[1] = -gx;
    out[2] = Math.sqrt(near) - HOLE_RADIUS;
    out[3] = psi;
  };

  // Flow-aligned extent of the box (u along the flow, v across it), in world units.
  const corners: Pt[] = [
    [toWx(0), toWy(0)],
    [toWx(W), toWy(0)],
    [toWx(0), toWy(H)],
    [toWx(W), toWy(H)],
  ];
  let umin = Infinity;
  let umax = -Infinity;
  let vmin = Infinity;
  let vmax = -Infinity;
  for (const [x, y] of corners) {
    const u = x * c + y * s;
    const v = -x * s + y * c;
    umin = Math.min(umin, u);
    umax = Math.max(umax, u);
    vmin = Math.min(vmin, v);
    vmax = Math.max(vmax, v);
  }
  // Seed far enough upstream that the field has not yet bent the lines.
  let holeUmin = Infinity;
  for (let k = 0; k < NH; k++) holeUmin = Math.min(holeUmin, HX[k] * c + HY[k] * s);
  const uSeed = Math.min(umin, holeUmin - 0.45) - 0.02;
  const margin = 12 / scale; // keep drawing a little past the box edge

  // Seeds: tows of `tow` filaments, a one-filament gap between tows.
  const sp = spacing / scale;
  const seeds: { v: number; f: number }[] = [];
  const pitch = (tow + 1) * sp;
  const span = vmax - vmin + 2 * margin;
  let total = Math.floor(span / sp);
  if (total > maxLines) total = maxLines;
  const realPitch = span / Math.max(1, Math.floor(total / (tow + 1)));
  const towCount = Math.max(1, Math.round(span / (realPitch || pitch)));
  const step = realPitch / (tow + 1);
  for (let t = 0; t < towCount; t++) {
    for (let j = 0; j < tow; j++) {
      seeds.push({ v: vmin - margin + t * realPitch + (j + 1) * step, f: tow > 1 ? j / (tow - 1) : 0.5 });
    }
  }

  const rnd = prng(seed);
  const lines: FlowLine[] = [];
  let i = 0;
  const box = { x0: -margin * scale, y0: -margin * scale, x1: W + margin * scale, y1: H + margin * scale };
  const minStep = 0.6 / scale;
  const bigStep = Math.max(maxStep, 24) / scale; // outside the box nothing is drawn
  const hStep = maxStep / scale;

  const dir = (x: number, y: number, o: Float64Array) => {
    vel(x, y);
    const m = Math.hypot(out[0], out[1]) || 1e-9;
    o[0] = out[0] / m;
    o[1] = out[1] / m;
    o[2] = m;
    return out[2];
  };
  const k1 = new Float64Array(3);
  const k2 = new Float64Array(3);
  const k3 = new Float64Array(3);
  const k4 = new Float64Array(3);

  function integrate(v0: number) {
    let x = uSeed * c - v0 * s;
    let y = uSeed * s + v0 * c;
    vel(x, y);
    const psi0 = out[3];
    const xs: number[] = [];
    const sp2: number[] = [];
    let entered = false;
    for (let n = 0; n < 6000; n++) {
      const surf = dir(x, y, k1);
      const px = ox + x * scale;
      const py = oy - y * scale;
      const inside = px >= box.x0 && px <= box.x1 && py >= box.y0 && py <= box.y1;
      if (inside) {
        entered = true;
        xs.push(px, py);
        sp2.push(k1[2]);
      } else if (entered) {
        break;
      }
      const u = x * c + y * s;
      if (u > umax + margin * 2) break;
      // Step: small near a bore, larger in the free stream, large outside the drawn box.
      const h = inside ? Math.min(hStep, Math.max(minStep, surf * 0.3)) : Math.min(bigStep, Math.max(minStep, surf * 0.3));
      dir(x + (h / 2) * k1[0], y + (h / 2) * k1[1], k2);
      dir(x + (h / 2) * k2[0], y + (h / 2) * k2[1], k3);
      dir(x + h * k3[0], y + h * k3[1], k4);
      x += (h / 6) * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0]);
      y += (h / 6) * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1]);
      // Pull the point back onto its own level set (RK4 drifts a little where lines turn hard).
      vel(x, y);
      const g2 = out[0] * out[0] + out[1] * out[1];
      if (g2 > 1e-4) {
        const e = (out[3] - psi0) / g2;
        // grad psi = (-v, u)
        x -= e * -out[1];
        y -= e * out[0];
      }
    }
    // Drop points that add nothing (straight runs in the free stream): within 0.12 px of the chord.
    const keep = simplifyIndices(xs, 0.12);
    const nPts = keep.length;
    const pts = new Float32Array(nPts * 2);
    const speed = new Float32Array(nPts);
    keep.forEach((k, j) => {
      pts[2 * j] = xs[2 * k];
      pts[2 * j + 1] = xs[2 * k + 1];
      speed[j] = sp2[k];
    });
    const len = new Float32Array(nPts);
    for (let p = 1; p < nPts; p++) {
      len[p] = len[p - 1] + Math.hypot(pts[2 * p] - pts[2 * p - 2], pts[2 * p + 1] - pts[2 * p - 1]);
    }
    return { pts, len, speed };
  }

  const holes = new Float32Array(NH * 2);
  for (let k = 0; k < NH; k++) {
    holes[2 * k] = ox + HX[k] * scale;
    holes[2 * k + 1] = oy - HY[k] * scale;
  }

  const frameBox: FlowField["frameBox"] = [ox + frame[0] * scale, oy - frame[3] * scale, ox + frame[2] * scale, oy - frame[1] * scale];
  const field: FlowField = { width: W, height: H, scale, holes, holeR: HOLE_RADIUS * scale, frameBox, lines };

  return {
    field,
    total: seeds.length,
    /** Integrates the next line. Returns false once every line is done. */
    step(): boolean {
      if (i >= seeds.length) return false;
      const sd = seeds[i++];
      const { pts, len, speed } = integrate(sd.v);
      // Tow shading: filaments at the centre of a tow catch more light than those at its edges,
      // and broad bands of tows catch more than others (grazing light across a weave).
      const shade = 0.3 + 0.7 * Math.sin(Math.PI * (0.1 + 0.8 * sd.f));
      const vp = sd.v * scale;
      const band = 0.3 + 0.7 * (0.5 + 0.3 * Math.sin(vp / 61 + 1.3) + 0.2 * Math.sin(vp / 23.7 + 4.1));
      const jitter = (0.8 + 0.4 * rnd()) * band;
      const hot = rnd() < 0.022;
      if (pts.length >= 4) lines.push({ pts, len, speed, alpha: Math.min(1, shade * jitter), hot });
      return i < seeds.length;
    },
  };
}

/** Builds the whole field in one go (for tests and the server fallback). */
export function buildFlowField(opts: FlowOptions): FlowField {
  const b = createFlowBuilder(opts);
  while (b.step()) {
    /* keep going */
  }
  return b.field;
}

/** Douglas-Peucker on an interleaved polyline: the indices of the points to keep. */
export function simplifyIndices(pts: ArrayLike<number>, tol: number): number[] {
  const n = pts.length / 2;
  if (n < 3) return Array.from({ length: n }, (_, k) => k);
  const keep = new Uint8Array(n);
  keep[0] = 1;
  keep[n - 1] = 1;
  const stack: [number, number][] = [[0, n - 1]];
  const t2 = tol * tol;
  while (stack.length) {
    const [a, b] = stack.pop()!;
    const ax = pts[2 * a];
    const ay = pts[2 * a + 1];
    const bx = pts[2 * b];
    const by = pts[2 * b + 1];
    const dx = bx - ax;
    const dy = by - ay;
    const L2 = dx * dx + dy * dy || 1e-9;
    let worst = -1;
    let wd = 0;
    for (let p = a + 1; p < b; p++) {
      const px = pts[2 * p] - ax;
      const py = pts[2 * p + 1] - ay;
      const cr = px * dy - py * dx;
      const d2 = (cr * cr) / L2;
      if (d2 > wd) {
        wd = d2;
        worst = p;
      }
    }
    if (worst > 0 && wd > t2) {
      keep[worst] = 1;
      stack.push([a, worst], [worst, b]);
    }
  }
  const idx: number[] = [];
  for (let p = 0; p < n; p++) if (keep[p]) idx.push(p);
  return idx;
}

/** Douglas-Peucker simplification of an interleaved polyline, for compact SVG output. */
export function simplify(pts: Float32Array, tol: number): number[] {
  const out: number[] = [];
  for (const p of simplifyIndices(pts, tol)) out.push(pts[2 * p], pts[2 * p + 1]);
  return out;
}

/** SVG path data for a set of lines (simplified, rounded to 0.1 px). */
export function linesToPath(lines: FlowLine[], tol = 0.5): string {
  const r = (v: number) => Math.round(v * 10) / 10;
  return lines
    .map((l) => {
      const p = simplify(l.pts, tol);
      let d = `M${r(p[0])} ${r(p[1])}`;
      for (let k = 2; k < p.length; k += 2) d += `L${r(p[k])} ${r(p[k + 1])}`;
      return d;
    })
    .join("");
}
