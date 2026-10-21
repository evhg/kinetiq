// Pure geometry for the G11 icons and tier glyphs, drawn from racket-shape.ts.
// Screen px, y down. Self-contained so the icons can render in server or client components.

import { HANDLE, HEAD_CURVES, HEAD_START, THROAT_CURVES, THROAT_START, type Pt } from "@/lib/racket-shape";

export type V = [number, number];

/* ---------- G11 icon geometry (screen px, y down) ---------- */

const cubicSample = (p0: Pt, c: [Pt, Pt, Pt], steps: number): Pt[] => {
  const out: Pt[] = [];
  for (let i = 1; i <= steps; i++) {
    const t = i / steps;
    const u = 1 - t;
    const [c1, c2, e] = c;
    out.push([
      u * u * u * p0[0] + 3 * u * u * t * c1[0] + 3 * u * t * t * c2[0] + t * t * t * e[0],
      u * u * u * p0[1] + 3 * u * u * t * c1[1] + 3 * u * t * t * c2[1] + t * t * t * e[1],
    ]);
  }
  return out;
};

/**
 * The racket silhouette as a closed polygon for small icons: the real head outline from
 * racket-shape.ts flowing straight into a handle widened to `handleHalf` px so it survives a
 * 1.25px stroke. Top centre at (0, 0), length `len` px, y down.
 */
export function iconRacket(len: number, handleHalf: number): V[] {
  const top = HEAD_START[1];
  const butt = HANDLE.top - HANDLE.length;
  const k = len / (top - butt);
  const hw = handleHalf / k;
  const [c0, c1, , c3, c4] = HEAD_CURVES;
  const neck = -1.66;
  const c1b: [Pt, Pt, Pt] = [c1[0], [0.62, -1.2], [hw, neck]];
  const c3b: [Pt, Pt, Pt] = [[-0.62, -1.2], c3[1], c3[2]];
  const pts: Pt[] = [HEAD_START];
  pts.push(...cubicSample(HEAD_START, c0, 40));
  pts.push(...cubicSample(c0[2], c1b, 40));
  const endY = butt + hw;
  for (let i = 1; i <= 16; i++) pts.push([hw, neck + ((endY - neck) * i) / 16]);
  for (let i = 1; i <= 12; i++) {
    const a = (i / 12) * Math.PI;
    pts.push([hw * Math.cos(a), endY - hw * Math.sin(a)]);
  }
  for (let i = 1; i <= 16; i++) pts.push([-hw, endY + ((neck - endY) * i) / 16]);
  pts.push(...cubicSample([-hw, neck], c3b, 40));
  pts.push(...cubicSample(c3[2], c4, 40).slice(0, -1));
  return pts.map(([x, y]) => [x * k, (top - y) * k]);
}

/** Throat opening of the icon racket (same transform as iconRacket). */
export function iconThroat(len: number): V[] {
  const top = HEAD_START[1];
  const k = len / (top - (HANDLE.top - HANDLE.length));
  const pts: Pt[] = [THROAT_START];
  let p0 = THROAT_START;
  for (const c of THROAT_CURVES) {
    pts.push(...cubicSample(p0, c, 16));
    p0 = c[2];
  }
  return pts.slice(0, -1).map(([x, y]) => [x * k, (top - y) * k]);
}

export function movePts(pts: V[], o: { dx?: number; dy?: number; rot?: number; px?: number; py?: number }): V[] {
  const a = ((o.rot ?? 0) * Math.PI) / 180;
  const cos = Math.cos(a);
  const sin = Math.sin(a);
  const px = o.px ?? 0;
  const py = o.py ?? 0;
  return pts.map(([x, y]) => {
    const rx = px + (x - px) * cos - (y - py) * sin;
    const ry = py + (x - px) * sin + (y - py) * cos;
    return [rx + (o.dx ?? 0), ry + (o.dy ?? 0)];
  });
}

const inside = ([x, y]: V, poly: V[]) => {
  let c = false;
  for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) {
    const [xi, yi] = poly[i];
    const [xj, yj] = poly[j];
    if (yi > y !== yj > y && x < ((xj - xi) * (y - yi)) / (yj - yi) + xi) c = !c;
  }
  return c;
};
const distSeg = ([x, y]: V, [ax, ay]: V, [bx, by]: V) => {
  const dx = bx - ax;
  const dy = by - ay;
  const t = Math.max(0, Math.min(1, ((x - ax) * dx + (y - ay) * dy) / (dx * dx + dy * dy || 1)));
  return Math.hypot(x - (ax + t * dx), y - (ay + t * dy));
};
const near = (p: V, poly: V[], gap: number) => {
  for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) if (distSeg(p, poly[j], poly[i]) < gap) return true;
  return false;
};

const fmt = (v: number) => String(Number(v.toFixed(2)));

/** Closed polygon as path data. */
export function ptsPath(pts: V[], closed = true): string {
  return pts.map(([x, y], i) => `${i ? "L" : "M"}${fmt(x)} ${fmt(y)}`).join("") + (closed ? "Z" : "");
}

/**
 * Path data for the parts of a closed outline that are not hidden behind any of `fronts`
 * (each a closed polygon), leaving a `gap` px knockout so overlaps read as layered.
 */
export function occluded(back: V[], fronts: V[][], gap: number): string {
  const dense: V[] = [];
  for (let i = 0; i < back.length; i++) {
    const a = back[i];
    const b = back[(i + 1) % back.length];
    const n = Math.max(1, Math.ceil(Math.hypot(b[0] - a[0], b[1] - a[1]) / 0.2));
    for (let s = 0; s < n; s++) dense.push([a[0] + ((b[0] - a[0]) * s) / n, a[1] + ((b[1] - a[1]) * s) / n]);
  }
  const vis = dense.map((p) => !fronts.some((f) => inside(p, f) || near(p, f, gap)));
  // rotate so we start on a hidden point (or anywhere if all visible)
  const start = vis.indexOf(false);
  if (start < 0) return ptsPath(back);
  const runs: V[][] = [];
  let cur: V[] = [];
  for (let s = 1; s <= dense.length; s++) {
    const i = (start + s) % dense.length;
    if (vis[i]) cur.push(dense[i]);
    else if (cur.length) {
      runs.push(cur);
      cur = [];
    }
  }
  if (cur.length) runs.push(cur);
  return runs
    .filter((r) => r.length > 1)
    .map((r) => ptsPath(r.filter((_, i) => i % 3 === 0 || i === r.length - 1), false))
    .join("");
}

/** A sparse, staggered hole pattern for glyphs (same transform as iconRacket), centred on the face. */
export function iconHoles(len: number, step = 0.48): V[] {
  const top = HEAD_START[1];
  const k = len / (top - (HANDLE.top - HANDLE.length));
  const cy = 0.32;
  const out: V[] = [];
  for (let row = -3; row <= 3; row++) {
    const y = cy + row * step * 0.87;
    const off = row % 2 === 0 ? 0 : step / 2;
    for (let col = -3; col <= 3; col++) {
      const x = col * step + off;
      if ((x * x) / (0.86 * 0.86) + ((y - cy) * (y - cy)) / (1.02 * 1.02) < 1 && y > -0.45) out.push([x * k, (top - y) * k]);
    }
  }
  return out;
}

/** Points that sit clear of every front polygon by at least `margin` px. */
export function clearOf(points: V[], fronts: V[][], margin: number): V[] {
  return points.filter((p) => !fronts.some((f) => inside(p, f) || near(p, f, margin)));
}
