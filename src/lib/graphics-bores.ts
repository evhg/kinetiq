// G06 drilled vs moulded: two magnified bores drawn at the same scale in one 1100 x 700 plate.
// Drilled: straight tows that stop dead at the bore, with cut ticks and a frayed rim.
// Moulded: potential-flow streamlines around a cylinder, psi = y (1 - R^2 / r^2), that part around
// the bore and rejoin, plus concentric wall lines running down the hole. Pure and deterministic.

export const PLATE = { w: 1100, h: 700, cx: 550, cy: 350, r: 172 } as const;

/** Where both callouts point, in degrees round the bore (upper left), so the pair reads alike. */
export const TARGET_DEG = 120;

/** Number of tows across the plate (the same on both sides, so the pair reads at one scale). */
export const TOWS = 60;
const PITCH = (PLATE.h - 28) / TOWS; // about 11.2 units

/** mulberry32 */
function prng(seed: number) {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const f1 = (v: number) => {
  const r = Math.round(v * 10) / 10;
  return Object.is(r, -0) ? "0" : String(r);
};

/** Offsets of the tows from the plate centre line, outermost last when sorted by |dy|. */
const OFFSETS = Array.from({ length: TOWS }, (_, i) => (i - (TOWS - 1) / 2) * PITCH);

// ---------------------------------------------------------------------------------------------
// Drilled

export type DrilledLine = { d: string; cut: boolean; o: number };

export type Drilled = {
  lines: DrilledLine[];
  /** Short ticks across the cut ends, one path per cut tow (both ends). */
  ticks: string[];
  /** The ragged bore edge, with a few breakout chips where material tore away. */
  rim: string;
  /**
   * The torn wall seen down the bore: broken, wobbling rings with gaps, the counterpart of the
   * moulded side's clean concentric wall lines. Outer to inner.
   */
  walls: { d: string; o: number }[];
  /** Frayed filaments: short strands splayed off cut ends, and a few lifted into the bore. */
  loose: string;
  /** One cut end used as the callout target. */
  target: [number, number];
};

const TAU = Math.PI * 2;

/** A ragged ring: radius noise at several frequencies plus optional outward chips (breakout). */
function raggedRing(rad: number, amp: number, seed: number, chips: number) {
  const rr = prng(seed);
  const ph = [rr() * TAU, rr() * TAU, rr() * TAU];
  // Breakout chips sit where the tows are cut (the left and right flanks of the bore), as flat-floored
  // notches with steep sides, never as spikes.
  const cs = Array.from({ length: chips }, (_, k) => ({
    a: (k % 2 ? Math.PI : 0) + (rr() - 0.5) * 1.3,
    w: 0.07 + rr() * 0.07,
    d: 4 + rr() * 4,
  }));
  const N = 360;
  const radius = new Float64Array(N + 1);
  for (let k = 0; k < N; k++) {
    const t = (k / N) * TAU;
    const n = 0.5 * Math.sin(t * 23 + ph[0]) + 0.3 * Math.sin(t * 57 + ph[1]) + 0.2 * Math.sin(t * 131 + ph[2]);
    let chip = 0;
    for (const c of cs) {
      const d = Math.abs((((t - c.a) % TAU) + TAU * 1.5) % TAU - Math.PI);
      const e = Math.min(1, Math.max(0, (c.w - d) / (0.45 * c.w)));
      chip += c.d * e * e * (3 - 2 * e);
    }
    radius[k] = rad + amp * (n + (rr() - 0.5) * 0.9) + chip;
  }
  radius[N] = radius[0];
  /** Radius at angle t (radians, SVG y down). */
  const at = (t: number) => {
    const u = ((((t % TAU) + TAU) % TAU) / TAU) * N;
    const i = Math.min(N - 1, Math.floor(u));
    return radius[i] + (radius[i + 1] - radius[i]) * (u - i);
  };
  return { at, radius, N };
}

export function drilled(seed = 11): Drilled {
  const { w, cx, cy, r } = PLATE;
  const rnd = prng(seed);
  const rim = raggedRing(r, 2.4, seed + 1, 4);
  const maxAbs = Math.max(...OFFSETS.map(Math.abs));
  const lines: DrilledLine[] = [];
  const ticks: string[] = [];
  let loose = "";
  let target: [number, number] = [cx - r, cy];
  let bestT = Infinity;
  const tick = 5;

  /** A strand leaving a cut end at (x0, y), heading `side` (+1 right, -1 left), bent by `a`. */
  const strand = (x0: number, y: number, side: number, len: number, a: number) => {
    const ex = x0 + side * Math.cos(a) * len;
    const ey = y + Math.sin(a) * len;
    const qx = x0 + side * len * 0.55;
    loose += `M${f1(x0 - side * 2)} ${f1(y)}Q${f1(qx)} ${f1(y + Math.sin(a) * len * 0.25)} ${f1(ex)} ${f1(ey)}`;
  };

  for (const dy of OFFSETS) {
    const y = cy + dy;
    const rank = Math.abs(dy) / maxAbs;
    // Brightest at the bore (where the damage is), falling away like the moulded side's lines.
    const o = Math.max(0.2, 0.74 - 0.56 * rank) * (0.94 + 0.12 * rnd());
    if (Math.abs(dy) >= r + 6) {
      lines.push({ d: `M0 ${f1(y)}H${w}`, cut: false, o });
      continue;
    }
    // Where this tow meets the real (ragged, chipped) rim on each side.
    const meet = (left: boolean) => {
      let half = Math.sqrt(Math.max(0, r * r - dy * dy));
      for (let k = 0; k < 3; k++) {
        const t = Math.atan2(dy, left ? -half : half);
        const rk = rim.at(t);
        half = Math.sqrt(Math.max(0, rk * rk - dy * dy));
      }
      return half;
    };
    const hl = meet(true);
    const hr = meet(false);
    if (hl < 1 && hr < 1) {
      lines.push({ d: `M0 ${f1(y)}H${w}`, cut: false, o });
      continue;
    }
    // Frayed: most ends sit a little back from the bore, a few stick out into it.
    const fray = () => (rnd() < 0.22 ? -(1 + rnd() * 5) : rnd() * 8);
    const xl = cx - hl - fray();
    const xr = cx + hr + fray();
    lines.push({ d: `M0 ${f1(y)}H${f1(xl)}M${f1(xr)} ${f1(y)}H${w}`, cut: true, o });
    // Cut ticks only where the tow meets the wall steeply; near the tangent they would pile onto the rim.
    if (Math.abs(dy) < r * 0.9) {
      ticks.push(`M${f1(xl)} ${f1(y - tick)}V${f1(y + tick)}M${f1(xr)} ${f1(y - tick)}V${f1(y + tick)}`);
    }
    // Fray: now and then a strand splays off the cut end, and a rarer longer one lifts into the bore.
    for (const [x0, side] of [
      [xl, 1],
      [xr, -1],
    ] as const) {
      const u = rnd();
      if (u < 0.3) strand(x0, y, side, 5 + rnd() * 7, (rnd() < 0.5 ? -1 : 1) * (0.18 + rnd() * 0.35));
      else if (u < 0.4) strand(x0, y, side, 14 + rnd() * 14, (rnd() - 0.5) * 1.1);
    }
    // callout target: the cut end nearest TARGET_DEG on the upper left
    const ang = Math.atan2(-(y - cy), xl - cx);
    const dist = Math.abs(ang - (TARGET_DEG * Math.PI) / 180);
    if (dist < bestT) {
      bestT = dist;
      target = [xl, y];
    }
  }

  /** Arcs of a ring, from angle a for length l (radians), sampled every degree. */
  const arcPath = (radiusAt: (t: number) => number, arcs: [number, number][]) => {
    let d = "";
    for (const [a, l] of arcs) {
      const n = Math.max(2, Math.round((l * 180) / Math.PI));
      for (let k = 0; k <= n; k++) {
        const t = a + (l * k) / n;
        const rk = radiusAt(t);
        d += `${k ? "L" : "M"}${f1(cx + Math.cos(t) * rk)} ${f1(cy + Math.sin(t) * rk)}`;
      }
    }
    return d;
  };

  // Torn wall: where the moulded side shows continuous wall lines, the drilled wall shows only
  // broken fragments of ply edges at a few depths, each following the rim's chips a little.
  const walls: { d: string; o: number }[] = [];
  const wr = prng(seed + 7);
  const DEPTHS = [0.055, 0.1, 0.14];
  const ALPHA = [0.4, 0.28, 0.18];
  DEPTHS.forEach((dp, k) => {
    const ring = raggedRing(r * (1 - dp), 1.1, seed + 20 + k, 0);
    const follow = 0.6 - 0.2 * k;
    const at = (t: number) => ring.at(t) + (rim.at(t) - r) * follow;
    const arcs: [number, number][] = [];
    let a = wr() * TAU;
    const end = a + TAU;
    while (a < end - 0.4) {
      const l = Math.min(end - a - 0.2, 0.25 + wr() * 0.9);
      arcs.push([a, l]);
      a += l + 0.2 + wr() * 0.8;
    }
    walls.push({ d: arcPath(at, arcs), o: ALPHA[k] });
  });

  // The rim, sampled every degree.
  return { lines, ticks, rim: arcPath(rim.at, [[0, TAU]]) + "Z", walls, loose, target };
}

// ---------------------------------------------------------------------------------------------
// Moulded

export type MouldedLine = { d: string; /** 0 = hugging the bore, 1 = outermost */ rank: number; order: number };

export type Moulded = {
  lines: MouldedLine[];
  /** Wall rings, outer to inner (perspective down the bore). */
  walls: { r: number; o: number }[];
  /** A point on an inner streamline at the bore's shoulder, the callout target. */
  target: [number, number];
};

/** Douglas-Peucker on a polyline. */
function simplify(pts: [number, number][], tol: number): [number, number][] {
  const n = pts.length;
  if (n < 3) return pts;
  const keep = new Uint8Array(n);
  keep[0] = keep[n - 1] = 1;
  const stack: [number, number][] = [[0, n - 1]];
  while (stack.length) {
    const [a, b] = stack.pop()!;
    const [ax, ay] = pts[a];
    const dx = pts[b][0] - ax;
    const dy = pts[b][1] - ay;
    const L = Math.hypot(dx, dy) || 1e-9;
    let worst = -1;
    let wd = tol;
    for (let k = a + 1; k < b; k++) {
      const dist = Math.abs((pts[k][0] - ax) * dy - (pts[k][1] - ay) * dx) / L;
      if (dist > wd) {
        wd = dist;
        worst = k;
      }
    }
    if (worst > 0) {
      keep[worst] = 1;
      stack.push([a, worst], [worst, b]);
    }
  }
  return pts.filter((_, k) => keep[k]);
}

/** y offset (from the axis, same sign as c) of the streamline psi = c at horizontal offset x. */
function streamY(c: number, x: number, R: number) {
  const s = Math.sign(c) || 1;
  const cc = Math.abs(c);
  let lo = Math.sqrt(Math.max(0, R * R - x * x)) + 1e-6;
  let hi = cc + R + 1;
  const f = (y: number) => y * (1 - (R * R) / (x * x + y * y)) - cc;
  if (f(lo) > 0) return s * lo;
  for (let k = 0; k < 48; k++) {
    const m = (lo + hi) / 2;
    if (f(m) > 0) hi = m;
    else lo = m;
  }
  return s * ((lo + hi) / 2);
}

export function moulded(): Moulded {
  const { w, cx, cy, r } = PLATE;
  const maxAbs = Math.max(...OFFSETS.map(Math.abs));
  const sorted = [...OFFSETS].map((c) => Math.abs(c)).sort((a, b) => a - b);
  const lines: MouldedLine[] = OFFSETS.map((c) => {
    // Sample densely, then keep only the points the eye needs
    // (within 0.35 units of the chord) so the 60 lines stay small in the markup.
    const pts: [number, number][] = [];
    for (let x = -cx; x < w - cx; x += 2) pts.push([cx + x, cy + streamY(c, x, r)]);
    pts.push([w, cy + streamY(c, w - cx, r)]);
    let d = "";
    simplify(pts, 0.35).forEach(([x, y], k) => {
      d += `${k ? "L" : "M"}${f1(x)} ${f1(y)}`;
    });
    return { d, rank: Math.abs(c) / maxAbs, order: sorted.indexOf(Math.abs(c)) >> 1 };
  });
  // Wall rings: spacing shrinks with depth, like looking down a polished bore.
  const walls: { r: number; o: number }[] = [];
  let rr = r;
  let gap = r * 0.05;
  for (let k = 0; k < 9; k++) {
    walls.push({ r: rr, o: k === 0 ? 1 : 0.62 * Math.pow(0.8, k) });
    rr -= gap;
    gap *= 0.84;
  }
  // Callout target: the innermost upper streamline, TARGET_DEG round the bore (upper left).
  const tx = r * Math.cos((TARGET_DEG * Math.PI) / 180);
  const target: [number, number] = [cx + tx, cy + streamY(-sorted[0], tx, r)];
  return { lines, walls, target };
}
