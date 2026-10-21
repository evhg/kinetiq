"use client";

import { useId, useMemo, useRef, type ReactNode } from "react";
import { gsap, useGSAP } from "@/lib/gsap";
import { useMotion } from "@/components/motion/MotionProvider";
import {
  BORE,
  CUT_Y,
  DIM,
  HEAD_MAX,
  HEAD_W,
  LIP_R,
  arrow,
  at,
  boreFibres,
  boreSection,
  circle,
  headHalfWidth,
  holes,
  line,
  poly,
  slabFibres,
  slabSection,
  sideHalf,
  sideHidden,
  sideProfile,
  silhouette,
  tangentEdge,
  throat,
  type V,
  type Xf,
} from "@/lib/graphics-drawing";
import styles from "./TechnicalDrawing.module.css";

/** New strings used by G01 (not yet in copy.ts). Claims restate existing copy (CLAIMS.md rows). */
export const LABELS = {
  summary:
    "Technical drawing of the KINETIQ racket. Overall length 455 mm, head width 260 mm, thickness 38.0 mm, 42 moulded holes of 12.4 mm diameter, every surface within plus or minus 0.015 mm. Section A-A shows one continuous shell around the core; section B-B shows the shell running unbroken down the wall of a moulded hole.",
  holeNote: "0 drilled",
  shell: "One shell. No tube.",
  core: "Core",
  fibre: ["Fibre continuous", "around the edge"],
  weave: ["One weave,", "face to edge"],
  flows: ["Every fibre", "flows around it"],
  sectionTitle: "Section A-A",
  sectionScale: "Scale 1:2",
  detailTitle: "Section B-B",
  detailScale: "Scale 2:1",
  notesTitle: "Notes",
  notes: [
    "One piece, from a single mould.",
    "No frame tube. No seam. No joint.",
    "42 holes moulded. 0 drilled.",
    "Every surface within ±0.015 of design.",
    "Mass within ±1.0 g of reference.",
    "Balance within ±1.0 mm, set in the mould.",
  ],
  balance: "Balance ±1.0 mm",
  balanceSub: "set in the mould",
  title: "KINETIQ",
  titleSub: "One-piece padel racket",
  titleCap: "Title",
  /** Title-block cells, each in its own grid area (see .cells in the CSS module). */
  cells: [
    ["dwg", "DWG", "K-01"],
    ["rev", "Rev", "A"],
    ["scale", "Scale", "1:4"],
    ["units", "Units", "mm"],
    ["tol", "Tolerance", "±0.015"],
    ["sheet", "Sheet", "1 of 1"],
  ] as [string, string, string][],
  projection: "Projection",
};

type Layer = "outline" | "hidden" | "dims" | "values";
type Kind =
  | "vis"
  | "hole"
  | "tangent"
  | "hidden"
  | "centre"
  | "construct"
  | "dim"
  | "dimFill"
  | "shell"
  | "core"
  | "fibre"
  | "cut"
  | "cutThick"
  | "ring"
  | "bar"
  | "barFill"
  | "dot"
  | "cgDisc"
  | "cgRing"
  | "cgFill";
type Prim = { layer: Layer; kind: Kind; d: string; clip?: string };
type Place = "n" | "s" | "e" | "w" | "c" | "vl" | "vr" | "se" | "sw";
type LabelKind = "dim" | "note" | "muted" | "title" | "letter";
type Lab = { x: number; y: number; place: Place; kind: LabelKind; lines: ReactNode[] };

// Dimension furniture, in sheet units.
const AL = 7;
const AH = 1.25;
const GAP = 3;
const OVER = 4;

class Draft {
  prims: Prim[] = [];
  labels: Lab[] = [];
  clips: { id: string; d: string }[] = [];
  constructor(
    public w: number,
    public h: number,
    public uid: string,
  ) {}
  add(layer: Layer, kind: Kind, d: string, clip?: string) {
    this.prims.push({ layer, kind, d, clip });
  }
  label(x: number, y: number, place: Place, kind: LabelKind, ...lines: ReactNode[]) {
    this.labels.push({ x, y, place, kind, lines });
  }
}

/** Vertical dimension: features a (top) and b (bottom), dimension line at sheet x. */
function dimV(D: Draft, a: V, b: V, x: number, text: string) {
  for (const p of [a, b]) {
    const dir = Math.sign(x - p[0]) || -1;
    D.add("dims", "dim", line([p[0] + dir * GAP, p[1]], [x + dir * OVER, p[1]]));
  }
  D.add("dims", "dim", line([x, a[1]], [x, b[1]]));
  D.add("dims", "dimFill", arrow([x, a[1]], [x, a[1] + 10], AL, AH) + arrow([x, b[1]], [x, b[1] - 10], AL, AH));
  const left = x < a[0];
  D.label(x, (a[1] + b[1]) / 2, left ? "vl" : "vr", "dim", text);
}

/** Horizontal dimension between features a (left) and b (right), dimension line at sheet y. */
function dimH(D: Draft, a: V, b: V, y: number, text: ReactNode, o: { outside?: boolean; ext?: boolean; place?: Place } = {}) {
  if (o.ext !== false) {
    for (const p of [a, b]) {
      const dir = Math.sign(y - p[1]) || -1;
      D.add("dims", "dim", line([p[0], p[1] + dir * GAP], [p[0], y + dir * OVER]));
    }
  }
  if (o.outside) {
    D.add("dims", "dim", line([a[0] - 16, y], [b[0] + 16, y]));
    D.add("dims", "dimFill", arrow([a[0], y], [a[0] - 10, y], AL, AH) + arrow([b[0], y], [b[0] + 10, y], AL, AH));
  } else {
    D.add("dims", "dim", line([a[0], y], [b[0], y]));
    D.add("dims", "dimFill", arrow([a[0], y], [a[0] + 10, y], AL, AH) + arrow([b[0], y], [b[0] - 10, y], AL, AH));
  }
  D.label((a[0] + b[0]) / 2, y, o.place ?? "n", "dim", text);
}

/** Leader from a feature (tip) through an elbow to a short landing; the text sits at the landing end. */
function leader(D: Draft, tip: V, elbow: V, land: number, kind: LabelKind, lines: ReactNode[], term: "arrow" | "dot" = "arrow") {
  const end: V = [elbow[0] + land, elbow[1]];
  D.add("dims", "dim", poly([tip, elbow, end]));
  if (term === "arrow") D.add("dims", "dimFill", arrow(tip, elbow, AL, AH));
  else D.add("dims", "dimFill", circle({ ox: tip[0], oy: tip[1], s: 1 }, [0, 0], 1.7));
  D.label(end[0], end[1], land >= 0 ? "e" : "w", kind, ...lines);
}

/**
 * The engineering diameter sign, drawn: Saira's Ø reads as a zero at label sizes. Sized in em so
 * it tracks the label; the stroke matches Saira's regular stem.
 */
function Dia() {
  return (
    <svg className={styles.dia} viewBox="0 0 12 12" aria-hidden="true" focusable="false">
      <circle cx="6" cy="6" r="4.5" />
      <path d="M1.3 10.7 L10.7 1.3" />
    </svg>
  );
}

/** ISO centre-of-gravity mark: a ring with two opposite quadrants filled, over a masking disc. */
function cgMark(D: Draft, t: Xf, c: V, r: number) {
  const [cx, cy] = at(t, c);
  const R = r * t.s;
  D.add("dims", "cgDisc", circle(t, c, r));
  D.add("dims", "cgFill", `M${cx} ${cy}V${cy - R}A${R} ${R} 0 0 1 ${cx + R} ${cy}Z M${cx} ${cy}V${cy + R}A${R} ${R} 0 0 1 ${cx - R} ${cy}Z`);
  D.add("dims", "cgRing", circle(t, c, r));
}

type FrontOpts = { dims?: boolean; cut?: boolean; callout?: boolean };

/** ISO cutting plane: thin chain, thick ends, arrows in the direction of view, a letter at each arrow. */
function cutPlane(D: Draft, t: Xf, y: number, x0: number, x1: number, end: number, letter: string, drop = 17) {
  D.add("hidden", "cut", line(at(t, [x0, y]), at(t, [x1, y])));
  D.add("hidden", "cutThick", line(at(t, [x0, y]), at(t, [x0 + end, y])) + line(at(t, [x1 - end, y]), at(t, [x1, y])));
  for (const x of [x0 + 4, x1 - 4]) {
    const base = at(t, [x, y]);
    const tip = at(t, [x, y - drop]);
    D.add("hidden", "cut", line(base, [tip[0], tip[1] - 3]));
    D.add("dims", "dimFill", arrow(tip, base, AL * 1.25, AH * 1.4));
    D.label(tip[0], tip[1] + 1, "s", "letter", letter);
  }
}

function frontView(D: Draft, t: Xf, o: FrontOpts = {}) {
  const top = DIM.headTop;
  const butt = DIM.buttY;
  D.add("outline", "vis", silhouette(t));
  D.add("outline", "vis", throat(t));
  D.add("outline", "hole", holes(t));
  D.add("outline", "tangent", tangentEdge(t, 13));
  D.add("hidden", "centre", line(at(t, [0, top + 16]), at(t, [0, butt - 16])));
  if (o.cut) {
    // both planes run clear across the head, so every letter sits outside the outline
    const wa = Math.round(headHalfWidth(CUT_Y) + 28);
    const wb = Math.round(headHalfWidth(BORE[1]) + 28);
    cutPlane(D, t, CUT_Y, -wa, wa, 13, "A");
    cutPlane(D, t, BORE[1], -wb, wb, 13, "B");
  }
  if (o.dims) {
    dimV(D, at(t, [0, top]), at(t, [-DIM.handleR - 1.6, butt]), at(t, [-174, 0])[0], String(DIM.length));
    dimH(D, at(t, [-HEAD_MAX[0], HEAD_MAX[1]]), at(t, [HEAD_MAX[0], HEAD_MAX[1]]), at(t, [0, top + 32])[1], String(DIM.width));
  }
  if (o.callout) {
    const hole: V = [40.5, -40.5];
    const a = (-62 * Math.PI) / 180;
    const tip = at(t, [hole[0] + Math.cos(a) * (DIM.holeD / 2), hole[1] + Math.sin(a) * (DIM.holeD / 2)]);
    leader(D, tip, at(t, [72, -197]), 9, "dim", [
      <span key="a">
        <Dia />
        {DIM.holeD.toFixed(1)} <span className={styles.times}>×{DIM.holes}</span>
      </span>,
      <span key="b" className={styles.subline}>
        {LABELS.holeNote}
      </span>,
    ]);
  }
}

function sideView(D: Draft, t: Xf, o: { dims?: boolean; balance?: boolean } = {}) {
  const h = DIM.thickness / 2;
  D.add("outline", "vis", sideProfile(t));
  D.add("hidden", "hidden", sideHidden(t));
  D.add("hidden", "centre", line(at(t, [0, DIM.headTop + 16]), at(t, [0, DIM.buttY - 16])));
  if (o.dims) {
    dimH(D, at(t, [-h, DIM.headTop - 7]), at(t, [h, DIM.headTop - 7]), at(t, [0, DIM.headTop + 32])[1], DIM.thickness.toFixed(1), {
      outside: true,
    });
  }
  if (o.balance) {
    // the balance point on the centreline, with its tolerance (the position itself is never printed)
    const r = 5;
    const c: V = [0, DIM.buttY + DIM.balance];
    cgMark(D, t, c, r);
    const tip = at(t, [r * 0.7071, c[1] + r * 0.7071]);
    leader(D, tip, [tip[0] + 44, tip[1] - 34], 9, "dim", [
      LABELS.balance,
      <span key="s" className={styles.subline}>
        {LABELS.balanceSub}
      </span>,
    ]);
  }
}

/** Thin projection lines that tie the front view to the side view. */
function projection(D: Draft, f: Xf, s: Xf) {
  const rows: [number, number, number][] = [
    [DIM.headTop, 5, sideHalf(DIM.headTop) - 2],
    [-86.5, headHalfWidth(-86.5) + 5, sideHalf(-86.5) + 5],
    [-127, headHalfWidth(-127) + 5, sideHalf(-127) + 5],
    [DIM.buttY, DIM.handleR + 6, DIM.handleR + 6],
  ];
  for (const [y, fx, sx] of rows) D.add("hidden", "construct", line(at(f, [fx, y]), at(s, [-sx, y])));
}

type SectionCallouts = "wide" | "narrow";

function sectionView(D: Draft, t: Xf, o: { callouts: SectionCallouts }) {
  const h = DIM.thickness / 2;
  const W = HEAD_W;
  const p = slabSection(t);
  D.add("outline", "shell", `${p.outer} ${p.core}`);
  D.add("outline", "core", p.core);
  D.add("outline", "fibre", slabFibres(t));
  D.add("hidden", "centre", line(at(t, [-W - 10, 0]), at(t, [W + 10, 0])));
  D.add("hidden", "centre", line(at(t, [0, h + 9]), at(t, [0, -h - 9])));
  // tips: the shell on the top face, the core, and the wrapped rim
  const shellTip = at(t, [-96, h - 1]);
  const coreTip = at(t, [92, -3]);
  const k = 0.7071;
  const rimTip = at(t, [W - 15 + 15 * k, h - 15 + 15 * k]);
  const top = at(t, [0, h])[1];
  const bot = at(t, [0, -h])[1];
  if (o.callouts === "wide") {
    leader(D, shellTip, [shellTip[0] + 16, top - 50], 10, "note", [LABELS.shell], "dot");
    leader(D, rimTip, [rimTip[0] - 4, top - 50], -10, "note", LABELS.fibre);
    leader(D, coreTip, [coreTip[0] + 14, bot + 34], 10, "note", [LABELS.core], "dot");
  } else {
    leader(D, at(t, [-96, -h + 1]), [at(t, [-96, 0])[0] + 10, bot + 24], 8, "note", [LABELS.shell], "dot");
    leader(D, at(t, [W - 15 + 15 * k, -h + 15 - 15 * k]), [at(t, [W, 0])[0] - 6, bot + 66], -8, "note", LABELS.fibre);
    leader(D, at(t, [92, 3]), [at(t, [92, 0])[0] + 8, top - 22], 8, "note", [LABELS.core], "dot");
  }
}

/** Section B-B: a partial section through one moulded hole, bounded by a circle. */
function boreView(D: Draft, t: Xf, o: { callouts: "flank" | "right"; R?: number }) {
  const h = DIM.thickness / 2;
  const r = DIM.holeD / 2;
  const R = o.R ?? 14;
  const clip = `${D.uid}-clip`;
  D.clips.push({ id: clip, d: circle(t, [0, h], R) });
  for (const p of boreSection(t)) {
    D.add("outline", "shell", `${p.outer} ${p.core}`, clip);
    D.add("outline", "core", p.core, clip);
  }
  D.add("outline", "fibre", boreFibres(t), clip);
  D.add("hidden", "centre", line(at(t, [0, h + R + 3]), at(t, [0, h - R - 3])));
  D.add("outline", "ring", circle(t, [0, h], R));
  const y = at(t, [0, h - 7.5])[1];
  dimH(
    D,
    at(t, [-r, 0]),
    at(t, [r, 0]),
    y,
    <span key="d">
      <Dia />
      {DIM.holeD.toFixed(1)}
    </span>,
    { ext: false },
  );
  D.label(at(t, [0, 0])[0], y, "s", "dim", "±0.015");
  const c = at(t, [0, h]);
  const rr = R * t.s;
  const lip = LIP_R;
  const lipTip = at(t, [r + lip - lip * 0.7071, h - lip + lip * 0.7071]);
  if (o.callouts === "flank") {
    leader(D, lipTip, [c[0] + rr * 1.02, c[1] - rr * 0.78], 10, "note", LABELS.flows);
    leader(D, at(t, [-10.5, h]), [c[0] - rr * 1.02, c[1] - rr * 0.78], -10, "note", LABELS.weave);
  } else {
    leader(D, lipTip, [c[0] + rr * 1.14, c[1] - rr * 0.72], 8, "note", LABELS.flows);
    leader(D, at(t, [10, h]), [c[0] + rr * 1.14, c[1] + rr * 0.5], 8, "note", LABELS.weave);
  }
}

/** Graduated scale bar in drawing mm (front-view scale), alternate segments filled. */
function scaleBar(D: Draft, t: Xf, x0: number, y: number, len: number, step: number) {
  const hgt = 3.2;
  const [ax, ay] = at(t, [x0, y]);
  const [bx] = at(t, [x0 + len, y]);
  D.add("dims", "bar", `M${ax} ${ay}H${bx}V${ay + hgt}H${ax}Z`);
  let fills = "";
  for (let x = 0, i = 0; x < len; x += step, i++) {
    if (i % 2 === 0) {
      const [sx] = at(t, [x0 + x, y]);
      fills += `M${sx} ${ay}h${step * t.s}v${hgt}h${-step * t.s}Z`;
    }
  }
  D.add("dims", "barFill", fills);
  for (let x = 0; x <= len; x += len / 2) {
    const [sx] = at(t, [x0 + x, y]);
    D.label(sx, ay + hgt, "s", "muted", String(x));
  }
  D.label(bx + 2, ay + hgt / 2, "e", "muted", "mm");
}

/* ---------- layouts ---------- */

function wideSheet(uid: string): Draft {
  const D = new Draft(1240, 585, uid);
  const f: Xf = { ox: 228, oy: 244, s: 1 };
  const s: Xf = { ox: f.ox + 268, oy: f.oy, s: 1 };
  frontView(D, f, { dims: true, cut: true, callout: true });
  sideView(D, s, { dims: true, balance: true });
  projection(D, f, s);
  const sec: Xf = { ox: 908, oy: 150, s: 2 };
  sectionView(D, sec, { callouts: "wide" });
  D.label(sec.ox, sec.oy + 19 * 2 + 16, "s", "title", LABELS.sectionTitle, <span key="s" className={styles.scale}>{LABELS.sectionScale}</span>);
  const cy = 402;
  const det: Xf = { ox: 884, oy: cy + 19 * 8, s: 8 };
  boreView(D, det, { callouts: "flank" });
  D.label(det.ox, cy + 14 * 8 + 12, "s", "title", LABELS.detailTitle, <span key="s" className={styles.scale}>{LABELS.detailScale}</span>);
  scaleBar(D, { ox: 0, oy: 0, s: 1 }, 1068, -528, 100, 12.5);
  return D;
}

function narrowViews(uid: string): Draft {
  const D = new Draft(490, 566, `${uid}-a`);
  const f: Xf = { ox: 212, oy: 236, s: 1 };
  const s: Xf = { ox: f.ox + 226, oy: f.oy, s: 1 };
  frontView(D, f, { dims: true, cut: true, callout: true });
  sideView(D, s, { dims: true });
  projection(D, f, s);
  return D;
}

function narrowSection(uid: string): Draft {
  const D = new Draft(300, 196, `${uid}-b`);
  const t: Xf = { ox: 150, oy: 92, s: 1 };
  sectionView(D, t, { callouts: "narrow" });
  D.label(14, 12, "se", "title", LABELS.sectionTitle, <span key="s" className={styles.scale}>{LABELS.sectionScale}</span>);
  return D;
}

function narrowDetail(uid: string): Draft {
  const R = 13;
  const s = 6;
  const cy = 116;
  const D = new Draft(320, cy + R * s + 64, `${uid}-c`);
  const t: Xf = { ox: 88, oy: cy + 19 * s, s };
  boreView(D, t, { callouts: "right", R });
  D.label(t.ox, cy + R * s + 8, "s", "title", LABELS.detailTitle, <span key="s" className={styles.scale}>{LABELS.detailScale}</span>);
  return D;
}

function frontOnly(uid: string, annotate: boolean): Draft {
  const D = new Draft(annotate ? 410 : 300, annotate ? 566 : 490, `${uid}-f`);
  const f: Xf = annotate ? { ox: 212, oy: 236, s: 1 } : { ox: 150, oy: 172, s: 1 };
  frontView(D, f, { dims: annotate, callout: annotate });
  return D;
}

/* ---------- rendering ---------- */

const LAYERS: Layer[] = ["outline", "hidden", "dims"];

function Panel({ draft, className }: { draft: Draft; className?: string }) {
  const hatch = `${draft.uid}-hatch`;
  const glow = `${draft.uid}-glow`;
  const byLayer = (l: Layer) => draft.prims.filter((p) => p.layer === l);
  const prim = (p: Prim, i: number) => (
    <path
      key={i}
      d={p.d}
      className={styles[p.kind]}
      fillRule={p.kind === "shell" ? "evenodd" : undefined}
      style={p.kind === "core" ? { fill: `url(#${hatch})` } : undefined}
      clipPath={p.clip ? `url(#${p.clip})` : undefined}
    />
  );
  return (
    <div className={`${styles.panel} ${className ?? ""}`} style={{ aspectRatio: `${draft.w} / ${draft.h}` }}>
      <svg className={styles.svg} viewBox={`0 0 ${draft.w} ${draft.h}`} aria-hidden="true" focusable="false">
        <defs>
          <pattern id={hatch} patternUnits="userSpaceOnUse" width="5.5" height="5.5" patternTransform="rotate(45)">
            <line x1="0" y1="0" x2="0" y2="5.5" className={styles.hatchLine} />
          </pattern>
          <filter id={glow} x="-10%" y="-10%" width="120%" height="120%">
            <feGaussianBlur stdDeviation="2.2" />
          </filter>
          {draft.clips.map((c) => (
            <clipPath id={c.id} key={c.id}>
              <path d={c.d} />
            </clipPath>
          ))}
        </defs>
        {LAYERS.map((l) => (
          <g key={l} data-layer={l}>
            {l === "dims" ? (
              <g className={styles.glow} filter={`url(#${glow})`}>
                {byLayer(l).map(prim)}
              </g>
            ) : null}
            {byLayer(l).map(prim)}
          </g>
        ))}
      </svg>
      <div className={styles.labels} aria-hidden="true">
        {draft.labels.map((lab, i) => (
          <div
            key={i}
            className={`${styles.lab} ${styles[lab.kind]}`}
            data-place={lab.place}
            data-layer="values"
            style={{ left: `${(lab.x / draft.w) * 100}%`, top: `${(lab.y / draft.h) * 100}%` }}
          >
            {lab.lines.map((ln, j) => (
              <span key={j} className={styles.line}>
                {ln}
              </span>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}

/** ISO third-angle projection symbol. */
function ProjectionSymbol() {
  return (
    <svg className={styles.proj} viewBox="0 0 64 28" aria-hidden="true" focusable="false">
      <path d="M4 6 L28 10 V18 L4 22 Z" />
      <circle cx="47" cy="14" r="8" />
      <circle cx="47" cy="14" r="4.4" />
      <path className={styles.projCentre} d="M1 14 H31 M35 14 H60 M47 3 V25" />
    </svg>
  );
}

function TitleBlock() {
  return (
    <div className={styles.titleBlock} data-layer="values">
      <div className={styles.notes}>
        <p className={styles.cap}>{LABELS.notesTitle}</p>
        <ol className={styles.noteList}>
          {LABELS.notes.map((t, i) => (
            <li key={i}>
              <span className={styles.noteNo}>{i + 1}</span>
              {t}
            </li>
          ))}
        </ol>
      </div>
      <div className={styles.cellsWrap}>
        <dl className={styles.cells}>
          <div className={`${styles.cell} ${styles.titleCell}`} style={{ gridArea: "title" }}>
            <dt className={styles.cap}>{LABELS.titleCap}</dt>
            <dd>
              <span className={styles.wordmark}>{LABELS.title}</span>
              <span className={styles.val}>{LABELS.titleSub}</span>
            </dd>
          </div>
          {LABELS.cells.map(([area, k, v]) => (
            <div className={styles.cell} style={{ gridArea: area }} key={area}>
              <dt className={styles.cap}>{k}</dt>
              <dd className={styles.val}>{v}</dd>
            </div>
          ))}
          <div className={styles.cell} style={{ gridArea: "proj" }}>
            <dt className={styles.cap}>{LABELS.projection}</dt>
            <dd>
              <ProjectionSymbol />
            </dd>
          </div>
        </dl>
      </div>
    </div>
  );
}

const ZONES_X = ["1", "2", "3", "4", "5", "6", "7", "8"];
const ZONES_Y = ["A", "B", "C", "D", "E", "F"];

function Zones() {
  return (
    <div className={styles.zones} aria-hidden="true">
      {(["top", "bottom"] as const).map((e) => (
        <div key={e} className={`${styles.zoneRow} ${styles[e]}`}>
          {ZONES_X.map((z) => (
            <span key={z}>{z}</span>
          ))}
        </div>
      ))}
      {(["left", "right"] as const).map((e) => (
        <div key={e} className={`${styles.zoneCol} ${styles[e]}`}>
          {ZONES_Y.map((z) => (
            <span key={z}>{z}</span>
          ))}
        </div>
      ))}
    </div>
  );
}

function useReveal(root: React.RefObject<HTMLElement | null>, enabled: boolean) {
  const { motionOn } = useMotion();
  useGSAP(
    () => {
      if (!motionOn || !enabled || !root.current) return;
      const mm = gsap.matchMedia();
      mm.add("(prefers-reduced-motion: no-preference)", () => {
        const q = gsap.utils.selector(root);
        const tl = gsap.timeline({
          defaults: { duration: 0.4, ease: "power3.out" },
          scrollTrigger: { trigger: root.current, start: "top 75%", once: true },
        });
        (["outline", "hidden", "dims", "values"] as Layer[]).forEach((l, i) => {
          tl.from(q(`[data-layer="${l}"]`), { opacity: 0 }, i * 0.12);
        });
      });
      return () => mm.revert();
    },
    { scope: root, dependencies: [motionOn, enabled], revertOnUpdate: true },
  );
}

export type TechnicalDrawingProps = {
  className?: string;
  /** "full": the whole sheet (spec strip); "front": the front view only (phones, disclosures). */
  variant?: "full" | "front";
  /** "feature" for a graphic in its own right; "quiet" (spec-sheet 40% lines) behind other content. */
  tone?: "feature" | "quiet";
  /** Dimensions and callouts on the front variant. */
  annotate?: boolean;
  /** Title block under the full sheet. */
  titleBlock?: boolean;
  /** Fade the line groups in on first view. */
  reveal?: boolean;
};

export function TechnicalDrawing({
  className,
  variant = "full",
  tone = "feature",
  annotate = true,
  titleBlock = true,
  reveal = true,
}: TechnicalDrawingProps) {
  const root = useRef<HTMLElement>(null);
  const uid = `dw${useId().replace(/[^a-zA-Z0-9]/g, "")}`;
  useReveal(root, reveal);
  const drafts = useMemo(
    () =>
      variant === "full"
        ? { wide: wideSheet(uid), views: narrowViews(uid), section: narrowSection(uid), detail: narrowDetail(uid) }
        : { front: frontOnly(uid, annotate) },
    [uid, variant, annotate],
  );

  return (
    <figure ref={root} className={`${styles.root} ${className ?? ""}`} data-variant={variant} data-tone={tone}>
      {variant === "full" ? (
        <div className={styles.sheet}>
          <Zones />
          <div className={styles.inner}>
            <Panel draft={drafts.wide!} className={styles.wide} />
            <div className={styles.narrow}>
              <Panel draft={drafts.views!} className={styles.pViews} />
              <Panel draft={drafts.section!} className={styles.pSection} />
              <Panel draft={drafts.detail!} className={styles.pDetail} />
            </div>
            {titleBlock ? <TitleBlock /> : null}
          </div>
        </div>
      ) : (
        <Panel draft={drafts.front!} className={styles.front} />
      )}
      <figcaption className="visually-hidden">{LABELS.summary}</figcaption>
    </figure>
  );
}

/* ---------- G10c ghost contour ---------- */

const GHOST: Xf = { ox: 140, oy: 165, s: 1 };
const GHOST_PATHS = { outline: silhouette(GHOST), throat: throat(GHOST), holes: holes(GHOST) };

export type GhostContourProps = {
  className?: string;
  /** Which edge of the zone the contour bleeds off. */
  side?: "left" | "right";
  /** Rotation in degrees (0 = upright, as drawn). */
  angle?: number;
};

/**
 * The front-view outline at 140% of its zone's height, 1px --steel at 7%, bleeding off one edge.
 * Place inside a positioned (relative) zone. Shown only at 1920px and wider.
 */
export function GhostContour({ className, side = "right", angle = 0 }: GhostContourProps) {
  const root = useRef<HTMLDivElement>(null);
  const { motionOn } = useMotion();
  useGSAP(
    () => {
      if (!motionOn) return;
      const mm = gsap.matchMedia();
      mm.add("(prefers-reduced-motion: no-preference) and (min-width: 1920px)", () => {
        gsap.fromTo(
          "[data-ghost-art]",
          { yPercent: -1 },
          {
            yPercent: 1,
            ease: "none",
            scrollTrigger: { trigger: root.current, start: "top bottom", end: "bottom top", scrub: true },
          },
        );
      });
      return () => mm.revert();
    },
    { scope: root, dependencies: [motionOn], revertOnUpdate: true },
  );
  return (
    <div ref={root} className={`${styles.ghost} ${className ?? ""}`} data-side={side} aria-hidden="true">
      <div className={styles.ghostPos} style={{ ["--ghost-angle" as string]: `${angle}deg` }}>
        <svg data-ghost-art className={styles.ghostSvg} viewBox="0 0 280 476" focusable="false">
          <path d={GHOST_PATHS.outline} />
          <path d={GHOST_PATHS.throat} />
          <path d={GHOST_PATHS.holes} />
        </svg>
      </div>
    </div>
  );
}
