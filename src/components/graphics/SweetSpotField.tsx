"use client";

import { useId, useMemo, useRef } from "react";
import { useMotion } from "@/components/motion/MotionProvider";
import { sweetSpot } from "@/content/copy";
import { HANDLE_MM, CAP_SEAM, HOLES_MM, HOLE_R_MM, circle, handleDetail, holes, silhouette, throat, type V } from "@/lib/graphics-drawing";
import { FIELD, G15_XF, SPREAD_CENTRE, SWEET_CLAIM, g15Layout, polyPath, type G15Variant } from "@/lib/graphics-sweetspot";
import { gsap, useGSAP } from "@/lib/gsap";
import styles from "./SweetSpotField.module.css";

const T = G15_XF;
const n2 = (v: number) => Number(v.toFixed(2));

/**
 * Each moulded hole as a lined bore, seen face-on with the light from the upper left: the hole is open (the floor
 * shows through it), and the bore's lower-right wall, which faces the light, shows as a crescent inside the lip.
 * A crescent is the hole minus a copy of it shifted toward the light (even-odd, clipped to the holes), so it is
 * widest at the lower right and vanishes at the sides. `wall`: the whole visible wall (white carbon in shadow);
 * `near`: its upper part, nearest the face, a step lighter. `lip`: the rounded lip catching the light, an arc on the
 * lower right (drawn with the sweet spot's light, as K12's lip light).
 */
const crescents = (k: number) =>
  HOLES_MM.map((h, i) => {
    const r = HOLE_R_MM[i];
    return circle(T, h, r) + circle(T, [h[0] - k * r, h[1] + k * r], r);
  }).join(" ");
const LIP_ARC = HOLES_MM.map(([cx, cy], i) => {
  const r = HOLE_R_MM[i] + 0.1;
  const pts: V[] = [];
  for (let j = 0; j <= 10; j++) {
    const a = ((-95 + (j * 100) / 10) * Math.PI) / 180; // from straight down to just past three o'clock
    pts.push([cx + r * Math.cos(a), -(cy + r * Math.sin(a))]);
  }
  return pts.map(([x, y], j) => `${j ? "L" : "M"}${n2(x)} ${n2(y)}`).join("");
}).join("");

/** The engraved Q on the cap's front band (the company logo, kq_canon): 4.2 mm tall, bright-cut in satin black. */
const Q_MARK = (() => {
  const y = -HANDLE_MM.cap.mark; // sheet y
  return { cx: 0, cy: n2(y), rx: 1.75, ry: 2.05, tail: `M${n2(0.55)} ${n2(y + 1.05)}L${n2(1.85)} ${n2(y + 2.3)}` };
})();

const PATHS = {
  outline: silhouette(T),
  throat: throat(T),
  holes: holes(T),
  field: polyPath(T, FIELD),
  handle: handleDetail(T, "front"),
  wall: crescents(0.32),
  near: crescents(0.12),
  lip: LIP_ARC,
};
/** Sheet y of the overgrip's top and of the cap's seam (the grip and the cap take their own finish). */
const GRIP_TOP = -HANDLE_MM.grip.top;
const CAP_TOP = -CAP_SEAM(HANDLE_MM.grip.x);
/**
 * 3K 2/2 twill, 2.6 mm tows, four to a repeat: in row r the weft tow floats over columns (4 - r) % 4 and the next
 * one, and in column c the warp tow over rows (6 - c) % 4 and the next (a float that wraps the repeat is drawn
 * twice, a repeat apart). The floats tile the face; the crevices between them are the tile minus the floats.
 */
const TOW = 2.6;
const REP = TOW * 4;
const GAP = 0.2;
const TWILL = [0, 1, 2, 3].flatMap((i) => {
  const w = (4 - i) % 4;
  const v = (6 - i) % 4;
  return [0, -REP].flatMap((o) => [
    { weft: true, x: w * TOW + o + GAP, y: i * TOW + GAP, w: 2 * TOW - 2 * GAP, h: TOW - 2 * GAP },
    { weft: false, x: i * TOW + GAP, y: v * TOW + o + GAP, w: TOW - 2 * GAP, h: 2 * TOW - 2 * GAP },
  ]);
});
/** The crevices: the tile minus every float (even-odd; floats never overlap, and the tile clips what wraps). */
const CREVICES =
  `M0 0H${REP}V${REP}H0Z` +
  TWILL.map((t) => `M${n2(t.x)} ${n2(t.y)}h${n2(t.w)}v${n2(t.h)}h${n2(-t.w)}Z`).join("");

/**
 * One framing of G15, after the K12 still it stands in for: the canonical racket face-on in white 3K twill (Command,
 * owner 2026-10-22), the studio light low, and the sweet spot lit warm and even to 4 mm from the edge (the field,
 * from racket-shape.ts via graphics-sweetspot.ts), the weave reading through the light; the 42 holes open, each
 * with its lined bore and lit lip; and a magnified detail of the edge with its 4 mm dimension. The detail is the
 * edge drawn again at the detail's own scale (graphics-sweetspot.ts lensDetail), with the racket's own carbon and light
 * at that spot, so it stays crisp and matches the racket beside it.
 */
function Panel({ variant, className }: { variant: G15Variant; className?: string }) {
  const uid = `ss${useId().replace(/[^a-zA-Z0-9]/g, "")}`;
  const L = useMemo(() => g15Layout(variant), [variant]);
  const id = (k: string) => `${uid}-${k}`;
  const url = (k: string) => `url(#${id(k)})`;
  const [lx, ly] = L.pct(L.labelAt);
  const [sx, sy] = [SPREAD_CENTRE[0], -SPREAD_CENTRE[1]];
  const faceAndHoles = `${PATHS.outline} ${PATHS.throat} ${PATHS.holes}`;
  return (
    <div className={`${styles.panel} ${className ?? ""}`} data-variant={variant} style={{ aspectRatio: `${L.w} / ${L.h}` }}>
      <svg className={styles.svg} viewBox={L.viewBox} aria-hidden="true" focusable="false">
        <defs>
          {/* white carbon in a low studio light: a soft pool from the upper left, falling into shade down the neck */}
          <linearGradient id={id("carbon")} gradientUnits="userSpaceOnUse" x1="-120" y1="-150" x2="90" y2="230">
            <stop offset="0" className={styles.carbon0} />
            <stop offset="0.45" className={styles.carbon1} />
            <stop offset="1" className={styles.carbon2} />
          </linearGradient>
          <linearGradient id={id("cap")} gradientUnits="userSpaceOnUse" x1="-18" y1="0" x2="18" y2="0">
            <stop offset="0" className={styles.cap0} />
            <stop offset="0.35" className={styles.cap1} />
            <stop offset="1" className={styles.cap0} />
          </linearGradient>
          {/* the sweet spot's light: warm white, even, a touch warmer toward its line */}
          <radialGradient id={id("light")} gradientUnits="userSpaceOnUse" cx={sx} cy={sy} r="150">
            <stop offset="0" className={styles.light0} />
            <stop offset="0.55" className={styles.light1} />
            <stop offset="0.85" className={styles.light2} />
            <stop offset="1" className={styles.light3} />
          </radialGradient>
          <linearGradient id={id("rim")} gradientUnits="userSpaceOnUse" x1="-100" y1="-155" x2="60" y2="60">
            <stop offset="0" className={styles.rim0} />
            <stop offset="1" className={styles.rim1} />
          </linearGradient>
          {/* the clear coat: one crisp gloss line from the upper left to the lower right, with a soft shoulder */}
          <linearGradient id={id("coat")} gradientUnits="userSpaceOnUse" x1="-150" y1="-120" x2="70" y2="60">
            <stop offset="0.36" className={styles.coat0} />
            <stop offset="0.455" className={styles.coat1} />
            <stop offset="0.47" className={styles.coat2} />
            <stop offset="0.485" className={styles.coat1} />
            <stop offset="0.58" className={styles.coat0} />
          </linearGradient>
          {/* each tow a rounded bundle: darker at its edges, the warp tows a shade darker than the weft (fibre seen
              across its axis scatters more light than along it) */}
          <linearGradient id={id("weft")} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" className={styles.towEdge} />
            <stop offset="0.5" className={styles.towCrown} />
            <stop offset="1" className={styles.towEdge} />
          </linearGradient>
          <linearGradient id={id("warp")} x1="0" y1="0" x2="1" y2="0">
            <stop offset="0" className={styles.towEdge} />
            <stop offset="0.5" className={styles.warpCrown} />
            <stop offset="1" className={styles.towEdge} />
          </linearGradient>
          <pattern id={id("twill")} patternUnits="userSpaceOnUse" width={REP} height={REP}>
            <path d={CREVICES} fillRule="evenodd" className={styles.crevice} />
            {TWILL.map((t, i) => (
              <rect key={i} x={t.x} y={t.y} width={t.w} height={t.h} rx="0.8" fill={url(t.weft ? "weft" : "warp")} />
            ))}
          </pattern>
          {/* the light spreads from the sweet spot (scaled by the reveal; at rest it covers the whole field) */}
          <radialGradient id={id("soft")}>
            <stop offset="0.8" stopColor="#fff" />
            <stop offset="1" stopColor="#000" />
          </radialGradient>
          <mask id={id("spread")} maskUnits="userSpaceOnUse" x="-200" y="-200" width="400" height="320">
            <circle data-g15-spread="" cx={sx} cy={sy} r="210" fill={url("soft")} />
          </mask>
          <clipPath id={id("grip")}>
            <rect x="-40" y={GRIP_TOP} width="80" height="200" />
          </clipPath>
          <clipPath id={id("capclip")}>
            <rect x="-40" y={CAP_TOP} width="80" height="60" />
          </clipPath>
          <clipPath id={id("weaveclip")}>
            <rect x="-140" y="-160" width="280" height={GRIP_TOP + 160} />
          </clipPath>
          <clipPath id={id("bores")}>
            <path d={PATHS.holes} />
          </clipPath>
          <clipPath id={id("lens")}>
            <circle cx={L.detail.c[0]} cy={L.detail.c[1]} r={L.detail.r} />
          </clipPath>
          {/* the detail's own paint, mapped to its 6x scale: the carbon and the light exactly as the racket shows them
              at that spot, the rounded edge as a highlight across its 1.5 mm, and a fine hatch for the weave (crisp
              at any scale, where the twill itself would blow up into blocks) */}
          <linearGradient id={id("lensCarbon")} gradientUnits="userSpaceOnUse" x1="-120" y1="-150" x2="90" y2="230" gradientTransform={L.transform}>
            <stop offset="0" className={styles.carbon0} />
            <stop offset="0.45" className={styles.carbon1} />
            <stop offset="1" className={styles.carbon2} />
          </linearGradient>
          <radialGradient id={id("lensLight")} gradientUnits="userSpaceOnUse" cx={sx} cy={sy} r="150" gradientTransform={L.transform}>
            <stop offset="0" className={styles.light0} />
            <stop offset="0.55" className={styles.light1} />
            <stop offset="0.85" className={styles.light2} />
            <stop offset="1" className={styles.light3} />
          </radialGradient>
          <linearGradient id={id("edgeShade")} gradientUnits="userSpaceOnUse" {...L.lens.shade}>
            <stop offset="0" className={styles.edge0} />
            <stop offset="0.3" className={styles.edge1} />
            <stop offset="0.58" className={styles.edge2} />
            <stop offset="0.8" className={styles.edge3} />
            <stop offset="1" className={styles.edge4} />
          </linearGradient>
          <pattern id={id("hatch")} patternUnits="userSpaceOnUse" width="3.4" height="3.4" patternTransform="rotate(45)">
            <path d="M0 0.2H3.4" className={styles.hatch} />
          </pattern>
        </defs>

        <g data-g15="body">
          <g>
            {/* white carbon: the head, neck and handle as one silhouette, the throat and the holes open */}
            <path d={faceAndHoles} fillRule="evenodd" fill={url("carbon")} />
            <path d={PATHS.outline} className={styles.grip} clipPath={url("grip")} />
            <path d={PATHS.outline} fill={url("cap")} clipPath={url("capclip")} />
            {/* the weave on the bare carbon, in the studio's low light */}
            <path d={faceAndHoles} fillRule="evenodd" fill={url("twill")} clipPath={url("weaveclip")} />
            {/* each bore, lined in the same white carbon, its lit wall inside the lip */}
            <g clipPath={url("bores")}>
              <path d={PATHS.wall} fillRule="evenodd" className={styles.wall} />
              <path d={PATHS.near} fillRule="evenodd" className={styles.near} />
            </g>
            {/* the sweet spot: the field, lit warm and even to 4 mm from the edge and 4 mm above the throat, the
                weave reading through the light; the bores stay unlit, only their lips catch it */}
            <g data-g15="field" mask={url("spread")}>
              <path d={`${PATHS.field} ${PATHS.holes}`} fillRule="evenodd" fill={url("light")} className={styles.light} />
              <path d={`${PATHS.field} ${PATHS.holes}`} fillRule="evenodd" fill={url("twill")} className={styles.litWeave} />
              <path d={PATHS.lip} className={styles.lip} />
              <path d={PATHS.field} className={styles.fieldLine} />
            </g>
            <path d={faceAndHoles} fillRule="evenodd" fill={url("coat")} clipPath={url("weaveclip")} />
            <path d={PATHS.handle} className={styles.handle} />
            <g className={styles.qmark}>
              <ellipse cx={Q_MARK.cx} cy={Q_MARK.cy} rx={Q_MARK.rx} ry={Q_MARK.ry} />
              <path d={Q_MARK.tail} />
            </g>
            <path d={`${PATHS.outline} ${PATHS.throat}`} stroke={url("rim")} className={styles.rim} />
          </g>
        </g>

        <g data-g15="detail">
          <circle cx={L.ring.c[0]} cy={L.ring.c[1]} r={L.ring.r} className={styles.ring} />
          <path d={L.leader} className={styles.leader} />
          {/* the edge six times larger, drawn at that scale: the flat band of white carbon, the 1.5 mm radius
              catching the light, the lit field to its amber line, and the page's own graphite beyond the edge */}
          <g clipPath={url("lens")}>
            <path d={L.lens.body} fill={url("lensCarbon")} />
            <path d={L.lens.body} fill={url("hatch")} className={styles.bandHatch} />
            <path d={L.lens.radius} fill={url("edgeShade")} />
            <path d={L.lens.field} fill={url("lensLight")} />
            <path d={L.lens.field} fill={url("hatch")} className={styles.fieldHatch} />
            <path d={L.lens.fieldLine} className={styles.lensFieldLine} />
            <path d={L.lens.edgeLine} className={styles.lensEdge} />
          </g>
          <circle cx={L.detail.c[0]} cy={L.detail.c[1]} r={L.detail.r} className={styles.lensRim} />
          <path d={L.ext} className={styles.ext} />
          <path d={L.dim} className={styles.dim} />
          <path d={L.arrows} className={styles.arrow} />
        </g>
      </svg>
      <span className={`${styles.label} t-num`} data-g15="detail" data-place={L.labelPlace} style={{ left: `${lx}%`, top: `${ly}%` }} aria-hidden="true">
        {sweetSpot.graphic.detail(SWEET_CLAIM)}
      </span>
    </div>
  );
}

type Mode = "scrub" | "play" | "fade";

/**
 * G15's reveal, added to a timeline. "scrub" (a scroll-scrubbed timeline of length 1): the racket rises, then the
 * light spreads from the sweet spot to its 4 mm line, then the detail. "play": the same in seconds. "fade"
 * (phones): the racket, then the light, fading in. Only transform and opacity move: the spread scales the
 * mask's soft disc, never the field, which stops at its own line.
 */
export function addSweetSpotReveal(tl: gsap.core.Timeline, root: Element, mode: Mode, at = 0) {
  const q = gsap.utils.selector(root);
  const scrub = mode === "scrub";
  const k = scrub ? 1 : 2;
  const body = q('[data-g15="body"]');
  const field = q('[data-g15="field"]');
  const spread = q("[data-g15-spread]");
  const detail = q('[data-g15="detail"]');
  tl.fromTo(body, { autoAlpha: 0, y: mode === "fade" ? 0 : 10 }, { autoAlpha: 1, y: 0, duration: 0.2 * k, ease: scrub ? "none" : "power2.out", immediateRender: true }, at);
  if (mode === "fade") {
    tl.fromTo(field, { opacity: 0 }, { opacity: 1, duration: 0.6, ease: "power2.out", immediateRender: true }, at + 0.25);
  } else {
    tl.fromTo(
      spread,
      { scale: 0.15, transformOrigin: "50% 50%" },
      { scale: 1, duration: 0.4 * k, ease: scrub ? "none" : "power2.inOut", immediateRender: true },
      at + 0.15 * k,
    ).fromTo(field, { opacity: 0 }, { opacity: 1, duration: 0.12 * k, ease: "none", immediateRender: true }, at + 0.15 * k);
  }
  tl.fromTo(detail, { autoAlpha: 0 }, { autoAlpha: 1, duration: scrub ? 0.15 : 0.4, ease: scrub ? "none" : "power2.out", immediateRender: true }, at + (mode === "fade" ? 0.7 : 0.55 * k));
  return tl;
}

export type SweetSpotFieldProps = {
  className?: string;
  /** "auto": the wide framing, and the portrait one below 700 px (as the K12 still's crops). */
  variant?: G15Variant | "auto";
  /** Plays its own reveal on entry (review pages). The landing section drives it from its own timeline. */
  reveal?: boolean;
};

/** G15 "Sweet spot": illustrative, drawn from racket-shape.ts. The text alternative is a hidden caption. */
export function SweetSpotField({ className, variant = "auto", reveal = false }: SweetSpotFieldProps) {
  const root = useRef<HTMLElement>(null);
  const { motionOn } = useMotion();
  useGSAP(
    () => {
      if (!motionOn || !reveal || !root.current) return;
      const mm = gsap.matchMedia();
      mm.add("(prefers-reduced-motion: no-preference)", () => {
        const tl = gsap.timeline({ scrollTrigger: { trigger: root.current, start: "top 70%", once: true } });
        addSweetSpotReveal(tl, root.current!, "play");
      });
      return () => mm.revert();
    },
    { scope: root, dependencies: [motionOn, reveal], revertOnUpdate: true },
  );
  return (
    <figure ref={root} className={`${styles.root} ${className ?? ""}`} data-variant={variant}>
      {variant === "portrait" ? null : <Panel variant="wide" className={styles.wide} />}
      {variant === "wide" ? null : <Panel variant="portrait" className={styles.portrait} />}
      <figcaption className="visually-hidden">{sweetSpot.graphic.alt(SWEET_CLAIM)}</figcaption>
    </figure>
  );
}
