// G11: hairline icons and tier glyphs. 1.25px non-scaling strokes, round caps, currentColor,
// so the parent sets --steel or --amber. Every racket is drawn from racket-shape.ts.
// Server-safe (no hooks): usable from server and client components alike.

import type { ReactNode } from "react";
import type { TierId } from "@/content/lineup";
import { clearOf, iconHoles, iconRacket, iconThroat, movePts, occluded, ptsPath, type V } from "@/lib/graphics-icons";
import styles from "./Icons.module.css";

/** Accessible names for the icons (used only when a title is not given and the icon is not decorative). */
export const LABELS = {
  rackets3: "Three rackets",
  penNib: "Autographed",
  court: "Court session",
  numberedTag: "Numbered",
  fittedCase: "Fitted case",
  measurementCard: "Measurement card",
  deliveryBox: "Delivery",
  refundArrow: "Refundable",
  shieldCheck: "Secure",
  swissCross: "Swiss Made",
  mould: "One mould",
  tiers: { reserve: "One racket", limited: "One numbered racket", invite: "Three rackets" } as Record<TierId, string>,
};

/* ---------- geometry (computed once, at module load) ---------- */

const r24 = (len: number, hh: number, dx: number, dy: number, rot = 0, px = 0, py = 0) =>
  movePts(movePts(iconRacket(len, hh), { dx, dy }), { rot, px, py });

const ringPath = (c: V[], r: number) =>
  c.map(([x, y]) => `M${(x - r).toFixed(2)} ${y.toFixed(2)}a${r} ${r} 0 1 0 ${2 * r} 0a${r} ${r} 0 1 0 ${-2 * r} 0Z`).join("");

// three rackets in a cascade, the centre one in front: each side racket leans out from its own butt
const fan = (len: number, hh: number, cx: number, top: number, spread: number, drop: number, deg: number, gap: number, step: number, hr: number) => {
  const place = (dx: number, dy: number, rot: number) => (pts: V[]) =>
    movePts(movePts(pts, { dx: cx + dx, dy: top + dy }), { rot, px: cx + dx, py: top + len + dy });
  const centre = place(0, 0, 0)(iconRacket(len, hh));
  const sides = [place(-spread, drop, -deg), place(spread, drop, deg)];
  const holeSet = iconHoles(len, step);
  const sideHoles = sides.flatMap((f) => clearOf(f(holeSet), [centre], gap + hr));
  return {
    centre,
    back: sides.map((f) => occluded(f(iconRacket(len, hh)), [centre], gap)).join(""),
    holes: ringPath([...place(0, 0, 0)(holeSet), ...sideHoles], hr),
  };
};

const FAN24 = fan(17, 0.95, 12, 2.5, 5.2, 1.5, 9, 1.1, 0.62, 0.5);
const CASE_RACKET = movePts(r24(14.6, 0.95, 12, 4.7), { rot: -90, px: 12, py: 12 });
const MOULD_RACKET = movePts(movePts(iconRacket(14, 0.9), { dx: 12, dy: 5 }), { rot: -90, px: 12, py: 12 });
const MOULD_HOLES = ringPath(movePts(movePts(iconHoles(14, 0.62), { dx: 12, dy: 5 }), { rot: -90, px: 12, py: 12 }), 0.5);
const CASE_HOLES = ringPath(movePts(movePts(iconHoles(14.6, 0.62), { dx: 12, dy: 4.7 }), { rot: -90, px: 12, py: 12, dy: 0.5 }), 0.5);

const GLYPH_LEN = 40;
const glyphRacket = (cx: number, top: number, len = GLYPH_LEN) => ({
  outline: ptsPath(movePts(iconRacket(len, 1.9), { dx: cx, dy: top })),
  holes: ringPath(movePts(iconHoles(len), { dx: cx, dy: top }), 0.95),
  throat: ptsPath(movePts(iconThroat(len), { dx: cx, dy: top })),
});
const G_RESERVE = glyphRacket(24, 4);
const G_LIMITED = glyphRacket(19, 3.5);
const FAN48 = (() => {
  const len = 38;
  const centreTop = 4;
  const f = fan(len, 1.7, 24, centreTop, 11.5, 3, 9, 1.8, 0.52, 0.9);
  return {
    centre: ptsPath(f.centre),
    holes: f.holes,
    throat: ptsPath(movePts(iconThroat(len), { dx: 24, dy: centreTop })),
    back: f.back,
  };
})();

/* ---------- icons (24 x 24 grid) ---------- */

export type IconName =
  | "rackets3"
  | "penNib"
  | "court"
  | "numberedTag"
  | "fittedCase"
  | "measurementCard"
  | "deliveryBox"
  | "refundArrow"
  | "shieldCheck"
  | "swissCross"
  | "mould";

export const ICON_NAMES: IconName[] = [
  "rackets3",
  "penNib",
  "court",
  "numberedTag",
  "fittedCase",
  "measurementCard",
  "deliveryBox",
  "refundArrow",
  "shieldCheck",
  "swissCross",
  "mould",
];

const ICONS: Record<IconName, ReactNode> = {
  rackets3: (
    <>
      <path d={FAN24.back} />
      <path d={ptsPath(FAN24.centre)} />
      <path className={styles.dots} d={FAN24.holes} />
    </>
  ),
  penNib: (
    <>
      <g transform="rotate(45 12 12)">
        <path d="M12 21.25 L7.75 13.4 C7.4 12.75 7.5 12 8 11.45 L10 9.25 V2.75 H14 V9.25 L16 11.45 C16.5 12 16.6 12.75 16.25 13.4 Z" />
        <path d="M10 9.25 H14 M12 21.25 V15" />
        <circle cx="12" cy="13.6" r="1.15" />
      </g>
      <path d="M9.5 20.4 C11.2 19.2 12.4 21.6 14.1 20.5 C15.5 19.6 16.4 18.6 17.3 19.7 C17.9 20.4 19 20.6 20.75 19.4" />
    </>
  ),
  court: (
    <>
      <rect x="2.75" y="7.25" width="18.5" height="9.5" rx="0.6" />
      <path d="M12 5.75 V18.25 M5.9 7.25 V16.75 M18.1 7.25 V16.75 M5.9 12 H18.1" />
    </>
  ),
  numberedTag: (
    <>
      <path d="M3.25 12 L7.25 6.75 H19.75 C20.3 6.75 20.75 7.2 20.75 7.75 V16.25 C20.75 16.8 20.3 17.25 19.75 17.25 H7.25 Z" />
      <circle cx="7.5" cy="12" r="1.15" />
      <path d="M13.15 9.25 L12.35 14.75 M16.15 9.25 L15.35 14.75 M11.5 10.85 H17.4 M11.1 13.15 H17" />
    </>
  ),
  fittedCase: (
    <>
      <rect x="2.25" y="5.75" width="19.5" height="13.5" rx="2.25" />
      <path d="M9.5 5.75 V4.5 C9.5 3.95 9.95 3.5 10.5 3.5 H13.5 C14.05 3.5 14.5 3.95 14.5 4.5 V5.75" />
      <path d={ptsPath(movePts(CASE_RACKET, { dy: 0.5 }))} />
      <path className={styles.dots} d={CASE_HOLES} />
    </>
  ),
  measurementCard: (
    <>
      <rect x="2.75" y="5" width="18.5" height="14" rx="1.5" />
      <path d="M5.75 8.6 H12.5 M5.75 12 H10 M13 12 H18.25 M5.75 15.25 H10 M13 15.25 H18.25" />
      <circle cx="17.25" cy="8.6" r="1.1" />
    </>
  ),
  deliveryBox: (
    <>
      <path d="M12 2.75 L20.25 7.1 V16.9 L12 21.25 L3.75 16.9 V7.1 Z" />
      <path d="M3.75 7.1 L12 11.45 L20.25 7.1 M12 11.45 V21.25 M7.9 4.95 L16.1 9.3 V12.6" />
    </>
  ),
  refundArrow: (
    <>
      <path d="M9.25 5 L5 9.25 L9.25 13.5" />
      <path d="M5.25 9.25 H14.25 C16.87 9.25 19 11.38 19 14 C19 16.62 16.87 18.75 14.25 18.75 H9" />
    </>
  ),
  shieldCheck: (
    <>
      <path d="M12 2.75 L19.25 5.5 V11.25 C19.25 15.9 16.25 19.6 12 21.25 C7.75 19.6 4.75 15.9 4.75 11.25 V5.5 Z" />
      <path d="M8.6 12.1 L11 14.5 L15.6 9.6" />
    </>
  ),
  swissCross: (
    <>
      <rect className={styles.swissField} x="3" y="3" width="18" height="18" rx="1.75" />
      <path className={styles.swissCross} d="M10.31 6.38 H13.69 V10.31 H17.63 V13.69 H13.69 V17.63 H10.31 V13.69 H6.38 V10.31 H10.31 Z" />
    </>
  ),
  mould: (
    <>
      <path d="M2.75 11.25 V6.5 C2.75 5.67 3.42 5 4.25 5 H19.75 C20.58 5 21.25 5.67 21.25 6.5 V11.25 Z" />
      <path d="M2.75 12.75 V17.5 C2.75 18.33 3.42 19 4.25 19 H19.75 C20.58 19 21.25 18.33 21.25 17.5 V12.75 Z" />
      <path d={ptsPath(MOULD_RACKET)} />
      <path className={styles.dots} d={MOULD_HOLES} />
    </>
  ),
};

export type IconProps = {
  name: IconName;
  /** Rendered size in px (the drawing grid is 24). */
  size?: number;
  className?: string;
  /** Accessible name. Omit for decorative icons next to a visible label. */
  title?: string;
};

export function Icon({ name, size = 24, className, title }: IconProps) {
  return (
    <svg
      className={`${styles.icon} ${name === "swissCross" ? styles.filled : ""} ${className ?? ""}`}
      viewBox="0 0 24 24"
      width={size}
      height={size}
      role={title ? "img" : undefined}
      aria-label={title}
      aria-hidden={title ? undefined : true}
      focusable="false"
    >
      {ICONS[name]}
    </svg>
  );
}

/* ---------- tier glyphs (48 x 48 grid) ---------- */

export type TierGlyphProps = {
  tier: TierId;
  selected?: boolean;
  className?: string;
  /** Accessible name. Omit when the tier name is shown beside it (the default). */
  title?: string;
};

function Digit0({ x }: { x: number }) {
  return <ellipse className={styles.digit} cx={x} cy={37} rx={1.55} ry={2.9} />;
}

export function TierGlyph({ tier, selected = false, className, title }: TierGlyphProps) {
  let art: ReactNode;
  if (tier === "reserve") {
    art = (
      <>
        <path d={G_RESERVE.outline} />
        <path className={styles.soft} d={G_RESERVE.holes} />
        <path d={G_RESERVE.throat} />
      </>
    );
  } else if (tier === "limited") {
    art = (
      <>
        <path d={G_LIMITED.outline} />
        <path className={styles.soft} d={G_LIMITED.holes} />
        <path d={G_LIMITED.throat} />
        {/* the numbered tag, tied to the butt */}
        <path d="M19 43.5 C21.6 46.2 26.6 43.6 28.2 38.2" />
        <path d="M24.6 37 L28.4 32 H44.4 C45 32 45.5 32.5 45.5 33.1 V40.9 C45.5 41.5 45 42 44.4 42 H28.4 Z" />
        <circle cx="28.6" cy="37" r="1.1" />
        <Digit0 x={33.4} />
        <Digit0 x={37.8} />
        <path className={styles.digit} d="M41.2 35.2 L42.6 34.1 V39.9" />
      </>
    );
  } else {
    art = (
      <>
        <path d={FAN48.back} />
        <path d={FAN48.centre} />
        <path className={styles.soft} d={FAN48.holes} />
        <path d={FAN48.throat} />
      </>
    );
  }
  return (
    <svg
      className={`${styles.icon} ${styles.glyph} ${className ?? ""}`}
      data-selected={selected ? "true" : "false"}
      data-tier={tier}
      viewBox="0 0 48 48"
      role={title ? "img" : undefined}
      aria-label={title}
      aria-hidden={title ? undefined : true}
      focusable="false"
    >
      {art}
    </svg>
  );
}

