// G12 coaching court plan: a top-down padel court, 20 x 10 m, in metres.
// Court-local coordinates: u along the length (0..20, back wall to back wall), v across (0..10).
// Two slide layouts map them into a viewBox: landscape (16:10, u to x) and portrait (4:5, u to y).

export type Aspect = "16:10" | "4:5";

export const LENGTH = 20;
export const WIDTH = 10;
export const SERVICE = 6.95; // service line, from the net
export const CENTRE_EXT = 0.2; // the centre service line runs 200 mm past each service line
export const WALL = 0.16; // drawn wall thickness (double line)
export const SIDE_GLASS = 4; // glass along each side from the back wall; mesh in between
export const PANEL = 2; // glass and mesh panels are 2 m wide


type Layout = {
  vb: { w: number; h: number };
  /** Court origin and orientation in the viewBox. */
  map: (u: number, v: number) => [number, number];
  /** Dimension lines (viewBox units): from, to, and the label between. Drawn in HTML, so the gap fits the label. */
  dims: { key: "length" | "width"; from: [number, number]; to: [number, number]; text: string }[];
  /** Caption box: left, top and width in viewBox units. */
  caption: { x: number; y: number; w: number };
  /**
   * Downward shift of the whole composition, in percent of the slide height. CourtPlan.module.css applies
   * it only on wide slides (16:10 from 560 px, 4:5 from 600 px), where the caption is short enough
   * that the drawing can sit centred instead of top-heavy.
   */
  shift: number;
  /** One player position at the back of the court, near the back glass, on the caption's side. */
  marker: { u: number; v: number };
};

const r2 = (v: number) => (Math.round(v * 100) / 100).toString();

export const LAYOUT: Record<Aspect, Layout> = {
  "16:10": {
    vb: { w: 32, h: 20 },
    map: (u, v) => [6 + u, 2.55 + v],
    dims: [
      { key: "length", from: [6, 1.2], to: [26, 1.2], text: "20 m" },
      { key: "width", from: [27.75, 2.55], to: [27.75, 12.55], text: "10 m" },
    ],
    caption: { x: 7.45, y: 13.6, w: 22.5 },
    marker: { u: 1.45, v: 6.7 },
    shift: 6.5,
  },
  "4:5": {
    vb: { w: 24, h: 30 },
    map: (u, v) => [7 + v, 3 + u],
    dims: [
      { key: "width", from: [7, 1.55], to: [17, 1.55], text: "10 m" },
      { key: "length", from: [5.25, 3], to: [5.25, 23], text: "20 m" },
    ],
    caption: { x: 9.4, y: 24.45, w: 14.2 },
    marker: { u: 18.55, v: 2.4 },
    shift: 2.5,
  },
};

/** All plan paths for one layout. */
export function courtPaths(aspect: Aspect) {
  const { map } = LAYOUT[aspect];
  const P = (u: number, v: number) => {
    const [x, y] = map(u, v);
    return `${r2(x)} ${r2(y)}`;
  };
  const line = (u0: number, v0: number, u1: number, v1: number) => `M${P(u0, v0)}L${P(u1, v1)}`;
  const rect = (u0: number, v0: number, u1: number, v1: number) => `M${P(u0, v0)}L${P(u1, v0)}L${P(u1, v1)}L${P(u0, v1)}Z`;

  // glass: back walls and the first 4 m of each side, as double lines
  const glass = [
    line(0, 0, 0, WIDTH),
    line(-WALL, -WALL, -WALL, WIDTH + WALL),
    line(LENGTH, 0, LENGTH, WIDTH),
    line(LENGTH + WALL, -WALL, LENGTH + WALL, WIDTH + WALL),
    ...[0, WIDTH].flatMap((v) => {
      const o = v === 0 ? -WALL : WALL;
      return [
        line(0, v, SIDE_GLASS, v),
        line(-WALL, v + o, SIDE_GLASS, v + o),
        line(LENGTH - SIDE_GLASS, v, LENGTH, v),
        line(LENGTH - SIDE_GLASS, v + o, LENGTH + WALL, v + o),
      ];
    }),
  ].join("");

  // mesh: the middle 12 m of each side; outer line solid, inner line dotted (CSS)
  const meshOuter = [0, WIDTH].map((v) => line(SIDE_GLASS, v + (v === 0 ? -WALL : WALL), LENGTH - SIDE_GLASS, v + (v === 0 ? -WALL : WALL))).join("");
  const meshInner = [0, WIDTH].map((v) => line(SIDE_GLASS, v, LENGTH - SIDE_GLASS, v)).join("");

  // posts every 2 m along the sides and the back walls (panel joints)
  const s = 0.11;
  const posts: string[] = [];
  for (let u = 0; u <= LENGTH; u += PANEL) {
    for (const v of [-WALL / 2, WIDTH + WALL / 2]) posts.push(rect(u - s, v - s, u + s, v + s));
  }
  for (let v = PANEL; v < WIDTH; v += PANEL) {
    for (const u of [-WALL / 2, LENGTH + WALL / 2]) posts.push(rect(u - s, v - s, u + s, v + s));
  }

  const lines = [
    line(LENGTH / 2 - SERVICE, 0, LENGTH / 2 - SERVICE, WIDTH),
    line(LENGTH / 2 + SERVICE, 0, LENGTH / 2 + SERVICE, WIDTH),
    line(LENGTH / 2 - SERVICE - CENTRE_EXT, WIDTH / 2, LENGTH / 2 + SERVICE + CENTRE_EXT, WIDTH / 2),
  ].join("");

  const net = line(LENGTH / 2, -WALL - 0.12, LENGTH / 2, WIDTH + WALL + 0.12);
  const netPosts = [rect(LENGTH / 2 - 0.16, -WALL - 0.3, LENGTH / 2 + 0.16, -WALL + 0.02), rect(LENGTH / 2 - 0.16, WIDTH + WALL - 0.02, LENGTH / 2 + 0.16, WIDTH + WALL + 0.3)].join("");

  const surface = rect(0, 0, LENGTH, WIDTH);
  const { caption, marker } = LAYOUT[aspect];
  const [mx, my] = map(marker.u, marker.v);
  // leader from the marker straight down to the caption shelf
  const leader = `M${r2(mx)} ${r2(my + 0.75)}V${r2(caption.y)}`;

  return { glass, meshOuter, meshInner, posts: posts.join(""), lines, net, netPosts, surface, marker: { x: mx, y: my }, leader };
}

/** Placement of an HTML dimension line, in percent of the slide: axis, start and length. */
export function dimBox(aspect: Aspect, from: [number, number], to: [number, number]) {
  const { w, h } = LAYOUT[aspect].vb;
  const pc = (v: number) => `${(v * 100).toFixed(3)}%`;
  const vertical = Math.abs(to[1] - from[1]) > Math.abs(to[0] - from[0]);
  const x0 = Math.min(from[0], to[0]);
  const y0 = Math.min(from[1], to[1]);
  return vertical
    ? { vertical, x: pc(x0 / w), y: pc(y0 / h), len: pc(Math.abs(to[1] - from[1]) / h) }
    : { vertical, x: pc(x0 / w), y: pc(y0 / h), len: pc(Math.abs(to[0] - from[0]) / w) };
}
