// G08 measurement card: pure geometry for the flatness contour map and the guilloché rosette.
// Deterministic: the server and the client render identical path strings.
// Map units are millimetres, y down, origin at the head centre (racket-shape.ts is in dm, y up).

import { HEAD_CURVES, HEAD_START, HOLES, HOLE_RADIUS, THROAT_CURVES, THROAT_START, type Cubic, type Pt } from "@/lib/racket-shape";

const r1 = (v: number) => (Math.round(v * 10) / 10).toString();
const P = ([x, y]: Pt) => `${r1(x * 100)} ${r1(-y * 100)}`;
const curves = (start: Pt, cs: Cubic[]) => `M${P(start)}` + cs.map(([a, b, c]) => `C${P(a)} ${P(b)} ${P(c)}`).join("") + "Z";

/** Head bounding box in map units (mm). */
export const MAP_BOX = { x: -136, y: -161, w: 272, h: 322 };
export const mapViewBox = `${MAP_BOX.x} ${MAP_BOX.y} ${MAP_BOX.w} ${MAP_BOX.h}`;

export const headOutline = curves(HEAD_START, HEAD_CURVES);
export const throatOutline = curves(THROAT_START, THROAT_CURVES);
export const holeDots = HOLES.map(([x, y]) => ({ cx: Number(r1(x * 100)), cy: Number(r1(-y * 100)), r: Number(r1(HOLE_RADIUS * 100)) }));

/** Illustrative deviation field, in µm (0 at the reference surface, 12 at the highest point). */
function field(x: number, y: number) {
  // x, y in dm, y up
  const g = (dx: number, dy: number, s: number) => Math.exp(-(dx * dx + dy * dy) / (2 * s * s));
  return (
    0.92 * g(x - 0.46, y - 0.62, 0.36) +
    0.7 * g(x + 0.52, y + 0.02, 0.34) +
    0.5 * g(x - 0.18, y + 0.86, 0.3) +
    0.38 * g(x + 0.18, y - 1.08, 0.3) +
    0.08 * ((x + 1.3) / 2.6)
  );
}

type Seg = [number, number, number, number];

/** Marching squares over the head box; returns one path per level, joined into polylines. */
function contours(levels: number[], nx = 110, ny = 130) {
  const x0 = MAP_BOX.x / 100;
  const y0 = -(MAP_BOX.y + MAP_BOX.h) / 100;
  const dx = MAP_BOX.w / 100 / nx;
  const dy = MAP_BOX.h / 100 / ny;
  const v: number[][] = [];
  let max = 0;
  for (let j = 0; j <= ny; j++) {
    const row: number[] = [];
    for (let i = 0; i <= nx; i++) {
      const f = field(x0 + i * dx, y0 + j * dy);
      max = Math.max(max, f);
      row.push(f);
    }
    v.push(row);
  }
  const scale = 12 / max;
  for (const row of v) for (let i = 0; i < row.length; i++) row[i] *= scale;

  const toMap = (i: number, j: number): [number, number] => [(x0 + i * dx) * 100, -(y0 + j * dy) * 100];

  return levels.map((L) => {
    const segs: Seg[] = [];
    for (let j = 0; j < ny; j++) {
      for (let i = 0; i < nx; i++) {
        const a = v[j][i]; // (i, j)
        const b = v[j][i + 1]; // (i+1, j)
        const c = v[j + 1][i + 1]; // (i+1, j+1)
        const d = v[j + 1][i]; // (i, j+1)
        const idx = (a > L ? 1 : 0) | (b > L ? 2 : 0) | (c > L ? 4 : 0) | (d > L ? 8 : 0);
        if (idx === 0 || idx === 15) continue;
        const e = {
          ab: toMap(i + (L - a) / (b - a), j),
          bc: toMap(i + 1, j + (L - b) / (c - b)),
          dc: toMap(i + (L - d) / (c - d), j + 1),
          ad: toMap(i, j + (L - a) / (d - a)),
        };
        const push = (p: [number, number], q: [number, number]) => segs.push([p[0], p[1], q[0], q[1]]);
        switch (idx) {
          case 1: case 14: push(e.ab, e.ad); break;
          case 2: case 13: push(e.ab, e.bc); break;
          case 3: case 12: push(e.ad, e.bc); break;
          case 4: case 11: push(e.bc, e.dc); break;
          case 6: case 9: push(e.ab, e.dc); break;
          case 7: case 8: push(e.ad, e.dc); break;
          case 5: push(e.ab, e.ad); push(e.bc, e.dc); break;
          case 10: push(e.ab, e.bc); push(e.ad, e.dc); break;
        }
      }
    }
    return { level: L, d: join(segs) };
  });
}

/** Ramer-Douglas-Peucker: drop points closer than tol to the chord. */
function simplify(pts: [number, number][], tol: number): [number, number][] {
  if (pts.length < 3) return pts;
  const [ax, ay] = pts[0];
  const [bx, by] = pts[pts.length - 1];
  if (Math.hypot(bx - ax, by - ay) < 1e-6) {
    // closed loop: split at the point farthest from the start, simplify each half
    let far = 1;
    pts.forEach(([x, y], i) => {
      if (Math.hypot(x - ax, y - ay) > Math.hypot(pts[far][0] - ax, pts[far][1] - ay)) far = i;
    });
    return [...simplify(pts.slice(0, far + 1), tol).slice(0, -1), ...simplify(pts.slice(far), tol)];
  }
  const len = Math.hypot(bx - ax, by - ay) || 1;
  let worst = 0;
  let at = 0;
  for (let i = 1; i < pts.length - 1; i++) {
    const [px, py] = pts[i];
    const dist = Math.abs((bx - ax) * (ay - py) - (ax - px) * (by - ay)) / len;
    if (dist > worst) {
      worst = dist;
      at = i;
    }
  }
  if (worst <= tol) return [pts[0], pts[pts.length - 1]];
  return [...simplify(pts.slice(0, at + 1), tol).slice(0, -1), ...simplify(pts.slice(at), tol)];
}

/** Join loose segments into polylines (shared endpoints) for smooth, compact paths. */
function join(segs: Seg[]) {
  const key = (x: number, y: number) => `${Math.round(x * 100)},${Math.round(y * 100)}`;
  const ends = new Map<string, number[]>();
  segs.forEach((s, n) => {
    for (const k of [key(s[0], s[1]), key(s[2], s[3])]) {
      const list = ends.get(k);
      if (list) list.push(n);
      else ends.set(k, [n]);
    }
  });
  const used = new Uint8Array(segs.length);
  const out: string[] = [];
  for (let n = 0; n < segs.length; n++) {
    if (used[n]) continue;
    used[n] = 1;
    const line: [number, number][] = [
      [segs[n][0], segs[n][1]],
      [segs[n][2], segs[n][3]],
    ];
    // grow at the tail, then at the head
    for (const atHead of [false, true]) {
      for (;;) {
        const [x, y] = atHead ? line[0] : line[line.length - 1];
        const next = (ends.get(key(x, y)) ?? []).find((m) => !used[m]);
        if (next === undefined) break;
        used[next] = 1;
        const s = segs[next];
        const same = key(s[0], s[1]) === key(x, y);
        const p: [number, number] = same ? [s[2], s[3]] : [s[0], s[1]];
        if (atHead) line.unshift(p);
        else line.push(p);
      }
    }
    out.push(`M${simplify(line, 0.7).map(([x, y]) => `${r1(x)} ${r1(y)}`).join("L")}`);
  }
  return out.join("");
}

/** Contour lines every 2 µm. */
export const flatness = contours([2, 4, 6, 8, 10]);

/**
 * A guilloché rosette: one polar wave, repeated with small rotations (a rotation of the wave is a
 * phase shift, so the copies interleave into the engraved net). Radius about 100.
 */
export const ROSETTE_COPIES = 16;
export const ROSETTE_LOBES = 15;
export const rosetteWave = (() => {
  const pts: string[] = [];
  const steps = 600;
  for (let s = 0; s < steps; s++) {
    const t = (s / steps) * Math.PI * 2;
    const r = 74 + 17 * Math.sin(ROSETTE_LOBES * t) + 5 * Math.sin(3 * ROSETTE_LOBES * t);
    pts.push(`${r1(r * Math.cos(t))} ${r1(r * Math.sin(t))}`);
  }
  return `M${pts.join("L")}Z`;
})();
export const rosetteTurns = Array.from({ length: ROSETTE_COPIES }, (_, k) => (k * 360) / (ROSETTE_LOBES * ROSETTE_COPIES));
