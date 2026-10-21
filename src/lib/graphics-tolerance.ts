// G03 tolerance graph (illustrative, not measured): surface deviation along the racket,
// 0 to 455 mm, against the ±15 µm limit. The trace is seeded noise, so it is identical on
// server and client, and it never leaves the band.
import { VB, seeded, splinePath } from "./graphics-plot";

export const LENGTH_MM = 455;
export const RANGE_UM = 120;
export const LIMIT_UM = 15;

export const X = (mm: number) => (mm / LENGTH_MM) * VB;
export const Y = (um: number) => VB / 2 - (um / RANGE_UM) * (VB / 2);

function traceKnots(): [number, number][] {
  const rnd = seeded(15015);
  const waves = [
    { len: 190, amp: 5.2, ph: rnd() * Math.PI * 2 },
    { len: 83, amp: 3.1, ph: rnd() * Math.PI * 2 },
    { len: 37, amp: 1.7, ph: rnd() * Math.PI * 2 },
    { len: 17, amp: 0.9, ph: rnd() * Math.PI * 2 },
  ];
  const step = 3.5;
  const raw: number[] = [];
  let walk = 0;
  for (let mm = 0; mm <= LENGTH_MM + 1e-6; mm += step) {
    walk = walk * 0.6 + (rnd() - 0.5) * 1.6;
    let v = walk;
    for (const w of waves) v += w.amp * Math.sin((mm / w.len) * Math.PI * 2 + w.ph);
    raw.push(v);
  }
  // Centre and scale so the furthest point sits at 11.6 µm: inside the limit, never on it.
  const mean = raw.reduce((a, b) => a + b, 0) / raw.length;
  const peak = Math.max(...raw.map((v) => Math.abs(v - mean)));
  const k = 11.6 / peak;
  return raw.map((v, i) => [X(Math.min(LENGTH_MM, i * step)), Y((v - mean) * k)]);
}

const knots = traceKnots();

export const tolerance = {
  trace: splinePath(knots),
  /** Knot polyline (viewBox units) for the glow head. */
  head: knots,
  top: Y(LIMIT_UM),
  bottom: Y(-LIMIT_UM),
  zeroY: Y(0),
  /** Horizontal rules (µm) on desktop and on phones. */
  rules: [-120, -90, -60, -30, 30, 60, 90, 120],
  rulesPhone: [-120, -60, 60, 120],
  /** Vertical rules and x ticks (mm). */
  ticks: [0, 100, 200, 300, 400, LENGTH_MM],
  ticksPhone: [0, 100, 200, 300, 400],
  /** Ruler marks hanging from the axis: every 25 mm, major every 100 mm and at the tip. */
  marks: [...Array.from({ length: 19 }, (_, i) => i * 25), LENGTH_MM].map((mm) => ({
    x: X(mm),
    major: mm % 100 === 0 || mm === LENGTH_MM,
  })),
};
