// Pure geometry for G15, the sweet spot: the racket face-on with its face lit to 4 mm from the edge (the K12
// still's lit field, drawn as an SVG). Everything comes from racket-shape.ts. Drawing units are millimetres with
// y up, as in graphics-drawing.ts; the SVG uses them directly (sheet y = -y), so a viewBox is in millimetres.

import { cubicPts, type V, type Xf } from "@/lib/graphics-drawing";
import { EDGE_RADIUS, FACE_INSET, HEAD_CURVES, HEAD_START, THROAT_CURVES, THROAT_START } from "@/lib/racket-shape";

const MM = 100;
/** The SVG transform for G15: drawing mm straight into user units, y flipped. */
export const G15_XF: Xf = { ox: 0, oy: 0, s: 1 };

/** The head outline (mm), clockwise from just right of the top centre. */
const HEAD: V[] = cubicPts(HEAD_START, HEAD_CURVES, 200);

/** The bridge: the top of the throat opening (mm). The face is the head above it. */
export const BRIDGE_Y = Math.max(...cubicPts(THROAT_START, THROAT_CURVES, 200).map((p) => p[1]));

/** How far in from every edge the sweet spot reaches (mm): the flat face, 1.5 mm edge radius plus 2.5 mm. */
export const INSET = FACE_INSET * MM;
/** Where the 1.5 mm edge radius ends and the flat face begins (mm in from the outline). */
const RADIUS = EDGE_RADIUS * MM;

/** The outline offset inward by d (mm), along each point's normal (the head is convex above the bridge). */
function offset(pts: V[], d: number): V[] {
  const N = pts.length;
  return pts.map((p, i) => {
    const a = pts[(i - 1 + N) % N];
    const c = pts[(i + 1) % N];
    const tx = c[0] - a[0];
    const ty = c[1] - a[1];
    const len = Math.hypot(tx, ty) || 1;
    // clockwise with y up: the inward normal is (ty, -tx)
    return [p[0] + (ty / len) * d, p[1] - (tx / len) * d] as V;
  });
}

/** The part of a closed polygon at or above y0 (Sutherland-Hodgman against one horizontal line). */
function clipAbove(poly: V[], y0: number): V[] {
  const out: V[] = [];
  for (let i = 0; i < poly.length; i++) {
    const a = poly[i];
    const b = poly[(i + 1) % poly.length];
    const ina = a[1] >= y0;
    const inb = b[1] >= y0;
    if (ina) out.push(a);
    if (ina !== inb) {
      const k = (y0 - a[1]) / (b[1] - a[1]);
      out.push([a[0] + (b[0] - a[0]) * k, y0]);
    }
  }
  return out;
}

/** Shoelace area (mm²). */
function area(poly: V[]): number {
  let s = 0;
  for (let i = 0; i < poly.length; i++) {
    const [x0, y0] = poly[i];
    const [x1, y1] = poly[(i + 1) % poly.length];
    s += x0 * y1 - x1 * y0;
  }
  return Math.abs(s) / 2;
}

/** The face: the head outline above the bridge (holes included, as Apple counts a display's area). */
export const FACE: V[] = clipAbove(HEAD, BRIDGE_Y);
/** The sweet spot as designed: the face inset 4 mm from the edge and 4 mm above the throat. */
export const FIELD: V[] = clipAbove(offset(HEAD, INSET), BRIDGE_Y + INSET);

/**
 * The claim's numbers, computed (CLAIMS.md row 6b; /lab/g15 prints them beside the copy): the face and the field
 * in cm², the field's share of the face, and the inset in mm. With racket-shape.ts as of 2026-10-22: 531.5 cm²,
 * 498.7 cm², 93.8% (said as "Nearly 94%": SWEET_CLAIM), 4 mm.
 */
export const SWEET = (() => {
  const face = area(FACE) / 100;
  const field = area(FIELD) / 100;
  return { face, field, share: field / face, inset: INSET, bridge: BRIDGE_Y };
})();

/**
 * The claim as the page prints it, built from SWEET so it changes with racket-shape.ts and is never typed by hand
 * (CLAIMS.md row 6b). Rounded the way Apple rounds a display: down to the whole number, or to the next one with
 * "Nearly" (Apple Watch Series 7: "nearly 20 percent"), never up without the word. As of 2026-10-22: 93.8%, said
 * as "Nearly 94%"; 498.7 of 531.5 cm²; 4 mm.
 */
export const SWEET_CLAIM = (() => {
  const pct = SWEET.share * 100;
  const whole = Math.round(pct);
  return {
    /** The lockup's numeral: "94". */
    share: String(whole),
    /** True when the numeral is rounded up, so the lockup reads "Nearly 94%". */
    nearly: whole > pct + 1e-9,
    /** The exact share, for the fine print: "93.8". */
    exact: pct.toFixed(1),
    /** The inset in mm: "4". */
    inset: String(Number(SWEET.inset.toFixed(1))),
    /** The two areas in cm², to one decimal, for the fine print: "498.7" and "531.5". */
    field: SWEET.field.toFixed(1),
    face: SWEET.face.toFixed(1),
  };
})();

/** The sweet spot's centre as drawn (mm): where the light starts to spread, at the centre of the hole field. */
export const SPREAD_CENTRE: V = [0, 25];

const n = (v: number) => (Math.abs(v) < 0.005 ? "0" : String(Number(v.toFixed(2))));

/** A closed polygon in drawing mm as SVG path data. */
export function polyPath(t: Xf, pts: V[]): string {
  return pts.map(([x, y], i) => `${i ? "L" : "M"}${n(t.ox + x * t.s)} ${n(t.oy - y * t.s)}`).join("") + "Z";
}

/**
 * A point on the right side of the outline at height y, with the inward unit normal there: where G15's detail
 * looks at the edge.
 */
export function edgeAt(y: number): { p: V; n: V } {
  for (let i = 1; i < HEAD.length; i++) {
    const a = HEAD[i - 1];
    const b = HEAD[i];
    if (a[0] <= 0 || b[0] <= 0 || (a[1] - y) * (b[1] - y) > 0 || a[1] === b[1]) continue;
    const k = (y - a[1]) / (b[1] - a[1]);
    const tx = b[0] - a[0];
    const ty = b[1] - a[1];
    const len = Math.hypot(tx, ty);
    return { p: [a[0] + tx * k, y], n: [ty / len, -tx / len] };
  }
  throw new Error(`no edge at y ${y}`);
}

export type G15Variant = "wide" | "portrait";

/**
 * G15's two framings (mm, y up): the whole racket with a magnified detail of its edge beside it. Wide: the detail
 * beside the head, at about two o'clock; portrait (phones): beside the handle, looking at the head's lower right.
 * `zoom` is the detail's magnification; the label "4 mm" sits inside the detail (wide) or under it (portrait).
 */
export const G15_FRAMES: Record<
  G15Variant,
  { x0: number; top: number; w: number; h: number; spotY: number; detail: V; r: number; zoom: number; label: "in" | "below" }
> = {
  wide: { x0: -158, top: 172, w: 446, h: 494, spotY: 92, detail: [222, 64], r: 58, zoom: 6, label: "in" },
  portrait: { x0: -150, top: 172, w: 400, h: 494, spotY: -40, detail: [186, -168], r: 52, zoom: 6, label: "below" },
};

/** Everything G15 places for one framing, in SVG user units (mm, y down). */
export function g15Layout(variant: G15Variant) {
  const f = G15_FRAMES[variant];
  const { p, n: nv } = edgeAt(f.spotY);
  // the detail looks at the middle of the 4 mm band
  const look: V = [p[0] + nv[0] * (INSET / 2), p[1] + nv[1] * (INSET / 2)];
  const s = (v: V): V => [v[0], -v[1]];
  const [dcx, dcy] = s(f.detail);
  const [lx, ly] = s(look);
  const ring = f.r / f.zoom;
  // the leader joins the ring on the edge to the detail, between their rims
  const dx = dcx - lx;
  const dy = dcy - ly;
  const len = Math.hypot(dx, dy);
  const ux = dx / len;
  const uy = dy / len;
  const leader = `M${n(lx + ux * ring)} ${n(ly + uy * ring)}L${n(dcx - ux * f.r)} ${n(dcy - uy * f.r)}`;
  // the dimension across the band, through the detail's centre, along the normal (sheet y flips the normal's y)
  const half = (INSET / 2) * f.zoom;
  const nx = nv[0];
  const ny = -nv[1];
  const outer: V = [dcx - nx * half, dcy - ny * half];
  const inner: V = [dcx + nx * half, dcy + ny * half];
  const AL = 4.2; // arrowhead length and half width (sheet mm)
  const AH = 1.3;
  const head = (tip: V, dir: V) =>
    `M${n(tip[0])} ${n(tip[1])}L${n(tip[0] - dir[0] * AL - dir[1] * AH)} ${n(tip[1] - dir[1] * AL + dir[0] * AH)}L${n(tip[0] - dir[0] * AL + dir[1] * AH)} ${n(tip[1] - dir[1] * AL - dir[0] * AH)}Z`;
  const dim = `M${n(outer[0])} ${n(outer[1])}L${n(inner[0])} ${n(inner[1])}`;
  const arrows = head(outer, [-nx, -ny]) + head(inner, [nx, ny]);
  // The extension lines: a short tick along each measured line at the arrow's tips (the 4 mm line and the outline).
  const tx = -ny;
  const ty = nx;
  const EXT = 7;
  const ext = [outer, inner].map((p) => `M${n(p[0] - tx * EXT)} ${n(p[1] - ty * EXT)}L${n(p[0] + tx * EXT)} ${n(p[1] + ty * EXT)}`).join("");
  // the label: inside, out beyond the edge in the dark (wide); or centred under the detail (portrait)
  const labelAt: V =
    f.label === "in" ? [dcx - nx * (half + f.r * 0.42), dcy - ny * (half + f.r * 0.42)] : [dcx, dcy + f.r + 6];
  return {
    viewBox: `${f.x0} ${-f.top} ${f.w} ${f.h}`,
    w: f.w,
    h: f.h,
    /** viewBox point to a percentage of the panel (for HTML labels). */
    pct: ([x, y]: V) => [((x - f.x0) / f.w) * 100, ((y + f.top) / f.h) * 100] as V,
    ring: { c: [lx, ly] as V, r: ring },
    detail: { c: [dcx, dcy] as V, r: f.r },
    transform: `translate(${n(dcx)} ${n(dcy)}) scale(${f.zoom}) translate(${n(-lx)} ${n(-ly)})`,
    leader,
    dim,
    arrows,
    ext,
    lens: lensDetail(look, [dcx, dcy], f.zoom, f.r),
    labelAt,
    labelPlace: f.label,
  };
}

/** The head outline, densely sampled for the magnified detail (at 6x a coarse polygon would show its corners). */
const HEAD_DENSE: V[] = cubicPts(HEAD_START, HEAD_CURVES, 900);

/**
 * G15's magnified detail, drawn as its own vectors at the detail's scale (never the racket scaled up, whose weave and
 * gradients turn to blobs at 6x): the stretch of the edge around `look` (mm, y up) mapped into the detail circle
 * (centre `c` in sheet units). Lines: the outline, where the 1.5 mm edge radius meets the flat face, and the field's
 * 4 mm line. Areas, each closed far inside the circle (the circle clips them): the racket inside its outline, the
 * radius band, and the lit field. `shade` runs across the radius band, from the outline to the flat face, for its
 * gradient (the rounded edge catching the studio's strip light).
 */
function lensDetail(look: V, c: V, zoom: number, r: number) {
  const reach = (r / zoom) * 1.8;
  const N = HEAD_DENSE.length;
  // the contiguous run of outline points near the look point (the head is convex there: one run)
  const idx = HEAD_DENSE.map((p, i) => [i, Math.hypot(p[0] - look[0], p[1] - look[1])] as const).filter(([, d]) => d < reach).map(([i]) => i);
  const run = idx.map((i) => {
    const p = HEAD_DENSE[i];
    const a = HEAD_DENSE[(i - 1 + N) % N];
    const b = HEAD_DENSE[(i + 1) % N];
    const tx = b[0] - a[0];
    const ty = b[1] - a[1];
    const len = Math.hypot(tx, ty) || 1;
    return { p, n: [ty / len, -tx / len] as V };
  });
  const map = ([x, y]: V): V => [c[0] + zoom * (x - look[0]), c[1] - zoom * (y - look[1])];
  const at = (d: number) => run.map(({ p, n: nv }) => map([p[0] + nv[0] * d, p[1] + nv[1] * d]));
  const open = (pts: V[]) => pts.map(([x, y], i) => `${i ? "L" : "M"}${n(x)} ${n(y)}`).join("");
  // close a line toward the inside, far beyond the circle
  const far = reach * 3;
  const inside = (d: number) => {
    const pts = at(d);
    const first = run[0];
    const last = run[run.length - 1];
    const e1 = map([last.p[0] + last.n[0] * far, last.p[1] + last.n[1] * far]);
    const e0 = map([first.p[0] + first.n[0] * far, first.p[1] + first.n[1] * far]);
    return `${open(pts)}L${n(e1[0])} ${n(e1[1])}L${n(e0[0])} ${n(e0[1])}Z`;
  };
  const edge = at(0);
  const flat = at(RADIUS);
  // the normal at the look point, in sheet units (y down)
  const mid = run[Math.floor(run.length / 2)].n;
  const o = map([look[0] - mid[0] * (INSET / 2), look[1] - mid[1] * (INSET / 2)]);
  const f = map([look[0] - mid[0] * (INSET / 2 - RADIUS), look[1] - mid[1] * (INSET / 2 - RADIUS)]);
  return {
    /** the racket inside its outline (the flat band's carbon) */
    body: inside(0),
    /** the 1.5 mm edge radius, between the outline and the flat face */
    radius: `${open(edge)}${open(flat.slice().reverse()).replace(/^M/, "L")}Z`,
    /** the lit field, inside the 4 mm line */
    field: inside(INSET),
    edgeLine: open(edge),
    flatLine: open(flat),
    fieldLine: open(at(INSET)),
    /** the radius band's gradient runs from the outline (o) to where the flat face begins (f) */
    shade: { x1: o[0], y1: o[1], x2: f[0], y2: f[1] },
  };
}
