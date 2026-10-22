// G11: hairline icons and tier glyphs. 1.25px non-scaling strokes, round caps, currentColor,
// so the parent sets --steel or --amber. Every racket is drawn from racket-shape.ts.
// Server-safe (no hooks): usable from server and client components alike.

import type { ReactNode } from "react";
import type { TierId } from "@/content/lineup";
import { bounds, iconHoleCentres, iconHoleDia, iconRacket, iconThroat, movePts, occluded, penDots, ptsPath, type V } from "@/lib/graphics-icons";
import styles from "./Icons.module.css";

/** Accessible names for the icons (used only when a title is not given and the icon is not decorative). */
export const LABELS = {
  racket: "One racket",
  rackets3: "Three rackets",
  rackets2: "Two rackets",
  fiveYears: "Five years",
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
  // The editions only count the same racket: KINETIQ, First 500 (a numbered set of two), One of Ten (a set of three).
  tiers: { reserve: "One racket", limited: "Two rackets, numbered as a set", invite: "Three rackets, numbered as a set" } as Record<
    TierId,
    string
  >,
};

/* ---------- geometry (computed once, at module load) ---------- */

type Stack = { outlines: string[]; throat: string; holes: string; holeDia: number };

/**
 * `n` identical rackets in a diagonal stack, back to front, centred in a `box` grid. Each racket
 * hides the ones behind it with a `gap` knockout. The front racket carries the throat and, when
 * asked, the real 42-hole map.
 */
function stack(n: number, len: number, hh: number, box: number, dx: number, dy: number, gap: number, holes: boolean): Stack {
  const raw = Array.from({ length: n }, (_, i) => movePts(iconRacket(len, hh), { dx: i * dx, dy: i * dy }));
  const b = bounds(...raw);
  const ox = box / 2 - (b.x0 + b.x1) / 2;
  const oy = box / 2 - (b.y0 + b.y1) / 2;
  const rk = raw.map((r) => movePts(r, { dx: ox, dy: oy }));
  const front = { dx: ox + (n - 1) * dx, dy: oy + (n - 1) * dy };
  return {
    outlines: rk.map((r, i) => (i === n - 1 ? ptsPath(r) : occluded(r, rk.slice(i + 1), gap))),
    throat: ptsPath(movePts(iconThroat(len), front)),
    holes: holes ? penDots(movePts(iconHoleCentres(len), front)) : "",
    holeDia: iconHoleDia(len),
  };
}

function StackArt({ s }: { s: Stack }) {
  return (
    <>
      {s.outlines.map((d, i) => (
        <path key={i} d={d} />
      ))}
      <path d={s.throat} />
      {s.holes ? <path className={styles.holes} d={s.holes} style={{ strokeWidth: s.holeDia }} /> : null}
    </>
  );
}

// 24 px icons: no holes (they would be sub-pixel noise), the throat only on the front racket
const RACKET24 = stack(1, 20, 1.0, 24, 0, 0, 1.1, false);
const RACKETS24 = stack(3, 17.6, 1.0, 24, 4.7, 1.2, 1.1, false);
const PAIR24 = stack(2, 18.2, 1.0, 24, 5.8, 1.3, 1.1, false);

/** A racket lying on its side (head to the left), centred on (cx, cy). */
const lying = (len: number, hh: number, cx: number, cy: number) => {
  const r = iconRacket(len, hh);
  const t = iconThroat(len);
  const place = (p: V[]) => movePts(movePts(p, { dx: cx, dy: cy - len / 2 }), { rot: -90, px: cx, py: cy });
  return { outline: place(r), throat: place(t) };
};
const CASE_RACKET = lying(15.4, 0.95, 12, 12.6);
// the mould: a square-cornered tool block with four clamp bolts, the parting line running in from
// both sides to the racket-shaped cavity
const MOULD_RACKET = lying(12.8, 0.85, 12, 12);
const MOULD_PARTING = (() => {
  const b = bounds(MOULD_RACKET.outline);
  return `M2.75 12H${(b.x0 - 1.1).toFixed(2)}M${(b.x1 + 1.1).toFixed(2)} 12H21.25`;
})();

const GLYPH_LEN = 42;
const G_RESERVE = stack(1, GLYPH_LEN, 2.05, 48, 0, 0, 1.8, true);
const G_INVITE = stack(3, 34.5, 1.8, 48, 8.4, 2.4, 1.9, true);
// First 500: the set of two (the back racket knocked out behind the front one) with the set's numbered
// tag tied to the front grip
const PAIR = (() => {
  const len = 37;
  const backAt = { dx: 12.2, dy: 3 };
  const frontAt = { dx: 19.4, dy: 6.2 };
  const back = movePts(iconRacket(len, 1.9), backAt);
  const front = movePts(iconRacket(len, 1.9), frontAt);
  return {
    outlines: [occluded(back, [front], 1.8), ptsPath(front)],
    throat: ptsPath(movePts(iconThroat(len), frontAt)),
    holes: penDots(movePts(iconHoleCentres(len), frontAt)),
    holeDia: iconHoleDia(len),
  } satisfies Stack;
})();
// "001" in squarish strokes that echo Saira's numerals; 6.4 units tall
const DIGIT_H = 6.4;
const DIGIT_W = 3.1;
const DIGIT_Y = 36 - DIGIT_H / 2;
const zero = (x: number) => `M${x + 1.35} ${DIGIT_Y}h${DIGIT_W - 2.7}a1.35 1.35 0 0 1 1.35 1.35v${DIGIT_H - 2.7}a1.35 1.35 0 0 1 -1.35 1.35h${-(DIGIT_W - 2.7)}a1.35 1.35 0 0 1 -1.35 -1.35v${-(DIGIT_H - 2.7)}a1.35 1.35 0 0 1 1.35 -1.35Z`;
const one = (x: number) => `M${x + 0.6} ${DIGIT_Y + 1.5}L${x + 2.15} ${DIGIT_Y}V${DIGIT_Y + DIGIT_H}`;
const TAG_DIGITS = zero(30.6) + zero(35.05) + one(39.5);

/* ---------- icons (24 x 24 grid) ---------- */

export type IconName =
  | "racket"
  | "rackets3"
  | "rackets2"
  | "fiveYears"
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
  "racket",
  "rackets3",
  "rackets2",
  "fiveYears",
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
  racket: <StackArt s={RACKET24} />,
  rackets3: <StackArt s={RACKETS24} />,
  rackets2: <StackArt s={PAIR24} />,
  // a dial open at the top (time) around a squarish 5 that echoes Saira's numerals
  fiveYears: (
    <>
      <path d="M14.99 3.78 A8.75 8.75 0 1 1 9.01 3.78" />
      <path d="M10.75 1.9 H13.25" />
      <path d="M14.4 7.6 H10.15 L9.85 11.35 C10.45 10.95 11.15 10.8 11.9 10.8 C13.7 10.8 14.85 11.95 14.85 13.65 C14.85 15.4 13.6 16.5 11.85 16.5 C10.8 16.5 9.9 16.05 9.3 15.3" />
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
      <path d={ptsPath(CASE_RACKET.outline)} />
      <path d={ptsPath(CASE_RACKET.throat)} />
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
      <rect x="2.75" y="4.75" width="18.5" height="14.5" rx="0.75" />
      <path d={MOULD_PARTING} />
      <circle cx="5.1" cy="7.1" r="0.8" />
      <circle cx="18.9" cy="7.1" r="0.8" />
      <circle cx="5.1" cy="16.9" r="0.8" />
      <circle cx="18.9" cy="16.9" r="0.8" />
      <path d={ptsPath(MOULD_RACKET.outline)} />
      <path d={ptsPath(MOULD_RACKET.throat)} />
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

export function TierGlyph({ tier, selected = false, className, title }: TierGlyphProps) {
  let art: ReactNode;
  if (tier === "reserve") {
    art = <StackArt s={G_RESERVE} />;
  } else if (tier === "limited") {
    art = (
      <>
        <StackArt s={PAIR} />
        {/* the set's numbered tag, tied to the front grip */}
        <path d="M26.5 36.9 C25 39.9 23.2 41.6 21.3 41.9" />
        <path d="M26.2 30.5 H43.8 Q45 30.5 45 31.7 V40.3 Q45 41.5 43.8 41.5 H26.2 L23 36 Z" />
        <circle cx="27.5" cy="36" r="1" />
        <path className={styles.digit} d={TAG_DIGITS} />
      </>
    );
  } else {
    art = <StackArt s={G_INVITE} />;
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

