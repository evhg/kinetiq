// G17 "After the bounce" (owner, 2026-11-02): one sliced shot, seen from above the side of the court, and what the
// ball does after it lands, off a standard face and off the KINETIQ face. Pure geometry: a small 3D scene in metres
// (u along the court from the net, w across it, y up), projected through a pinhole camera into the SVG's viewBox.
// Deterministic, so the server and the client draw the same paths.
//
// The physics, kept plausible rather than measured (CLAIMS.md row 49): a slice carries backspin and some sidespin.
// In the air the sidespin curves the ball a little (Magnus). On the bounce, a ball with more spin skids, stays low and
// kicks off line in the direction of its sidespin; a ball with less spin bounces up and runs on close to its line. The
// standard ball's exit: about 8 degrees off its line, rising to 0.95 m. KINETIQ's: about 34 degrees off, rising to
// 0.32 m. A padel ball is 6.5 cm across; it is drawn about four times larger so it reads at phone size.

export type Vec3 = { u: number; w: number; y: number };
type Pt = { x: number; y: number; s: number };

export type SliceView = {
  /** The SVG viewBox width and height. */
  vw: number;
  vh: number;
  /** The camera: its position and the point it looks at, in metres, and its focal length in viewBox units. */
  eye: Vec3;
  at: Vec3;
  focal: number;
  /** Where the look-at point lands in the viewBox (0..1 of the width and height). */
  cx: number;
  cy: number;
};

/** The wide framing (from 700 px) and the portrait one (phones), the same scene from two cameras. */
export const VIEWS: Record<"wide" | "portrait", SliceView> = {
  wide: { vw: 1600, vh: 760, eye: { u: 3.6, w: -8.6, y: 5.6 }, at: { u: 5.2, w: 4.2, y: 0.5 }, focal: 1700, cx: 0.52, cy: 0.5 },
  portrait: { vw: 800, vh: 660, eye: { u: 4.8, w: -7.6, y: 6.6 }, at: { u: 6.6, w: 3.4, y: 0.35 }, focal: 1500, cx: 0.5, cy: 0.4 },
};

function sub(a: Vec3, b: Vec3): Vec3 {
  return { u: a.u - b.u, w: a.w - b.w, y: a.y - b.y };
}
function dot(a: Vec3, b: Vec3) {
  return a.u * b.u + a.w * b.w + a.y * b.y;
}
function cross(a: Vec3, b: Vec3): Vec3 {
  // right-handed in (u, w, y)
  return { u: a.w * b.y - a.y * b.w, w: a.y * b.u - a.u * b.y, y: a.u * b.w - a.w * b.u };
}
function norm(a: Vec3): Vec3 {
  const l = Math.hypot(a.u, a.w, a.y);
  return { u: a.u / l, w: a.w / l, y: a.y / l };
}

/** A projector for one view: metres in, viewBox units out (and the scale at that depth, for the ball's radius). */
export function projector(v: SliceView) {
  const fwd = norm(sub(v.at, v.eye));
  const up0: Vec3 = { u: 0, w: 0, y: 1 };
  let right = norm(cross(fwd, up0));
  // keep +u running left to right on screen
  if (right.u < 0) right = { u: -right.u, w: -right.w, y: -right.y };
  const up = norm(cross(right, fwd));
  const upFixed = up.y < 0 ? { u: -up.u, w: -up.w, y: -up.y } : up;
  return (p: Vec3): Pt => {
    const d = sub(p, v.eye);
    const z = dot(d, fwd);
    const s = v.focal / z;
    return { x: v.vw * v.cx + dot(d, right) * s, y: v.vh * v.cy - dot(d, upFixed) * s, s };
  };
}

const r1 = (n: number) => Math.round(n * 10) / 10;

/** A polyline through projected points as an SVG path. */
function path(pts: Pt[]) {
  return pts.map((p, i) => `${i ? "L" : "M"}${r1(p.x)} ${r1(p.y)}`).join("");
}

// ---- The shot -----------------------------------------------------------------------------------------------------

/** Where the ball lands (metres): past the service line, left of centre. */
export const BOUNCE: Vec3 = { u: 5.4, w: 4.0, y: 0 };
/** Where the slice was struck, on the far side of the net. */
const HIT: Vec3 = { u: -4.6, w: 7.2, y: 1.15 };

/** The flight in: a low arc over the net, curving a little with its sidespin. */
function flight(t: number): Vec3 {
  const u = HIT.u + (BOUNCE.u - HIT.u) * t;
  // straight line across, plus a gentle sideways curve (Magnus), zero at both ends
  const w = HIT.w + (BOUNCE.w - HIT.w) * t - 0.55 * t * (1 - t);
  // a parabola from the contact height down to the floor, apex about 1.75 m just before the net
  const y = HIT.y * (1 - t) + 2.6 * t * (1 - t) * (1 - 0.25 * t);
  return { u, w, y };
}

/** After the bounce: along a direction turned `turn` degrees from the incoming line (towards the camera's side). */
function exit(turn: number, length: number, apex: number, run: number) {
  const a = flight(0.98);
  const b = flight(1);
  const dir = Math.atan2(b.w - a.w, b.u - a.u) - (turn * Math.PI) / 180;
  return (t: number): Vec3 => {
    // ease the turn in over the first few centimetres, so the kick reads as the bounce's, not a corner
    const d = length * t;
    return {
      u: BOUNCE.u + Math.cos(dir) * d,
      w: BOUNCE.w + Math.sin(dir) * d,
      // a bounce arc: up to the apex, then down again by the end of `run` of the path
      y: apex * Math.sin(Math.min(1, t / run) * Math.PI) * (t <= run ? 1 : 0),
    };
  };
}

export const STANDARD = { turn: 8, length: 3.8, apex: 1.0, run: 1.35 };
export const KINETIQ = { turn: 36, length: 3.0, apex: 0.3, run: 0.8 };
const standardExit = exit(STANDARD.turn, STANDARD.length, STANDARD.apex, STANDARD.run);
const kinetiqExit = exit(KINETIQ.turn, KINETIQ.length, KINETIQ.apex, KINETIQ.run);

const N = 48;
const samples = (f: (t: number) => Vec3, n = N) => Array.from({ length: n + 1 }, (_, i) => f(i / n));
const floor = (p: Vec3): Vec3 => ({ ...p, y: 0 });

// ---- The court ----------------------------------------------------------------------------------------------------

/** The receiving half of a padel court, 10 x 10 m: net at u = 0, back wall at u = 10, service line at 6.95 m. */
const COURT = { len: 10, wide: 10, service: 6.95, net: 0.88, back: 3 };

export type SliceScene = {
  vw: number;
  vh: number;
  /** Court: the floor's outline, the lines on it, the net, the back wall's glass (as faint outlines). */
  floor: string;
  lines: string;
  net: string;
  glass: string;
  /** The flight in (and its shadow), then each exit (and its shadow). */
  flight: string;
  flightShadow: string;
  standard: string;
  standardShadow: string;
  kinetiq: string;
  kinetiqShadow: string;
  /** Projected points along each path, for the moving balls: x, y and the ball's radius there. */
  flightPts: { x: number; y: number; r: number }[];
  standardPts: { x: number; y: number; r: number }[];
  kinetiqPts: { x: number; y: number; r: number }[];
  /** The bounce point and the label anchors, as fractions of the viewBox (HTML labels sit at these). */
  bounce: { x: number; y: number; rx: number; ry: number };
  anchors: { standard: { x: number; y: number }; kinetiq: { x: number; y: number }; bounce: { x: number; y: number } };
};

/** Ball radius in metres, drawn about four times its size. */
const BALL = 0.033 * 4;

export function sliceScene(view: keyof typeof VIEWS): SliceScene {
  const v = VIEWS[view];
  const P = projector(v);
  const pts = (list: Vec3[]) => list.map(P);
  const ball = (list: Vec3[]) =>
    list.map((p) => {
      const q = P({ ...p, y: p.y + BALL });
      return { x: r1(q.x), y: r1(q.y), r: r1(BALL * q.s) };
    });

  const corners: Vec3[] = [
    { u: 0, w: 0, y: 0 },
    { u: COURT.len, w: 0, y: 0 },
    { u: COURT.len, w: COURT.wide, y: 0 },
    { u: 0, w: COURT.wide, y: 0 },
  ];
  const floorPath = `${path(pts(corners))}Z`;
  const line = (a: Vec3, b: Vec3) => path(pts([a, b]));
  const lines = [
    line({ u: COURT.service, w: 0, y: 0 }, { u: COURT.service, w: COURT.wide, y: 0 }),
    line({ u: 0, w: COURT.wide / 2, y: 0 }, { u: COURT.service, w: COURT.wide / 2, y: 0 }),
  ].join("");
  const net = [
    line({ u: 0, w: 0, y: COURT.net }, { u: 0, w: COURT.wide, y: COURT.net }),
    line({ u: 0, w: 0, y: 0 }, { u: 0, w: 0, y: COURT.net }),
    line({ u: 0, w: COURT.wide, y: 0 }, { u: 0, w: COURT.wide, y: COURT.net }),
  ].join("");
  const glass = [
    `${path(pts([
      { u: COURT.len, w: 0, y: 0 },
      { u: COURT.len, w: 0, y: COURT.back },
      { u: COURT.len, w: COURT.wide, y: COURT.back },
      { u: COURT.len, w: COURT.wide, y: 0 },
    ]))}`,
    // the far side wall's glass, its last 4 m
    path(pts([
      { u: COURT.len - 4, w: COURT.wide, y: 0 },
      { u: COURT.len - 4, w: COURT.wide, y: COURT.back },
      { u: COURT.len, w: COURT.wide, y: COURT.back },
    ])),
  ].join("");

  // the flight starts where it crosses into the frame's court: from just before the net
  const flightFrom = 0.3;
  const flightList = samples((t) => flight(flightFrom + (1 - flightFrom) * t));
  const stdList = samples(standardExit);
  const kqList = samples(kinetiqExit);

  const b = P(BOUNCE);
  const end = (list: Vec3[]) => P({ ...list[list.length - 1], y: list[list.length - 1].y + BALL });
  const sEnd = end(stdList);
  const kEnd = end(kqList);
  return {
    vw: v.vw,
    vh: v.vh,
    floor: floorPath,
    lines,
    net,
    glass,
    flight: path(pts(flightList)),
    flightShadow: path(pts(flightList.map(floor))),
    standard: path(pts(stdList)),
    standardShadow: path(pts(stdList.map(floor))),
    kinetiq: path(pts(kqList)),
    kinetiqShadow: path(pts(kqList.map(floor))),
    flightPts: ball(flightList),
    standardPts: ball(stdList),
    kinetiqPts: ball(kqList),
    bounce: { x: r1(b.x), y: r1(b.y), rx: r1(0.34 * b.s), ry: r1(0.12 * b.s) },
    anchors: {
      standard: { x: sEnd.x / v.vw, y: sEnd.y / v.vh },
      kinetiq: { x: kEnd.x / v.vw, y: kEnd.y / v.vh },
      bounce: { x: b.x / v.vw, y: b.y / v.vh },
    },
  };
}
