// Pure geometry for the G01 technical drawing, G10c ghost contour and G11 glyphs.
// Everything is generated from racket-shape.ts. Drawing units are millimetres with
// y up (1 racket unit = 100 mm); a Xf maps them onto a sheet (SVG user units, y down).

import { HANDLE, HEAD_CURVES, HEAD_START, HOLES, HOLE_RADIUS, THICKNESS, THROAT_CURVES, THROAT_START, type Pt } from "@/lib/racket-shape";

export type V = [number, number];
/** Sheet transform: sheet = (ox + x * s, oy - y * s). */
export type Xf = { ox: number; oy: number; s: number };

const MM = 100;
export const DIM = {
  length: Math.round((HEAD_START[1] - (HANDLE.top - HANDLE.length)) * MM), // 455
  width: 260,
  thickness: THICKNESS * MM, // 38
  holeD: HOLE_RADIUS * 2 * MM, // 12.4
  holes: HOLES.length, // 42
  headTop: HEAD_START[1] * MM, // 155
  buttY: (HANDLE.top - HANDLE.length) * MM, // -300
  handleR: HANDLE.radius * MM, // 16.5
  shell: 2, // drawn shell wall in sections (mm)
  rimShell: 3,
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

const cubicPts = (start: Pt, curves: [Pt, Pt, Pt][], steps = 48): V[] => {
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

/** Hole rows, top to bottom: y and sorted x positions (mm). */
export const HOLE_ROWS: { y: number; xs: number[] }[] = (() => {
  const m = new Map<number, number[]>();
  for (const [x, y] of HOLES) {
    const k = Math.round(y * MM * 10) / 10;
    m.set(k, [...(m.get(k) ?? []), Math.round(x * MM * 10) / 10]);
  }
  return [...m.entries()].sort((a, b) => b[0] - a[0]).map(([y, xs]) => ({ y, xs: xs.sort((a, b) => a - b) }));
})();

export const HOLES_MM: V[] = HOLES.map(mm);

/** Widest point of the head (the 260 dimension). */
export const HEAD_MAX: V = HEAD_PTS.reduce((a, p) => (p[0] > a[0] ? p : a), [0, 0] as V);

/**
 * Section plane A-A: between the widest row of holes and the row above, where the cut
 * meets no hole, so the section shows one unbroken shell around one unbroken core.
 */
export const CUT_Y = (() => {
  const i = HOLE_ROWS.reduce((best, r, k) => (r.xs.length > HOLE_ROWS[best].xs.length || (r.xs.length === HOLE_ROWS[best].xs.length && Math.abs(r.y - HEAD_MAX[1]) < Math.abs(HOLE_ROWS[best].y - HEAD_MAX[1])) ? k : best), 0);
  return (HOLE_ROWS[i].y + HOLE_ROWS[i - 1].y) / 2;
})();
export const HEAD_W = headHalfWidth(CUT_Y);

/** Section plane B-B: through one hole of the lowest row, for the bore detail. */
export const BORE_ROW = HOLE_ROWS[HOLE_ROWS.length - 1];
export const BORE: V = [BORE_ROW.xs[0], BORE_ROW.y];

/** Head + handle as ONE continuous silhouette: no line where the handle meets the head. */
export function silhouette(t: Xf): string {
  const [c0, c1, , c3, c4] = HEAD_CURVES;
  const P = (p: Pt) => mm(p);
  const b = new PathB(t);
  const hr = DIM.handleR;
  const by = DIM.buttY;
  const s = P(HEAD_START);
  b.M(s[0], s[1]);
  const seg = (c: [Pt, Pt, Pt]) => {
    const [a, bb, e] = c.map(P);
    b.C(a[0], a[1], bb[0], bb[1], e[0], e[1]);
  };
  seg(c0);
  seg(c1);
  // fillet from the throat foot into the handle, tangent to the head curve
  b.C(17.4, -157.4, hr, -159.5, hr, -164);
  b.L(hr, by + 12);
  b.C(hr, by + 9, hr + 1.6, by + 8, hr + 1.6, by + 5.5);
  b.L(hr + 1.6, by + 2.4);
  b.Q(hr + 1.6, by, hr - 0.8, by);
  b.L(-hr + 0.8, by);
  b.Q(-hr - 1.6, by, -hr - 1.6, by + 2.4);
  b.L(-hr - 1.6, by + 5.5);
  b.C(-hr - 1.6, by + 8, -hr, by + 9, -hr, by + 12);
  b.L(-hr, -164);
  b.C(-hr, -159.5, -17.4, -157.4, -20, -155);
  seg(c3);
  seg(c4);
  b.Z();
  return b.d;
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

export function holes(t: Xf, r = DIM.holeD / 2): string {
  return HOLES_MM.map((h) => circle(t, h, r)).join(" ");
}

/** Inner tangent edge of the frame: the head outline offset inward (convex polygon offset). */
export function tangentEdge(t: Xf, d = 13): string {
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
  const b = new PathB(t);
  out.forEach(([x, y], i) => (i ? b.L(x, y) : b.M(x, y)));
  return b.Z().d;
}

/** Side view half-thickness at height y (mm). */
export function sideHalf(y: number): number {
  const h = DIM.thickness / 2;
  const hr = DIM.handleR;
  if (y >= -105) return h;
  if (y <= -164) return hr;
  const k = (-105 - y) / 59;
  const e = k * k * (3 - 2 * k);
  return h + (hr - h) * e;
}

export function sideProfile(t: Xf): string {
  const h = DIM.thickness / 2;
  const hr = DIM.handleR;
  const top = DIM.headTop;
  const by = DIM.buttY;
  const r = 7;
  const b = new PathB(t)
    .M(-h + r, top)
    .L(h - r, top)
    .Q(h, top, h, top - r)
    .L(h, -105)
    .C(h, -128, hr, -140, hr, -164)
    .L(hr, by + 12)
    .C(hr, by + 9, hr + 1.6, by + 8, hr + 1.6, by + 5.5)
    .L(hr + 1.6, by + 2.4)
    .Q(hr + 1.6, by, hr - 0.8, by)
    .L(-hr + 0.8, by)
    .Q(-hr - 1.6, by, -hr - 1.6, by + 2.4)
    .L(-hr - 1.6, by + 5.5)
    .C(-hr - 1.6, by + 8, -hr, by + 9, -hr, by + 12)
    .L(-hr, -164)
    .C(-hr, -140, -h, -128, -h, -105)
    .L(-h, top - r)
    .Q(-h, top, -h + r, top)
    .Z();
  return b.d;
}

/** Hidden edges in the side view: core faces, every hole row and the throat opening. */
export function sideHidden(t: Xf): string {
  const h = DIM.thickness / 2;
  const c = h - DIM.shell;
  const top = DIM.headTop - DIM.rimShell;
  const parts: string[] = [];
  const core = new PathB(t).M(-c, -96).L(-c, top - 4).Q(-c, top, -c + 4, top).L(c - 4, top).Q(c, top, c, top - 4).L(c, -96).Q(0, -112, -c, -96);
  parts.push(core.d);
  const r = DIM.holeD / 2;
  for (const row of HOLE_ROWS) {
    for (const y of [row.y + r, row.y - r]) parts.push(new PathB(t).M(-h, y).L(h, y).d);
  }
  for (const y of [-86.5, -127]) {
    const w = sideHalf(y);
    parts.push(new PathB(t).M(-w, y).L(w, y).d);
  }
  return parts.join(" ");
}

export type SectionPiece = { outer: string; core: string };
const LIP = 2.6;

/** Section A-A: one unbroken shell wrapping one unbroken core, edge to edge. */
export function slabSection(t: Xf): SectionPiece {
  const W = HEAD_W;
  const h = DIM.thickness / 2;
  const R = 15;
  const sh = DIM.shell;
  const rs = DIM.rimShell;
  const rc = R - rs;
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
  const R = 15;
  return roundRect(t, -W + 1.5, -h + 1, W - 1.5, h - 1, [R - 1.5, R - 1.5, R - 1.5, R - 1.5]);
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
