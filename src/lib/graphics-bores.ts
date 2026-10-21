// G06 drilled vs moulded: two magnified bores drawn at the same scale in one 1100 x 700 plate.
// Drilled: straight tows that stop dead at the bore, with cut ticks and a frayed rim.
// Moulded: potential-flow streamlines around a cylinder, psi = y (1 - R^2 / r^2), that part around
// the bore and rejoin, plus concentric wall lines running down the hole. Pure and deterministic.

export const PLATE = { w: 1100, h: 700, cx: 550, cy: 350, r: 172 } as const;

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
  /** Short ticks across every cut end, one path per cut tow (both ends). */
  ticks: string[];
  /** The ragged bore edge. */
  rim: string;
  /** A second, fainter ragged ring: the torn wall below the rim. */
  wall: string;
  /** Loose filaments lifted at the edge. */
  loose: string;
  /** Cut fibre ends seen on the bore wall: short radial stubs just inside the rim. */
  stubs: string;
  /** One cut end used as the callout target. */
  target: [number, number];
};

export function drilled(seed = 11): Drilled {
  const { w, cx, cy, r } = PLATE;
  const rnd = prng(seed);
  const lines: DrilledLine[] = [];
  const ticks: string[] = [];
  let loose = "";
  let stubs = "";
  const stub = (ang: number, len: number) => {
    const r0 = r - 3;
    const r1 = r0 - len;
    stubs += `M${f1(cx + Math.cos(ang) * r0)} ${f1(cy + Math.sin(ang) * r0)}L${f1(cx + Math.cos(ang) * r1)} ${f1(cy + Math.sin(ang) * r1)}`;
  };
  let target: [number, number] = [cx - r, cy];
  let bestT = Infinity;
  const tick = 5.5;
  for (const dy of OFFSETS) {
    const y = cy + dy;
    const o = 0.34 + 0.22 * rnd();
    if (Math.abs(dy) >= r - 1) {
      lines.push({ d: `M0 ${f1(y)}H${w}`, cut: false, o });
      continue;
    }
    const half = Math.sqrt(r * r - dy * dy);
    // Frayed: most ends sit a little back from the bore, a few stick out into it.
    const fray = () => (rnd() < 0.2 ? -(1 + rnd() * 5) : rnd() * 9);
    const xl = cx - half - fray();
    const xr = cx + half + fray();
    lines.push({ d: `M0 ${f1(y)}H${f1(xl)}M${f1(xr)} ${f1(y)}H${w}`, cut: true, o: Math.min(0.85, o + 0.2) });
    ticks.push(`M${f1(xl)} ${f1(y - tick)}V${f1(y + tick)}M${f1(xr)} ${f1(y - tick)}V${f1(y + tick)}`);
    // the same tow, cut, shows its ends on the wall
    const a = Math.atan2(dy, -half);
    stub(a, 7 + rnd() * 14);
    stub(Math.PI - a, 7 + rnd() * 14);
    // callout target: the cut end nearest 125 degrees on the upper left
    const ang = Math.atan2(-(y - cy), xl - cx);
    const dist = Math.abs(ang - (125 * Math.PI) / 180);
    if (dist < bestT) {
      bestT = dist;
      target = [xl, y];
    }
    // a loose filament now and then, lifted off the cut end
    if (rnd() < 0.28) {
      const side = rnd() < 0.5 ? -1 : 1;
      const x0 = side < 0 ? xl : xr;
      const len = 10 + rnd() * 18;
      // lifted off the cut end, pointing into the bore
      const a = (rnd() - 0.5) * 1.4;
      loose += `M${f1(x0)} ${f1(y)}L${f1(x0 - side * Math.cos(a) * len)} ${f1(y + Math.sin(a) * len)}`;
    }
  }
  // Ragged rim: radius noise at several frequencies, sampled every degree.
  const ragged = (rad: number, amp: number, s: number) => {
    const rr = prng(s);
    const ph = [rr() * 6.28, rr() * 6.28, rr() * 6.28];
    let d = "";
    for (let k = 0; k <= 360; k++) {
      const t = (k * Math.PI) / 180;
      const n = 0.5 * Math.sin(t * 23 + ph[0]) + 0.3 * Math.sin(t * 57 + ph[1]) + 0.2 * Math.sin(t * 131 + ph[2]);
      const jag = (rr() - 0.5) * 0.9;
      const rk = rad + amp * (n + jag);
      d += `${k ? "L" : "M"}${f1(cx + Math.cos(t) * rk)} ${f1(cy + Math.sin(t) * rk)}`;
    }
    return d + "Z";
  };
  return { lines, ticks, rim: ragged(r, 2.6, seed + 1), wall: ragged(r * 0.86, 2.2, seed + 2), loose, stubs, target };
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
    // Sample densely near the bore, coarsely towards the plate edges.
    const xs: number[] = [];
    for (let x = -cx; x <= w - cx; ) {
      xs.push(x);
      const near = Math.abs(x) < r * 2.4;
      x += near ? 4 : 14;
    }
    if (xs[xs.length - 1] !== w - cx) xs.push(w - cx);
    let d = "";
    xs.forEach((x, k) => {
      const y = streamY(c, x, r);
      d += `${k ? "L" : "M"}${f1(cx + x)} ${f1(cy + y)}`;
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
  // Callout target: the innermost upper streamline, 125 degrees round the bore (upper left).
  const tx = r * Math.cos((125 * Math.PI) / 180);
  const target: [number, number] = [cx + tx, cy + streamY(-sorted[0], tx, r)];
  return { lines, walls, target };
}
