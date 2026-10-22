// Single source for the racket, used by every graphic (G01, G05, G07, G08, G11, G15) and matched by the
// Blender stills (the canonical racket, render audit 2026-10-22, section 4). Units: 1 = 10 cm. Head centre
// near the origin, y up. Overall 455.0 x 260.0 x 38.0 mm: the FIP limits for length, width and thickness.

export type Pt = [number, number];
export type Cubic = [Pt, Pt, Pt]; // control 1, control 2, end
/** A hole: centre x, centre y and its own radius. */
export type Hole = [number, number, number];

/** Head width: 260.0 mm, the FIP limit (Rules of Padel, the racket, point 4). */
export const HEAD_WIDTH = 2.6;

export const HEAD_START: Pt = [0, 1.55];
const DRAWN_CURVES: Cubic[] = [
  [[0.85, 1.55], [1.32, 0.95], [1.3, 0.25]],
  [[1.28, -0.55], [0.75, -1.05], [0.2, -1.55]],
  // flat bottom of the throat to the left side
  [[0.07, -1.55], [-0.07, -1.55], [-0.2, -1.55]],
  [[-0.75, -1.05], [-1.28, -0.55], [-1.3, 0.25]],
  [[-1.32, 0.95], [-0.85, 1.55], [0, 1.55]],
];

/** Largest x on a cubic: its ends, or where dx/dt = 0 (a quadratic in t). */
function cubicMaxX(p0: Pt, [c1, c2, e]: Cubic): number {
  const x = (t: number) => {
    const u = 1 - t;
    return u * u * u * p0[0] + 3 * u * u * t * c1[0] + 3 * u * t * t * c2[0] + t * t * t * e[0];
  };
  const d0 = c1[0] - p0[0];
  const d1 = c2[0] - c1[0];
  const d2 = e[0] - c2[0];
  const a = d0 - 2 * d1 + d2;
  const b = 2 * (d1 - d0);
  const ts = [0, 1];
  if (Math.abs(a) < 1e-12) {
    if (Math.abs(b) > 1e-12) ts.push(-d0 / b);
  } else {
    const disc = b * b - 4 * a * d0;
    if (disc >= 0) ts.push((-b + Math.sqrt(disc)) / (2 * a), (-b - Math.sqrt(disc)) / (2 * a));
  }
  return Math.max(...ts.filter((t) => t >= 0 && t <= 1).map(x));
}

/**
 * The head outline, clockwise from the top centre. The drawn curves peak at 260.1 mm, so x is scaled to put
 * the widest point at exactly HEAD_WIDTH (the length is unchanged).
 */
export const HEAD_CURVES: Cubic[] = (() => {
  let p0 = HEAD_START;
  let half = 0;
  for (const c of DRAWN_CURVES) {
    half = Math.max(half, cubicMaxX(p0, c));
    p0 = c[2];
  }
  const k = HEAD_WIDTH / 2 / half;
  return DRAWN_CURVES.map((c) => c.map(([x, y]) => [x * k, y]) as Cubic);
})();

/** The open "bridge" above the handle, as a closed cubic path. */
export const THROAT_START: Pt = [-0.32, -0.88];
export const THROAT_CURVES: Cubic[] = [
  [[-0.1, -0.86], [0.1, -0.86], [0.32, -0.88]],
  [[0.3, -1.0], [0.12, -1.2], [0, -1.27]],
  [[-0.12, -1.2], [-0.3, -1.0], [-0.32, -0.88]],
];

export const THICKNESS = 0.38;

/** The edge: the face meets the 38 mm side wall over a 1.5 mm radius; the twill folds over it. */
export const EDGE_RADIUS = 0.015;
/** The flat face runs to 4 mm in from the outline: the 1.5 mm edge radius plus 2.5 mm. */
export const FACE_INSET = 0.04;

/** The 34 grid holes: 12.4 mm. */
export const HOLE_RADIUS = 0.062;
/** The crown of 8 along the top: 14.0 mm. They sit within 40 mm of the edge, where FIP rule 6 allows up to 20 mm. */
export const CROWN_RADIUS = 0.07;
export const CROWN_COUNT = 8;
export const HOLE_COUNT = 42;

/**
 * The canonical 42 holes (render audit section 7, renders4/canon/canon_holes.py), [x, y, r].
 * First the crown of 8: on the outline inset 31 mm, 32 mm apart along it, the first pair 16.5 mm either side
 * of the centre line. Then 34 on a rhombic lattice: columns 24.5 mm apart, rows 14.3 mm apart, rows
 * A B A C A C A C A B A top to bottom (A: 0, ±49 mm; B: ±24.5; C: ±24.5, ±73.5), from y +83.4 to -59.6 mm.
 * The sides beyond ±80 mm stay solid.
 */
export const HOLES: Hole[] = [
  [-0.1646, 1.2304, 0.07], [0.1646, 1.2304, 0.07], [-0.4725, 1.1475, 0.07], [0.4725, 1.1475, 0.07],
  [-0.7344, 0.9669, 0.07], [0.7344, 0.9669, 0.07], [-0.9105, 0.702, 0.07], [0.9105, 0.702, 0.07],
  [-0.49, 0.834, 0.062], [0, 0.834, 0.062], [0.49, 0.834, 0.062],
  [-0.245, 0.691, 0.062], [0.245, 0.691, 0.062],
  [-0.49, 0.548, 0.062], [0, 0.548, 0.062], [0.49, 0.548, 0.062],
  [-0.735, 0.405, 0.062], [-0.245, 0.405, 0.062], [0.245, 0.405, 0.062], [0.735, 0.405, 0.062],
  [-0.49, 0.262, 0.062], [0, 0.262, 0.062], [0.49, 0.262, 0.062],
  [-0.735, 0.119, 0.062], [-0.245, 0.119, 0.062], [0.245, 0.119, 0.062], [0.735, 0.119, 0.062],
  [-0.49, -0.024, 0.062], [0, -0.024, 0.062], [0.49, -0.024, 0.062],
  [-0.735, -0.167, 0.062], [-0.245, -0.167, 0.062], [0.245, -0.167, 0.062], [0.735, -0.167, 0.062],
  [-0.49, -0.31, 0.062], [0, -0.31, 0.062], [0.49, -0.31, 0.062],
  [-0.245, -0.453, 0.062], [0.245, -0.453, 0.062],
  [-0.49, -0.596, 0.062], [0, -0.596, 0.062], [0.49, -0.596, 0.062],
];

/** Tip at y 1.55, butt at y -3.0: 455.0 mm overall. `radius` is the handle core's half width (33.0 mm). */
export const HANDLE = { radius: 0.165, top: -1.5, length: 1.5 };

/*
 * The canonical handle (render audit section 4.1, kq_canon.py), the same in every still and graphic.
 * The head flows into the handle as one carbon piece: no collar, no joint. About 25 mm of bare woven carbon
 * shows between the frame and the grip.
 */
/** Front view: 47 mm wide at y -146 mm, narrowing (smoothstep) to 33 mm at -176 mm, with an 18 mm concave fillet into the head. */
export const NECK = { top: -1.46, halfTop: 0.235, end: -1.76, halfEnd: 0.165, fillet: 0.18 };
/** Side view: the full 38.0 mm to y -150 mm, tapering (smoothstep) to 29.0 mm at -176 mm. The edge radius grows from here. */
export const NECK_TAPER = { top: -1.5, end: -1.76, thickness: 0.29 };
/** Overgrip: 0.5 mm tape over the 33.0 x 29.0 mm core in a helical wrap (27 mm pitch), an 11 mm finishing band at the top. */
export const GRIP = { top: -1.74, bottom: -2.842, tape: 0.005, pitch: 0.27, band: 0.11 };
/**
 * Satin black anodised butt cap, about 1.5 mm proud of the grip, with one fine groove and an engraved K.
 * `profile`: [scale of the grip's section, y], top to bottom (K05's cap, as kq_canon.cap_profile).
 */
export const CAP = {
  top: -2.817,
  groove: -2.955,
  mark: -2.925,
  profile: [
    [0.89, -2.817], [0.968, -2.822], [0.99, -2.832], [1.035, -2.862], [1.074, -2.887], [1.09, -2.902],
    [1.09, -2.949], [1.074, -2.952], [1.074, -2.958], [1.09, -2.961], [1.09, -2.969], [1.068, -2.983],
    [1.023, -2.992], [0.934, -2.998], [0.668, -3.0],
  ] as Pt[],
};

/** SVG path data for the outline, the throat and every hole (y flipped for SVG). */
export function racketSvgPath(scale = 100, ox = 150, oy = 170): { outline: string; holes: string } {
  const p = ([x, y]: Pt) => `${(ox + x * scale).toFixed(1)} ${(oy - y * scale).toFixed(1)}`;
  const curves = (start: Pt, cs: Cubic[]) =>
    `M${p(start)} ` + cs.map(([a, b, c]) => `C${p(a)} ${p(b)} ${p(c)}`).join(" ") + " Z";
  const holes = HOLES.map(([x, y, hr]) => {
    const [cx, cy] = [ox + x * scale, oy - y * scale];
    const r = hr * scale;
    return `M${(cx - r).toFixed(1)} ${cy.toFixed(1)} a${r.toFixed(1)} ${r.toFixed(1)} 0 1 0 ${(2 * r).toFixed(1)} 0 a${r.toFixed(1)} ${r.toFixed(1)} 0 1 0 ${(-2 * r).toFixed(1)} 0 Z`;
  }).join(" ");
  return { outline: curves(HEAD_START, HEAD_CURVES), holes: `${curves(THROAT_START, THROAT_CURVES)} ${holes}` };
}
