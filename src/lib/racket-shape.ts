// Single source for the racket silhouette, used by the 3D model and the
// static SVG fallback. Units: 1 = 10 cm. Head centre near the origin, y up.

export type Pt = [number, number];
export type Cubic = [Pt, Pt, Pt]; // control 1, control 2, end

export const HEAD_START: Pt = [0, 1.55];
export const HEAD_CURVES: Cubic[] = [
  [[0.85, 1.55], [1.32, 0.95], [1.3, 0.25]],
  [[1.28, -0.55], [0.75, -1.05], [0.2, -1.55]],
  // flat bottom of the throat to the left side
  [[0.07, -1.55], [-0.07, -1.55], [-0.2, -1.55]],
  [[-0.75, -1.05], [-1.28, -0.55], [-1.3, 0.25]],
  [[-1.32, 0.95], [-0.85, 1.55], [0, 1.55]],
];

/** The open "bridge" above the handle, as a closed cubic path. */
export const THROAT_START: Pt = [-0.32, -0.88];
export const THROAT_CURVES: Cubic[] = [
  [[-0.1, -0.86], [0.1, -0.86], [0.32, -0.88]],
  [[0.3, -1.0], [0.12, -1.2], [0, -1.27]],
  [[-0.12, -1.2], [-0.3, -1.0], [-0.32, -0.88]],
];

export const HOLE_RADIUS = 0.062;
export const HOLE_COUNT = 42;
export const THICKNESS = 0.38;

export const HANDLE = { radius: 0.165, top: -1.5, length: 1.5 };

/** 42 holes on a staggered grid, nearest to the face centre first. */
export const HOLES: Pt[] = (() => {
  const centre: Pt = [0, 0.3];
  const step = 0.27;
  const candidates: Pt[] = [];
  for (let row = -6; row <= 6; row++) {
    const y = centre[1] + row * step * 0.87;
    const offset = row % 2 === 0 ? 0 : step / 2;
    for (let col = -6; col <= 6; col++) {
      const x = col * step + offset;
      const inside = (x * x) / (1.0 * 1.0) + ((y - centre[1]) * (y - centre[1])) / (1.08 * 1.08) < 1;
      if (inside && y > -0.62) candidates.push([Number(x.toFixed(3)), Number(y.toFixed(3))]);
    }
  }
  const d = ([x, y]: Pt) => x * x * 1.1 + (y - centre[1]) * (y - centre[1]);
  return candidates.sort((a, b) => d(a) - d(b) || a[0] - b[0]).slice(0, HOLE_COUNT);
})();

/** SVG path data for the outline, the throat and every hole (y flipped for SVG). */
export function racketSvgPath(scale = 100, ox = 150, oy = 170): { outline: string; holes: string } {
  const p = ([x, y]: Pt) => `${(ox + x * scale).toFixed(1)} ${(oy - y * scale).toFixed(1)}`;
  const curves = (start: Pt, cs: Cubic[]) =>
    `M${p(start)} ` + cs.map(([a, b, c]) => `C${p(a)} ${p(b)} ${p(c)}`).join(" ") + " Z";
  const r = HOLE_RADIUS * scale;
  const holes = HOLES.map(([x, y]) => {
    const [cx, cy] = [ox + x * scale, oy - y * scale];
    return `M${(cx - r).toFixed(1)} ${cy.toFixed(1)} a${r.toFixed(1)} ${r.toFixed(1)} 0 1 0 ${(2 * r).toFixed(1)} 0 a${r.toFixed(1)} ${r.toFixed(1)} 0 1 0 ${(-2 * r).toFixed(1)} 0 Z`;
  }).join(" ");
  return { outline: curves(HEAD_START, HEAD_CURVES), holes: `${curves(THROAT_START, THROAT_CURVES)} ${holes}` };
}
