"use client";

import { useId, useRef } from "react";
import { useMotion } from "@/components/motion/MotionProvider";
import { identical } from "@/content/copy";
import { sampleSet } from "@/content/lineup";
import { gsap, useGSAP } from "@/lib/gsap";
import {
  flatness,
  headOutline,
  holeDots,
  mapViewBox,
  rosetteTurns,
  rosetteWave,
  throatOutline,
} from "@/lib/graphics-certificate";
import styles from "./MeasurementCard.module.css";

const { card } = identical;

/** Strings this graphic adds on top of identical.card (copy.ts). */
export const LABELS = {
  wordmark: "KINETIQ",
  serial: "Serial",
  limit: "limit 0.015 mm",
  mapTitle: "Flatness",
  mapScaleFrom: "0",
  mapScaleTo: "12 µm",
  signature: "Signature",
  summary:
    "Sample measurement card: every KINETIQ ships with its own certificate, with the measured weight, balance, thickness and surface deviation, a flatness map of the head and a blank signature line.",
};

type Props = {
  className?: string;
  /**
   * A First 500 sample card, one per racket of set 027 of 500, numbered to match: "Set No. 027 / 500 A" under the
   * serial, and B is the set's second racket (its own serial and measured values). Without it the card is a single
   * racket's: its own serial (KQ-000427) and no set line.
   */
  set?: "A" | "B";
  /** Any other edition line under the serial (lab pages); `set` takes precedence. */
  edition?: string;
  /** The buyer's feel (e.g. "Pace") in place of the sample's. */
  feel?: string;
  /** The second racket of a set: its own serial and measured values (identical.card.second). Implied by set "B". */
  second?: boolean;
  /** Rest the card at −3° on wide screens (flat on phones). */
  rotate?: boolean;
  /**
   * "full": the readable card. "thumb": a text-free miniature for small placements (trust list),
   * where text could not stay at 15 px or more.
   */
  variant?: "full" | "thumb";
  /** Slide up 24 px with a fade when it scrolls into view. Default true. */
  enter?: boolean;
  /** The graphite mount plate behind the card. Default true; a set of cards shares one soft shadow instead. */
  plate?: boolean;
  /**
   * The back card of a set, of which only the top shows: header and serial with the set number, and nothing below
   * (no title, rows or map), so the strip beside the front card is clean paper, never clipped values.
   */
  peek?: boolean;
  /**
   * A tighter rhythm on a narrow card (below 340 px, where the text sits at its floor), so a set's two cards fit a
   * phone's 4:5 gallery frame whole: the /reserve gallery only.
   */
  dense?: boolean;
};

function SwissCross({ className }: { className?: string }) {
  // Flag proportions: arms 6 wide, reaching 7 beyond the 6 x 6 centre, on a 32 unit square.
  return (
    <svg className={className} viewBox="0 0 32 32" aria-hidden="true" focusable="false">
      <rect width="32" height="32" fill="var(--swiss)" />
      <path d="M13 6h6v7h7v6h-7v7h-6v-7H6v-6h7z" fill="#fff" />
    </svg>
  );
}

function FlatnessMap({ uid }: { uid: string }) {
  const clip = `${uid}-head`;
  return (
    <svg className={styles.mapSvg} viewBox={mapViewBox} aria-hidden="true" focusable="false">
      <defs>
        <clipPath id={clip}>
          <path d={`${headOutline}${throatOutline}`} clipRule="evenodd" />
        </clipPath>
      </defs>
      <g clipPath={`url(#${clip})`}>
        {flatness.map((c) => (
          <path key={c.level} className={styles.contour} data-level={c.level} d={c.d} vectorEffect="non-scaling-stroke" />
        ))}
      </g>
      <path className={styles.headLine} d={`${headOutline}${throatOutline}`} vectorEffect="non-scaling-stroke" />
      {holeDots.map((h) => (
        <circle key={`${h.cx},${h.cy}`} className={styles.hole} cx={h.cx} cy={h.cy} r={h.r} vectorEffect="non-scaling-stroke" />
      ))}
    </svg>
  );
}

function Rosette({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="-100 -100 200 200" aria-hidden="true" focusable="false">
      {rosetteTurns.map((deg) => (
        <path key={deg} d={rosetteWave} transform={`rotate(${deg.toFixed(3)})`} vectorEffect="non-scaling-stroke" />
      ))}
      <circle r="52" vectorEffect="non-scaling-stroke" />
      <circle r="97" vectorEffect="non-scaling-stroke" />
    </svg>
  );
}

/**
 * G08, the certificate of measurement. A6 card on paper stock with ink text: header, serial,
 * measured rows in tabular numerals, a flatness contour map with the 42 holes, the Swiss cross and
 * a blank signature line. Server render and reduced motion show it in place; motion slides it up
 * 24 px with a fade on entry; fine pointers straighten and lift it on hover (CSS).
 */
export function MeasurementCard({
  className,
  set,
  edition: editionLine,
  feel,
  second: secondRacket = false,
  rotate = false,
  variant = "full",
  enter = true,
  plate = true,
  peek = false,
  dense = false,
}: Props) {
  const root = useRef<HTMLElement>(null);
  const { motionOn } = useMotion();
  const uid = `g08${useId().replace(/[^a-zA-Z0-9]/g, "")}`;
  const thumb = variant === "thumb";

  useGSAP(
    () => {
      if (!enter || !motionOn || !root.current) return;
      const el = root.current;
      const mm = gsap.matchMedia();
      mm.add("(prefers-reduced-motion: no-preference)", () => {
        gsap.fromTo(
          el.querySelector("[data-g08-mover]"),
          { y: 24, opacity: 0 },
          { y: 0, opacity: 1, duration: 0.3, ease: "power3.out", scrollTrigger: { trigger: el, start: "top 88%", once: true } },
        );
      });
      return () => mm.revert();
    },
    { scope: root, dependencies: [motionOn, enter], revertOnUpdate: true },
  );

  const second = secondRacket || set === "B";
  const edition = set ? sampleSet.card(set) : editionLine;
  const sample = second ? card.second : null;
  const serial = sample?.serial ?? card.serial;
  const rows = card.rows.map(([k, v]): [string, string] => [k, k === "Feel" && feel ? feel : (sample?.values[k] ?? v)]);
  const deviationKey = rows[rows.length - 1][0];

  return (
    <figure
      ref={root}
      className={`${styles.root}${className ? ` ${className}` : ""}`}
      data-rotate={rotate ? "" : undefined}
      data-variant={variant}
      data-plate={plate ? undefined : "none"}
      data-peek={peek ? "" : undefined}
      data-dense={dense ? "" : undefined}
      aria-hidden={thumb ? true : undefined}
    >
      <div className={styles.mover} data-g08-mover="">
        {/* the tilt carries card and plate together, so the plate always sits square behind the card */}
        <div className={styles.tilt}>
          {plate ? <div className={styles.plate} aria-hidden="true" /> : null}
          <div className={styles.card}>
            <div className={styles.rosetteClip} aria-hidden="true">
              <Rosette className={styles.rosette} />
            </div>

            {/* text-free miniature: the card's structure as fine strokes, never solid redaction bars */}
            {peek ? null : (
              <div className={styles.thumbBody} aria-hidden="true">
                <span className={styles.thumbHead}>
                  <span className={styles.thumbMark} />
                  <span className={styles.thumbTag} />
                </span>
                <span className={styles.thumbTitle} />
                <span className={styles.thumbTitle2} />
                <span className={styles.thumbRows}>
                  {rows.map(([k]) => (
                    <span key={k} className={styles.thumbRow}>
                      <span className={styles.thumbKey} />
                      <span className={styles.thumbValue} />
                    </span>
                  ))}
                </span>
                <span className={styles.thumbFoot}>
                  <span className={styles.thumbMap}>
                    <FlatnessMap uid={`${uid}t`} />
                  </span>
                  <span className={styles.thumbSide}>
                    <SwissCross className={styles.thumbCross} />
                    <span className={styles.thumbSign} />
                  </span>
                </span>
              </div>
            )}
            {thumb ? null : peek ? (
              <div className={styles.fullBody}>
                <header className={styles.top}>
                  <span className={styles.wordmark}>{LABELS.wordmark}</span>
                  <span className={styles.tag}>{card.tag}</span>
                </header>
                <p className={`${styles.meta} ${styles.peekMeta}`}>
                  <span>
                    <span className={styles.metaKey}>{LABELS.serial}</span> <span className={styles.metaValue}>{serial}</span>
                  </span>
                  {edition ? <span className={styles.edition}>{edition}</span> : null}
                </p>
              </div>
            ) : (
              <div className={styles.fullBody}>
                <header className={styles.top}>
                  <span className={styles.wordmark}>{LABELS.wordmark}</span>
                  <span className={styles.tag}>{card.tag}</span>
                </header>
                <p className={styles.title}>{card.title}</p>
                <p className={styles.meta}>
                  <span>
                    <span className={styles.metaKey}>{LABELS.serial}</span> <span className={styles.metaValue}>{serial}</span>
                  </span>
                  {edition ? <span className={styles.edition}>{edition}</span> : null}
                </p>

                <dl className={styles.rows}>
                  {rows.map(([k, v]) => (
                    <div key={k} className={styles.row}>
                      <dt>{k}</dt>
                      <dd>
                        {v}
                        {k === deviationKey ? <span className={styles.limit}>{LABELS.limit}</span> : null}
                      </dd>
                    </div>
                  ))}
                </dl>

                <div className={styles.foot}>
                  <div className={styles.map}>
                    <FlatnessMap uid={uid} />
                  </div>
                  <div className={styles.side}>
                    <div className={styles.legend} aria-hidden="true">
                      <span className={styles.legendTitle}>{LABELS.mapTitle}</span>
                      <span className={styles.legendScale}>
                        <span>{LABELS.mapScaleFrom}</span>
                        <span className={styles.legendBar} />
                        <span>{LABELS.mapScaleTo}</span>
                      </span>
                    </div>
                    <p className={styles.swiss}>
                      <SwissCross className={styles.cross} />
                      <span>{card.swiss}</span>
                    </p>
                    <p className={styles.sign}>
                      <span className={styles.signLine} aria-hidden="true" />
                      <span className={styles.signLabel}>{LABELS.signature}</span>
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
      {thumb ? null : <figcaption className="visually-hidden">{LABELS.summary}</figcaption>}
    </figure>
  );
}
