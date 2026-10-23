// G04 consistency spikes (not measured): a narrow distribution inside its tolerance window, ±1.0 g for mass (355.0 g
// reference) and ±0.1 mm for balance (250.0 mm reference; owner, 2026-10-23). Each axis spans five windows either side
// of the reference, so the two windows draw the same width and the spikes read alike.
import { VB, n1, seeded } from "./graphics-plot";

export type SpikeSpec = {
  id: "mass" | "balance";
  reference: number;
  /** Half-width of the x axis, either side of the reference. */
  span: number;
  window: number;
  /** Minor tick spacing along the axis. */
  step: number;
  sigma: number;
  unit: string;
  seed: number;
};

export const SPIKES: SpikeSpec[] = [
  { id: "mass", reference: 355, span: 5, window: 1, step: 1, sigma: 0.24, unit: "g", seed: 3550 },
  { id: "balance", reference: 250, span: 0.5, window: 0.1, step: 0.1, sigma: 0.027, unit: "mm", seed: 2504 },
];

/** Peak height as a share of the plot. */
const PEAK = 0.86;

/** Box-Muller with a seeded source. */
function normals(seed: number, count: number) {
  const rnd = seeded(seed);
  const out: number[] = [];
  while (out.length < count) {
    const u = Math.max(1e-9, rnd());
    const v = rnd();
    const r = Math.sqrt(-2 * Math.log(u));
    out.push(r * Math.cos(2 * Math.PI * v), r * Math.sin(2 * Math.PI * v));
  }
  return out.slice(0, count);
}

export function spikeGeometry(s: SpikeSpec) {
  const lo = s.reference - s.span;
  const hi = s.reference + s.span;
  const X = (v: number) => ((v - lo) / (hi - lo)) * VB;
  const Y = (h: number) => VB - h * PEAK * VB;
  const g = (v: number) => Math.exp(-0.5 * ((v - s.reference) / s.sigma) ** 2);

  // The spike only: its tails meet the axis at about four sigma.
  const pts: [number, number][] = [];
  const reach = s.sigma * 4.2;
  const n = 72;
  for (let i = 0; i <= n; i++) {
    const v = s.reference - reach + (2 * reach * i) / n;
    pts.push([X(v), Y(g(v))]);
  }
  const line = pts.map((p, i) => `${i ? "L" : "M"}${n1(p[0])} ${n1(p[1])}`).join("");
  const area = `${line}L${n1(X(s.reference + reach))} ${VB}L${n1(X(s.reference - reach))} ${VB}Z`;

  // A rug of individual rackets along the baseline.
  const rug = normals(s.seed, 44).map((z) => n1(X(s.reference + z * s.sigma)));

  return {
    line,
    area,
    rug,
    lo,
    hi,
    windowLo: X(s.reference - s.window),
    windowHi: X(s.reference + s.window),
    centre: X(s.reference),
    /** Faint horizontal rules, as shares of the plot height from the top. */
    rules: [0, 0.25, 0.5, 0.75].map((f) => f * VB),
    /** Minor ticks every `step` across the axis. */
    minor: Array.from({ length: Math.round((s.span * 2) / s.step) + 1 }, (_, i) => X(lo + i * s.step)),
  };
}
