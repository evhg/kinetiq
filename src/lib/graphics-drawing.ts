// Pure geometry for the G01 technical drawing, G10c ghost contour and G11 glyphs.
// Everything is generated from racket-shape.ts. Drawing units are millimetres with
// y up (1 racket unit = 100 mm); a Xf maps them onto a sheet (SVG user units, y down).

import {
  CAP,
  CROWN_RADIUS,
  EDGE_RADIUS,
  FACE_INSET,
  GRIP,
  HANDLE,
  HEAD_CURVES,
  HEAD_START,
  HEAD_WIDTH,
  HOLES,
  HOLE_RADIUS,
  NECK,
  NECK_TAPER,
  THICKNESS,
  THROAT_CURVES,
  THROAT_START,
  type Pt,
} from "@/lib/racket-shape";

export type V = [number, number];
/** Sheet transform: sheet = (ox + x * s, oy - y * s). */
export type Xf = { ox: number; oy: number; s: number };

const MM = 100;
const CROWN = HOLES.filter((h) => h[2] === CROWN_RADIUS).length;
export const DIM = {
  length: Math.round((HEAD_START[1] - (HANDLE.top - HANDLE.length)) * MM), // 455
  width: Math.round(HEAD_WIDTH * MM * 10) / 10, // 260.0
  thickness: THICKNESS * MM, // 38
  holeD: HOLE_RADIUS * 2 * MM, // 12.4, the grid
  crownD: CROWN_RADIUS * 2 * MM, // 14.0, the crown along the top
  holes: HOLES.length, // 42
  crown: CROWN, // 8
  grid: HOLES.length - CROWN, // 34
  headTop: HEAD_START[1] * MM, // 155
  buttY: (HANDLE.top - HANDLE.length) * MM, // -300
  handleR: HANDLE.radius * MM, // 16.5, the carbon core under the grip
  edgeR: EDGE_RADIUS * MM, // 1.5
  faceInset: FACE_INSET * MM, // 4
  shell: 2, // drawn shell wall in sections (mm)
  rimShell: 3,
  /** Balance point from the butt (mm): the 250.0 nominal (the sample card measures 250.04). Drawn as a symbol only, never printed. */
  balance: 250,
};

/** The canonical handle in drawing mm (racket-shape.ts NECK, NECK_TAPER, GRIP, CAP). */
export const HANDLE_MM = {
  neckTop: NECK.top * MM, // -146
  neckEnd: NECK.end * MM, // -176
  taperTop: NECK_TAPER.top * MM, // -150
  core: { x: NECK.halfEnd * MM, z: (NECK_TAPER.thickness / 2) * MM }, // 16.5 x 14.5
  grip: {
    top: GRIP.top * MM, // -174
    bottom: GRIP.bottom * MM, // -284.2
    band: GRIP.band * MM, // 11
    pitch: GRIP.pitch * MM, // 27
    x: (NECK.halfEnd + GRIP.tape) * MM, // 17.0
    z: (NECK_TAPER.thickness / 2 + GRIP.tape) * MM, // 15.0
  },
  cap: { top: CAP.top * MM, groove: CAP.groove * MM, mark: CAP.mark * MM },
};

const n = (v: number) => (Math.abs(v) < 0.005 ? "0" : String(Number(v.toFixed(2))));
export const mm = (p: Pt): V => [p[0] * MM, p[1] * MM];
export const at = (t: Xf, [x, y]: V): V => [t.ox + x * t.s, t.oy - y * t.s];

/** Tiny path builder in drawing mm (y up), emitting sheet coordinates. */
export class PathB {
  private parts: string[] = [];
  constructor(private t: Xf) {}
  private p(v: V) {
    const [x, y] = at(this.t, v);
    return `${n(x)} ${n(y)}`;
  }
  M(x: number, y: number) {
    this.parts.push(`M${this.p([x, y])}`);
    return this;
  }
  L(x: number, y: number) {
    this.parts.push(`L${this.p([x, y])}`);
    return this;
  }
  C(x1: number, y1: number, x2: number, y2: number, x: number, y: number) {
    this.parts.push(`C${this.p([x1, y1])} ${this.p([x2, y2])} ${this.p([x, y])}`);
    return this;
  }
  Q(x1: number, y1: number, x: number, y: number) {
    this.parts.push(`Q${this.p([x1, y1])} ${this.p([x, y])}`);
    return this;
  }
  Z() {
    this.parts.push("Z");
    return this;
  }
  get d() {
    return this.parts.join(" ");
  }
}

export function circle(t: Xf, [cx, cy]: V, r: number): string {
  const [x, y] = at(t, [cx, cy]);
  const R = r * t.s;
  return `M${n(x - R)} ${n(y)}a${n(R)} ${n(R)} 0 1 0 ${n(2 * R)} 0a${n(R)} ${n(R)} 0 1 0 ${n(-2 * R)} 0Z`;
}

/** Rounded rectangle in drawing mm with per-corner radii [tl, tr, br, bl] (y up: top = y1). */
export function roundRect(t: Xf, x0: number, y0: number, x1: number, y1: number, r: [number, number, number, number]): string {
  const [tl, tr, br, bl] = r;
  const b = new PathB(t)
    .M(x0 + tl, y1)
    .L(x1 - tr, y1)
    .Q(x1, y1, x1, y1 - tr)
    .L(x1, y0 + br)
    .Q(x1, y0, x1 - br, y0)
    .L(x0 + bl, y0)
    .Q(x0, y0, x0, y0 + bl)
    .L(x0, y1 - tl)
    .Q(x0, y1, x0 + tl, y1)
    .Z();
  return b.d;
}

export const cubicPts = (start: Pt, curves: [Pt, Pt, Pt][], steps = 48): V[] => {
  const out: V[] = [];
  let p0 = start;
  for (const [c1, c2, e] of curves) {
    for (let i = 1; i <= steps; i++) {
      const t = i / steps;
      const u = 1 - t;
      out.push([
        (u * u * u * p0[0] + 3 * u * u * t * c1[0] + 3 * u * t * t * c2[0] + t * t * t * e[0]) * MM,
        (u * u * u * p0[1] + 3 * u * u * t * c1[1] + 3 * u * t * t * c2[1] + t * t * t * e[1]) * MM,
      ]);
    }
    p0 = e;
  }
  return out;
};

const HEAD_PTS = cubicPts(HEAD_START, HEAD_CURVES, 64);

/** Half-width of the head outline at height y (mm), right side. */
export function headHalfWidth(y: number): number {
  let best = 0;
  for (let i = 1; i < HEAD_PTS.length; i++) {
    const [ax, ay] = HEAD_PTS[i - 1];
    const [bx, by] = HEAD_PTS[i];
    if (ax < 0 || bx < 0) continue;
    if ((ay - y) * (by - y) <= 0 && ay !== by) {
      const k = (y - ay) / (by - ay);
      best = Math.max(best, ax + (bx - ax) * k);
    }
  }
  return best;
}

/** Hole rows, top to bottom: y, sorted x positions and the row's hole radius (mm). */
export const HOLE_ROWS: { y: number; xs: number[]; r: number }[] = (() => {
  const m = new Map<number, { xs: number[]; r: number }>();
  for (const [x, y, r] of HOLES) {
    const k = Math.round(y * MM * 10) / 10;
    const row = m.get(k) ?? { xs: [], r: r * MM };
    row.xs.push(Math.round(x * MM * 10) / 10);
    m.set(k, row);
  }
  return [...m.entries()].sort((a, b) => b[0] - a[0]).map(([y, row]) => ({ y, xs: row.xs.sort((a, b) => a - b), r: row.r }));
})();

export const HOLES_MM: V[] = HOLES.map(([x, y]) => mm([x, y]));
/** Each hole's radius (mm), in HOLES order: 7.0 for the crown, 6.2 for the grid. */
export const HOLE_R_MM: number[] = HOLES.map(([, , r]) => r * MM);

/** Widest point of the head (the 260.0 dimension). */
export const HEAD_MAX: V = cubicPts(HEAD_START, HEAD_CURVES, 2000).reduce((a, p) => (p[0] > a[0] ? p : a), [0, 0] as V);

/** Top of the throat (mm): the highest point of its upper edge. */
const THROAT_TOP = Math.max(...cubicPts(THROAT_START, THROAT_CURVES, 64).map((p) => p[1]));

/**
 * Section plane A-A: below the hole field and above the throat, the one band where a cut across the head
 * meets no hole (the crown and the lattice leave no other), so the section shows one unbroken shell around
 * one unbroken core.
 */
export const CUT_Y = (() => {
  const lowest = Math.min(...HOLES.map(([, y, r]) => (y - r) * MM));
  return Math.round(((lowest + THROAT_TOP) / 2) * 10) / 10;
})();
export const HEAD_W = headHalfWidth(CUT_Y);

/** Section plane B-B: through the top row of the lattice (its three holes and nothing else), for the bore detail. */
export const BORE_ROW = HOLE_ROWS.find((r) => r.r === HOLE_RADIUS * MM)!;
export const BORE: V = [BORE_ROW.xs[0], BORE_ROW.y];

/* ---------- the canonical handle ---------- */

const smooth = (t: number) => {
  const k = Math.min(1, Math.max(0, t));
  return k * k * (3 - 2 * k);
};

/** Neck half width before the fillet (mm): 23.5 at NECK.top to 16.5 at NECK.end (smoothstep), then the core. */
function neckHalf(y: number): number {
  const { neckTop, neckEnd, core } = HANDLE_MM;
  if (y > neckTop) return -Infinity;
  return NECK.halfTop * MM + (core.x - NECK.halfTop * MM) * smooth((neckTop - y) / (neckTop - neckEnd));
}

/**
 * Right half width of the head and neck from the throat foot down to the grip (mm), as kq_canon builds it:
 * the head outline united with the neck, closed by the 18 mm concave fillet (a morphological closing,
 * exact for a shape symmetric about x = 0). Sampled every 0.25 mm; `from` is where it leaves the head curve.
 */
const NECK_PROFILE = (() => {
  const r = NECK.fillet * MM;
  const step = 0.25;
  const y0 = -100;
  const y1 = HANDLE_MM.grip.top;
  const ys: number[] = [];
  for (let y = y0 + 2 * r; y >= y1 - 2 * r; y -= step) ys.push(Math.round(y * 100) / 100);
  const w = ys.map((y) => Math.max(y >= -155 ? headHalfWidth(y) : -Infinity, neckHalf(y)));
  const k = Math.round(r / step);
  const disc = Array.from({ length: 2 * k + 1 }, (_, j) => Math.sqrt(Math.max(0, r * r - ((j - k) * step) ** 2)));
  const dil = ys.map((_, i) => {
    let m = -Infinity;
    for (let j = -k; j <= k; j++) if (w[i + j] !== undefined) m = Math.max(m, w[i + j] + disc[j + k]);
    return m;
  });
  const close = ys.map((_, i) => {
    let m = Infinity;
    for (let j = -k; j <= k; j++) if (dil[i + j] !== undefined) m = Math.min(m, dil[i + j] - disc[j + k]);
    return m;
  });
  const pts: V[] = [];
  let from = y0;
  for (let i = 0; i < ys.length; i++) {
    const y = ys[i];
    if (y > y0 || y < y1) continue;
    if (y >= -155 && close[i] - headHalfWidth(y) < 0.02 && pts.length === 0) {
      from = y;
      continue;
    }
    pts.push([close[i], y]);
  }
  return { from, pts };
})();

/** Split a cubic at t: the first part. */
function cubicHead(p0: Pt, [c1, c2, e]: [Pt, Pt, Pt], t: number): [Pt, Pt, Pt] {
  const L = (a: Pt, b: Pt): Pt => [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t];
  const a = L(p0, c1);
  const b = L(c1, c2);
  const c = L(c2, e);
  const d = L(a, b);
  const f = L(b, c);
  return [a, d, L(d, f)];
}

/** Parameter on a cubic (monotone in y) where y = target, by bisection. */
function cubicAtY(p0: Pt, [c1, c2, e]: [Pt, Pt, Pt], target: number): number {
  const y = (t: number) => {
    const u = 1 - t;
    return u * u * u * p0[1] + 3 * u * u * t * c1[1] + 3 * u * t * t * c2[1] + t * t * t * e[1];
  };
  let lo = 0;
  let hi = 1;
  const down = y(1) < y(0);
  for (let i = 0; i < 50; i++) {
    const m = (lo + hi) / 2;
    if (y(m) > target === down) lo = m;
    else hi = m;
  }
  return (lo + hi) / 2;
}

/** Catmull-Rom through points (n per segment), as a polyline. */
function catmull(P: V[], n = 4): V[] {
  const out: V[] = [];
  for (let i = 0; i < P.length - 1; i++) {
    const p0 = P[Math.max(i - 1, 0)];
    const p1 = P[i];
    const p2 = P[i + 1];
    const p3 = P[Math.min(i + 2, P.length - 1)];
    for (let k = 0; k < n; k++) {
      const t = k / n;
      const t2 = t * t;
      const t3 = t2 * t;
      const f = (j: 0 | 1) =>
        0.5 * (2 * p1[j] + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2 + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3);
      out.push([f(0), f(1)]);
    }
  }
  out.push(P[P.length - 1]);
  return out;
}

/**
 * The cap's right half outline below the grip (mm): K05's flared cap, about 1.5 mm proud of the grip, with its
 * fine groove, ending in a rounded end at the butt. `half` is the grip's half width in this view.
 */
function capOutline(half: number): V[] {
  const prof = catmull(CAP.profile.map(([s, y]) => [s * half, y * MM] as V), 3);
  // the cap shows below the point where it stands proud of the grip
  const i = prof.findIndex(([x]) => x >= half);
  const a = prof[i - 1];
  const b = prof[i];
  const k = (half - a[0]) / (b[0] - a[0]);
  return [[half, a[1] + (b[1] - a[1]) * k], ...prof.slice(i)];
}

/** Where the cap meets the grip (mm): the line across the handle at the top of the cap. */
export const CAP_SEAM = (half: number) => capOutline(half)[0][1];

/** The cap's half width at its groove (mm). */
const capHalfAt = (half: number, y: number) => {
  const p = capOutline(half);
  for (let i = 1; i < p.length; i++) if ((p[i - 1][1] - y) * (p[i][1] - y) <= 0) return p[i][0];
  return half;
};

/** Head + handle as ONE continuous silhouette: the head flows into the neck, no line where they meet. */
export function silhouette(t: Xf): string {
  const [c0, c1, , c3, c4] = HEAD_CURVES;
  const P = (p: Pt) => mm(p);
  const b = new PathB(t);
  const s = P(HEAD_START);
  b.M(s[0], s[1]);
  const seg = (c: [Pt, Pt, Pt]) => {
    const [a, bb, e] = c.map(P);
    b.C(a[0], a[1], bb[0], bb[1], e[0], e[1]);
  };
  seg(c0);
  // the right side down to where the fillet leaves the head curve
  const tf = cubicAtY(c0[2], c1, NECK_PROFILE.from / MM);
  seg(cubicHead(c0[2], c1, tf));
  // neck, grip and cap, right side
  const g = HANDLE_MM.grip;
  for (const [x, y] of NECK_PROFILE.pts) b.L(x, y);
  b.L(g.x, g.top);
  const cap = capOutline(g.x);
  for (const [x, y] of cap) b.L(x, y);
  // and back up the left side
  for (const [x, y] of [...cap].reverse()) b.L(-x, y);
  b.L(-g.x, g.top);
  for (const [x, y] of [...NECK_PROFILE.pts].reverse()) b.L(-x, y);
  // the left side's head curve from the fillet up: c3 reversed is the mirror of c1
  const [m1, m2] = cubicHead(c0[2], c1, tf).map(P);
  const l0 = mm(c3[2]);
  b.C(-m2[0], m2[1], -m1[0], m1[1], l0[0], l0[1]);
  seg(c4);
  b.Z();
  return b.d;
}

/**
 * Handle detail lines: the overgrip's top edge and its finishing band, the seams of the helical wrap, the line
 * where the cap meets the grip and the cap's groove. (The engraved Q, the logo, 4.2 mm tall, is named in a callout: at
 * drawing scale it would only be a speck.)
 */
export function handleDetail(t: Xf, view: "front" | "side" = "front"): string {
  const g = HANDLE_MM.grip;
  const half = view === "front" ? g.x : g.z;
  const seam = CAP_SEAM(half);
  const parts: string[] = [];
  const across = (y: number, w = half) => parts.push(new PathB(t).M(-w, y).L(w, y).d);
  across(g.top);
  across(g.top - g.band);
  across(seam);
  // seams of the wrap: on the front the tape climbs from right to left by half a pitch; seen from the
  // side, it climbs the other way
  const dir = view === "front" ? 1 : -1;
  const y0 = g.top - g.band;
  for (let j = -1; j < 6; j++) {
    const yk = y0 - 6 - j * g.pitch;
    const pts: V[] = [];
    for (let i = 0; i <= 16; i++) {
      const th = -Math.PI / 2 + (Math.PI * i) / 16;
      const y = yk - (g.pitch / 2) * (i / 16);
      if (y > y0 - 0.5 || y < seam + 0.5) continue;
      pts.push([dir * half * Math.sin(th), y]);
    }
    if (pts.length > 1) {
      const b = new PathB(t);
      pts.forEach(([x, y], i) => (i ? b.L(x, y) : b.M(x, y)));
      parts.push(b.d);
    }
  }
  const cap = HANDLE_MM.cap;
  across(cap.groove, capHalfAt(half, cap.groove) - 0.3);
  return parts.join(" ");
}

export function throat(t: Xf): string {
  const b = new PathB(t);
  const s = mm(THROAT_START);
  b.M(s[0], s[1]);
  for (const c of THROAT_CURVES) {
    const [a, bb, e] = c.map(mm);
    b.C(a[0], a[1], bb[0], bb[1], e[0], e[1]);
  }
  return b.Z().d;
}

/** Every hole at its own diameter (or all at `r`, if given). */
export function holes(t: Xf, r?: number): string {
  return HOLES_MM.map((h, i) => circle(t, h, r ?? HOLE_R_MM[i])).join(" ");
}

/**
 * The tangent edge: where the flat face ends, the head outline offset inward by `d` (the canonical 4 mm: the
 * 1.5 mm edge radius plus 2.5 mm). An open line over the top of the head, ending at `yEnd`: by default where
 * the outline leaves the head curve for the fillet into the neck, so the line never strays from the edge.
 */
export function tangentEdge(t: Xf, d = DIM.faceInset, yEnd = NECK_PROFILE.from): string {
  const pts = HEAD_PTS;
  const N = pts.length;
  const out: V[] = [];
  for (let i = 0; i < N; i++) {
    const a = pts[(i - 1 + N) % N];
    const c = pts[(i + 1) % N];
    const tx = c[0] - a[0];
    const ty = c[1] - a[1];
    const len = Math.hypot(tx, ty) || 1;
    // outline runs clockwise (y up), so the inward normal is (ty, -tx)
    out.push([pts[i][0] + (ty / len) * d, pts[i][1] + (-tx / len) * d]);
  }
  // HEAD_PTS starts just right of the top centre and runs clockwise: keep the run above yEnd through the top
  const iR = out.findIndex((p) => p[1] < yEnd);
  let iL = N - 1;
  while (iL > 0 && out[iL][1] >= yEnd) iL--;
  const cross = (p: V, q: V): V => {
    const k = (yEnd - p[1]) / (q[1] - p[1]);
    return [p[0] + (q[0] - p[0]) * k, yEnd];
  };
  const run: V[] = [cross(out[iL], out[iL + 1]), ...out.slice(iL + 1), ...out.slice(0, iR), cross(out[iR - 1], out[iR])];
  const b = new PathB(t);
  run.forEach(([x, y], i) => (i ? b.L(x, y) : b.M(x, y)));
  return b.d;
}

/** Side view half-thickness at height y (mm): 38.0 to the neck, 29.0 core, the grip, then the cap. */
export function sideHalf(y: number): number {
  const h = DIM.thickness / 2;
  const { taperTop, neckEnd, core, grip } = HANDLE_MM;
  if (y >= taperTop) return h;
  if (y >= grip.top) return h + (core.z - h) * smooth((taperTop - y) / (taperTop - neckEnd));
  const cap = capOutline(grip.z);
  if (y >= cap[0][1]) return grip.z;
  for (let i = 1; i < cap.length; i++) if ((cap[i - 1][1] - y) * (cap[i][1] - y) <= 0) return cap[i][0];
  return cap[cap.length - 1][0];
}

/** Side view: the 38.0 mm wall with its 1.5 mm edges, tapering through the neck into the grip and the cap. */
export function sideProfile(t: Xf): string {
  const h = DIM.thickness / 2;
  const top = DIM.headTop;
  const r = DIM.edgeR;
  const { taperTop, grip } = HANDLE_MM;
  const taper: V[] = [];
  for (let y = taperTop; y > grip.top; y -= 1) taper.push([sideHalf(y), y]);
  taper.push([sideHalf(grip.top), grip.top]);
  const cap = capOutline(grip.z);
  const right: V[] = [...taper, [grip.z, grip.top], ...cap];
  const b = new PathB(t).M(-h + r, top).L(h - r, top).Q(h, top, h, top - r);
  for (const [x, y] of right) b.L(x, y);
  for (const [x, y] of [...right].reverse()) b.L(-x, y);
  b.L(-h, top - r).Q(-h, top, -h + r, top).Z();
  return b.d;
}

/** Hidden edges in the side view: core faces, the top and bottom of every hole and the throat opening. */
export function sideHidden(t: Xf): string {
  const h = DIM.thickness / 2;
  const c = h - DIM.shell;
  const top = DIM.headTop - DIM.rimShell;
  const parts: string[] = [];
  const core = new PathB(t).M(-c, -96).L(-c, top - 4).Q(-c, top, -c + 4, top).L(c - 4, top).Q(c, top, c, top - 4).L(c, -96).Q(0, -112, -c, -96);
  parts.push(core.d);
  for (const row of HOLE_ROWS) {
    for (const y of [row.y + row.r, row.y - row.r]) parts.push(new PathB(t).M(-h, y).L(h, y).d);
  }
  for (const y of [-86.5, -127]) {
    const w = sideHalf(y);
    parts.push(new PathB(t).M(-w, y).L(w, y).d);
  }
  return parts.join(" ");
}

export type SectionPiece = { outer: string; core: string };
const LIP = 2.6;

/** Section A-A: one unbroken shell wrapping one unbroken core, edge to edge, with the canonical 1.5 mm edges. */
export function slabSection(t: Xf): SectionPiece {
  const W = HEAD_W;
  const h = DIM.thickness / 2;
  const R = DIM.edgeR;
  const sh = DIM.shell;
  const rs = DIM.rimShell;
  const rc = 0.6;
  return {
    outer: roundRect(t, -W, -h, W, h, [R, R, R, R]),
    core: roundRect(t, -W + rs, -h + sh, W - rs, h - sh, [rc, rc, rc, rc]),
  };
}

/** Section B-B around one moulded bore (centred on x = 0): the shell runs down every bore wall. */
export function boreSection(t: Xf, reach = 30): SectionPiece[] {
  const h = DIM.thickness / 2;
  const r = DIM.holeD / 2;
  const sh = DIM.shell;
  const ci = Math.max(0.6, LIP - sh);
  const big = 6;
  return [
    {
      outer: roundRect(t, -reach, -h, -r, h, [big, LIP, LIP, big]),
      core: roundRect(t, -reach + sh, -h + sh, -r - sh, h - sh, [big - sh, ci, ci, big - sh]),
    },
    {
      outer: roundRect(t, r, -h, reach, h, [LIP, big, big, LIP]),
      core: roundRect(t, r + sh, -h + sh, reach - sh, h - sh, [ci, big - sh, big - sh, ci]),
    },
  ];
}

/** Fibre lines inside the shell wall of the bore section, wrapping the lip. */
export function boreFibres(t: Xf, reach = 30): string {
  const h = DIM.thickness / 2;
  const r = DIM.holeD / 2;
  return [0.5, 1.0, 1.5]
    .map((k) => {
      const L = LIP - k;
      return (
        roundRect(t, -reach - 4, -h + k, -r - k, h - k, [L, L, L, L]) + " " + roundRect(t, r + k, -h + k, reach + 4, h - k, [L, L, L, L])
      );
    })
    .join(" ");
}

/** Fibre lines inside the slab shell, wrapping the rim. */
export function slabFibres(t: Xf): string {
  const W = HEAD_W;
  const h = DIM.thickness / 2;
  const r = DIM.edgeR / 2;
  return roundRect(t, -W + 1.5, -h + 1, W - 1.5, h - 1, [r, r, r, r]);
}

export const LIP_R = LIP;

/** Leader / dimension primitives in sheet units. */
export function arrow(tip: V, from: V, len: number, half: number): string {
  const dx = tip[0] - from[0];
  const dy = tip[1] - from[1];
  const l = Math.hypot(dx, dy) || 1;
  const ux = dx / l;
  const uy = dy / l;
  const bx = tip[0] - ux * len;
  const by = tip[1] - uy * len;
  return `M${n(tip[0])} ${n(tip[1])}L${n(bx - uy * half)} ${n(by + ux * half)}L${n(bx + uy * half)} ${n(by - ux * half)}Z`;
}
export const line = (a: V, b: V) => `M${n(a[0])} ${n(a[1])}L${n(b[0])} ${n(b[1])}`;
export const poly = (pts: V[]) => pts.map((p, i) => `${i ? "L" : "M"}${n(p[0])} ${n(p[1])}`).join("");
