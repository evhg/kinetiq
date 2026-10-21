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
  /** Dimension lines (viewBox units): from, to, and the label between. */
  dims: { key: "length" | "width"; from: [number, number]; to: [number, number]; text: string }[];
  /** Caption box: left, top and width in viewBox units. */
  caption: { x: number; y: number; w: number };
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
    caption: { x: 7.45, y: 13.75, w: 18.5 },
    marker: { u: 1.45, v: 6.7 },
  },
  "4:5": {
    vb: { w: 24, h: 30 },
    map: (u, v) => [7 + v, 3 + u],
    dims: [
      { key: "width", from: [7, 1.55], to: [17, 1.55], text: "10 m" },
      { key: "length", from: [5.25, 3], to: [5.25, 23], text: "20 m" },
    ],
    caption: { x: 9.4, y: 24.7, w: 13.4 },
    marker: { u: 18.55, v: 2.4 },
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

/** A dimension line with a gap for its label and end ticks perpendicular to it. */
export function dimPath(from: [number, number], to: [number, number], gap = 3.6, tick = 0.5) {
  const [x0, y0] = from;
  const [x1, y1] = to;
  const len = Math.hypot(x1 - x0, y1 - y0);
  const ux = (x1 - x0) / len;
  const uy = (y1 - y0) / len;
  const cx = (x0 + x1) / 2;
  const cy = (y0 + y1) / 2;
  const a: [number, number] = [cx - (ux * gap) / 2, cy - (uy * gap) / 2];
  const b: [number, number] = [cx + (ux * gap) / 2, cy + (uy * gap) / 2];
  const t = (x: number, y: number) => `M${r2(x - uy * tick)} ${r2(y + ux * tick)}L${r2(x + uy * tick)} ${r2(y - ux * tick)}`;
  return {
    d: `M${r2(x0)} ${r2(y0)}L${r2(a[0])} ${r2(a[1])}M${r2(b[0])} ${r2(b[1])}L${r2(x1)} ${r2(y1)}${t(x0, y0)}${t(x1, y1)}`,
    at: [cx, cy] as [number, number],
    vertical: Math.abs(uy) > Math.abs(ux),
  };
}
