// G07 section comparison: pure geometry for the two cross-sections through the racket head.
// Units are millimetres, y down. Both sections share one scale and one viewBox, so they always
// read at matching scale. The head is 260 mm wide; the drawing keeps 52 mm at each edge (frame
// or shell edge plus the outermost hole) and shortens the middle with an ISO break zone.
// Deterministic output: server and client render identical path strings.

import { HEAD_CURVES, HOLES, THICKNESS } from "@/lib/racket-shape";

/** The hole nearest the side edge (the crown's lowest pair) and the head's half width at its height. */
const OUTER = HOLES.reduce((a, h) => (h[0] > a[0] ? h : a));
const OUTER_HALF = (() => {
  // the right side of the head above its widest point is the first curve, from the top centre to the side
  const [c1, c2, e] = HEAD_CURVES[0];
  const at = (t: number): [number, number] => {
    const u = 1 - t;
    const f = (j: 0 | 1, p0: number) => u * u * u * p0 + 3 * u * u * t * c1[j] + 3 * u * t * t * c2[j] + t * t * t * e[j];
    return [f(0, 0), f(1, 1.55)];
  };
  let prev = at(0);
  for (let i = 1; i <= 2000; i++) {
    const p = at(i / 2000);
    if ((prev[1] - OUTER[1]) * (p[1] - OUTER[1]) <= 0) return prev[0] + ((p[0] - prev[0]) * (OUTER[1] - prev[1])) / (p[1] - prev[1]);
    prev = p;
  }
  return e[0];
})();

export const T = THICKNESS * 100; // 38 mm
export const SKIN = 2.4; // face skin, drawn a touch thicker than life so it reads at 170 px
export const EDGE_R = 11; // outer edge radius
export const TUBE_W = 20; // frame tube width
export const TUBE_WALL = 2.2;
export const HOLE_R = OUTER[2] * 100; // 7.0 mm, a crown hole
/** Outermost hole centre, from the edge at its height (racket-shape: 124.0 - 91.05 = 32.9 mm). */
export const HOLE_C = Math.round((OUTER_HALF - OUTER[0]) * 1000) / 10;
export const PIECE = 52; // mm kept at each edge
export const BREAK = 8; // break zone between the two pieces
export const W = PIECE * 2 + BREAK; // 112
export const SIDE_WALL = 4.5; // KINETIQ: the shell is thicker at the sides (weight moulded in there)
/** Final drift of the tubular parts, in mm (about 6 px at 1440). */
export const DRIFT = 1.8;

/** The viewBox: drawing plus label bands, the union of both layouts' windows. */
export const VB = { x: -6, y: -41, w: 124, h: 101 };
export const viewBox = `${VB.x} ${VB.y} ${VB.w} ${VB.h}`;
/**
 * Visible windows. Wide containers show the whole section (one label row below); narrow ones
 * (phones, side by side at about 170 px) show one edge only, the tubular left half and the
 * KINETIQ right half, with two label rows in each band.
 */
export const WINDOW = {
  full: { x0: -4, x1: 116, y0: -21.5, y1: 52.8 },
  /** 640 px and wider: the labels take fewer millimetres, so the bands close up. */
  wide: { x0: -4, x1: 116, y0: -16.5, y1: 49.5 },
  /** One edge, sized so 15 px labels still fit at 150 px wide (360 px phones, side by side). */
  tubular: { x0: -6, x1: 60, y0: -41, y1: 60 },
  kinetiq: { x0: 52, x1: 118, y0: -41, y1: 60 },
} as const;

const r1 = (v: number) => (Math.round(v * 100) / 100).toString();
const pt = (x: number, y: number) => `${r1(x)} ${r1(y)}`;

export const holes = [HOLE_C, W - HOLE_C].map((c) => ({ c, l: c - HOLE_R, r: c + HOLE_R }));
export const breakZone = { l: PIECE, r: PIECE + BREAK, c: PIECE + BREAK / 2 };

/** Percent position of a drawing point inside the full (regular) canvas. */
export function pctX(x: number) {
  return `${(((x - VB.x) / VB.w) * 100).toFixed(3)}%`;
}
export function pctY(y: number) {
  return `${(((y - VB.y) / VB.h) * 100).toFixed(3)}%`;
}

/** Rounded rectangle with separate left and right corner radii. */
function rrect(x0: number, y0: number, x1: number, y1: number, rl: number, rr: number) {
  return [
    `M${pt(x0 + rl, y0)}`,
    `H${r1(x1 - rr)}`,
    rr ? `A${r1(rr)} ${r1(rr)} 0 0 1 ${pt(x1, y0 + rr)}` : "",
    `V${r1(y1 - rr)}`,
    rr ? `A${r1(rr)} ${r1(rr)} 0 0 1 ${pt(x1 - rr, y1)}` : "",
    `H${r1(x0 + rl)}`,
    rl ? `A${r1(rl)} ${r1(rl)} 0 0 1 ${pt(x0, y1 - rl)}` : "",
    `V${r1(y0 + rl)}`,
    rl ? `A${r1(rl)} ${r1(rl)} 0 0 1 ${pt(x0 + rl, y0)}` : "",
    "Z",
  ].join("");
}

const rect = (x0: number, y0: number, x1: number, y1: number) => `M${pt(x0, y0)}H${r1(x1)}V${r1(y1)}H${r1(x0)}Z`;

/** Spans of material between the edges and holes (x ranges), from a left and right limit. */
function spans(l: number, r: number) {
  const out: [number, number][] = [];
  let x = l;
  for (const h of holes) {
    out.push([x, h.l]);
    x = h.r;
  }
  out.push([x, r]);
  return out;
}

/** 45 degree ISO hatch lines covering a box (clip them to the section with a clipPath). */
export function hatch(x0: number, y0: number, x1: number, y1: number, gap: number) {
  const step = gap * Math.SQRT2;
  const parts: string[] = [];
  // lines y = -x + c run from bottom-left to top-right
  for (let c = x0 + y0 + step / 2; c < x1 + y1; c += step) {
    const xa = Math.max(x0, c - y1);
    const xb = Math.min(x1, c - y0);
    if (xb <= xa) continue;
    parts.push(`M${pt(xa, c - xa)}L${pt(xb, c - xb)}`);
  }
  return parts.join("");
}

/** A cylinder bore seen beyond the cutting plane: vertical shading lines, denser at the walls. */
function bore(c: number, y0: number, y1: number) {
  return [0.42, 0.7, 0.88, 0.97]
    .flatMap((s) => [c - HOLE_R * s, c + HOLE_R * s])
    .map((x) => `M${pt(x, y0)}V${r1(y1)}`)
    .join("");
}

/** ISO centrelines: the mid-plane and one through each hole (dash-dot, drawn quiet). */
export const centrelines = {
  mid: `M${pt(-3, T / 2)}H${r1(W + 3)}`,
  holes: [HOLE_C, W - HOLE_C].map((c) => `M${pt(c, -4.2)}V${r1(T + 4.2)}`).join(""),
};

/** The bore beyond each cut hole, filled with a cylinder shade. */
export const boreRects = [HOLE_C, W - HOLE_C].map((c) => ({ x: c - HOLE_R, y: 0, w: HOLE_R * 2, h: T }));

// ---------------------------------------------------------------- tubular racket

const coreSpans = spans(TUBE_W, W - TUBE_W);

export const tubular = {
  tube: [0, W - TUBE_W].map((x0, i) => {
    const left = i === 0;
    const outer = rrect(x0, 0, x0 + TUBE_W, T, left ? EDGE_R : 2, left ? 2 : EDGE_R);
    const w = TUBE_WALL;
    const inner = rrect(x0 + w, w, x0 + TUBE_W - w, T - w, left ? EDGE_R - w : 1, left ? 1 : EDGE_R - w);
    return { d: `${outer}${inner}`, drift: [left ? -DRIFT : DRIFT, 0] as const };
  }),
  faces: [
    // The faces stay on the core: both constructions bond a face to a core, so only the frame tube's
    // joints open (CLAIMS.md row 4).
    { y0: 0, y1: SKIN, drift: [0, 0] as const },
    { y0: T - SKIN, y1: T, drift: [0, 0] as const },
  ].map((f) => ({
    d: coreSpans.map(([a, b]) => rect(a, f.y0, b, f.y1)).join(""),
    // the bore beyond the cut: the face's top and bottom edges seen across each hole
    rims: holes.map((h) => `M${pt(h.l, f.y0)}H${r1(h.r)}M${pt(h.l, f.y1)}H${r1(h.r)}`).join(""),
    drift: f.drift,
  })),
  core: coreSpans.map(([a, b]) => rect(a, SKIN, b, T - SKIN)).join(""),
  coreClip: coreSpans.map(([a, b]) => rect(a, SKIN, b, T - SKIN)).join(""),
  bores: holes.map((h) => bore(h.c, 0, T)).join(""),
  /**
   * The frame tube's two joints, each in the middle of the gap the tube drifts open. Face-to-core bonds are
   * not marked: KINETIQ bonds its shell to a core too, so marking them on one side only would be unfair.
   */
  bonds: [
    { id: "left", d: `M${pt(TUBE_W - DRIFT / 2, 0)}V${r1(T)}` },
    { id: "right", d: `M${pt(W - TUBE_W + DRIFT / 2, 0)}V${r1(T)}` },
  ],
};

// ---------------------------------------------------------------- KINETIQ shell

type Seg = { d: string; len: number; end: [number, number] };

/**
 * The shell's outer skin as ONE path, drawn in one unbroken stroke: it starts at the middle of the top face,
 * runs right, wraps the right edge, returns along the bottom, wraps the left edge and comes back along the
 * top. The hole walls are drawn apart and quieter (`walls`), so the only strong line is the unbroken skin.
 * Returns the path and the fraction of its length that completes the right half (phones).
 */
function shellPath() {
  const segs: Seg[] = [];
  let cur: [number, number] = [breakZone.c, 0];
  const line = (x: number, y: number) => {
    segs.push({ d: `L${pt(x, y)}`, len: Math.hypot(x - cur[0], y - cur[1]), end: [x, y] });
    cur = [x, y];
  };
  const arc = (x: number, y: number) => {
    segs.push({ d: `A${EDGE_R} ${EDGE_R} 0 0 1 ${pt(x, y)}`, len: (Math.PI * EDGE_R) / 2, end: [x, y] });
    cur = [x, y];
  };
  // top, rightwards, then the right edge
  line(W - EDGE_R, 0);
  arc(W, EDGE_R);
  line(W, T - EDGE_R);
  arc(W - EDGE_R, T);
  // bottom, leftwards, to the middle: the right half is complete
  const halfIndex = segs.length;
  line(breakZone.c, T);
  // left edge, and back along the top to the start
  line(EDGE_R, T);
  arc(0, T - EDGE_R);
  line(0, EDGE_R);
  arc(EDGE_R, 0);
  line(breakZone.c, 0);

  const total = segs.reduce((s, g) => s + g.len, 0);
  const half = segs.slice(0, halfIndex + 1).reduce((s, g) => s + g.len, 0);
  return { d: `M${pt(breakZone.c, 0)}${segs.map((s) => s.d).join("")}`, halfFraction: half / total };
}

const shell = shellPath();
const innerSpans = spans(SIDE_WALL, W - SIDE_WALL).map(([a, b], i, all) => [
  i === 0 ? a : a + SKIN,
  i === all.length - 1 ? b : b - SKIN,
]) as [number, number][];
const CORE_R = 7;

export const kinetiq = {
  shell: shell.d,
  /** The outer contour only: the glow follows the edge and faces, not the hole walls. */
  contour: rrect(0, 0, W, T, EDGE_R, EDGE_R),
  /** Fraction of the shell path that completes the right half (the phone crop). */
  halfFraction: shell.halfFraction,
  /** The skin lining each hole: the same carbon, drawn as quiet hairlines inside the section. */
  walls: holes.map((h) => `M${pt(h.l, 0)}V${r1(T)}M${pt(h.r, 0)}V${r1(T)}`).join(""),
  coreClip: innerSpans
    .map(([a, b]) => {
      const left = a < 1 + SIDE_WALL;
      const right = b > W - SIDE_WALL - 1;
      return rrect(a, SKIN, b, T - SKIN, left ? CORE_R : 0, right ? CORE_R : 0);
    })
    .join(""),
  bores: holes.map((h) => bore(h.c, 0, T)).join(""),
};

export const hatchBox = hatch(-2, -2, W + 2, T + 2, 2.1);

// ---------------------------------------------------------------- labels

export type Side = "left" | "right" | "centre";
export type Band = "top" | "bottom";
export type Callout = {
  key: string;
  text: string;
  /** Target point on the drawing. */
  at: [number, number];
  /** A second target, led from the same anchor: one label for two features. */
  also?: [number, number];
  /** Shelf point the leader leaves from. */
  anchor: [number, number];
  /** Which end of the label the anchor is, the text running away from it; or its middle ("centre"). */
  side: Side;
  band: Band;
  /** Break onto two balanced lines. */
  wrap?: boolean;
  tone?: "bond" | "part" | "shell";
};

/**
 * Shelf heights (top: text above the shelf; bottom: below). top2 is used only by the one-edge phone
 * layout: it sits a full two-line label above top1, so stacked labels never overlap at 150 px.
 */
export const ROW = { top1: -5.2, top2: -22.5, bottom1: T + 5.2 } as const;

/** Split a callout into two lines of similar length, at a word boundary. */
export function twoLines(text: string): [string, string] {
  const words = text.split(" ");
  let best: [string, string] = [text, ""];
  let score = Infinity;
  for (let i = 1; i < words.length; i++) {
    const a = words.slice(0, i).join(" ");
    const b = words.slice(i).join(" ");
    const d = Math.abs(a.length - b.length);
    if (d < score) {
      score = d;
      best = [a, b];
    }
  }
  return best;
}
