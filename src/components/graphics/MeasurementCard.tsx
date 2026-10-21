"use client";

import { useId, useRef } from "react";
import { useMotion } from "@/components/motion/MotionProvider";
import { identical } from "@/content/copy";
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
  /** Limited edition line, e.g. "Edition No. 017 / 500" (Tier 2). */
  edition?: string;
  /** Rest the card at −3° on wide screens (flat on phones). */
  rotate?: boolean;
  /**
   * "full": the readable card. "thumb": a text-free miniature for small placements (trust list),
   * where text could not stay at 15 px or more.
   */
  variant?: "full" | "thumb";
  /** Slide up 24 px with a fade when it scrolls into view. Default true. */
  enter?: boolean;
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
export function MeasurementCard({ className, edition, rotate = false, variant = "full", enter = true }: Props) {
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

  const rows = card.rows;
  const deviationKey = rows[rows.length - 1][0];

  return (
    <figure
      ref={root}
      className={`${styles.root}${className ? ` ${className}` : ""}`}
      data-rotate={rotate ? "" : undefined}
      data-variant={variant}
      aria-hidden={thumb ? true : undefined}
    >
      <div className={styles.mover} data-g08-mover="">
        <div className={styles.plate} aria-hidden="true" />
        <div className={styles.card}>
          <Rosette className={styles.rosette} />

          {thumb ? (
            <div className={styles.thumbBody} aria-hidden="true">
              <span className={styles.thumbBar} />
              <span className={styles.thumbBarWide} />
              {rows.map(([k]) => (
                <span key={k} className={styles.thumbRow} />
              ))}
              <div className={styles.thumbFoot}>
                <div className={styles.map}>
                  <FlatnessMap uid={uid} />
                </div>
                <SwissCross className={styles.cross} />
              </div>
            </div>
          ) : (
            <>
              <header className={styles.top}>
                <span className={styles.wordmark}>{LABELS.wordmark}</span>
                <span className={styles.tag}>{card.tag}</span>
              </header>
              <p className={styles.title}>{card.title}</p>
              <p className={styles.meta}>
                <span>
                  <span className={styles.metaKey}>{LABELS.serial}</span> <span className={styles.metaValue}>{card.serial}</span>
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
                <div className={styles.mapBlock}>
                  <div className={styles.map}>
                    <FlatnessMap uid={uid} />
                  </div>
                  <div className={styles.legend} aria-hidden="true">
                    <span className={styles.legendTitle}>{LABELS.mapTitle}</span>
                    <span className={styles.legendScale}>
                      <span>{LABELS.mapScaleFrom}</span>
                      <span className={styles.legendBar} />
                      <span>{LABELS.mapScaleTo}</span>
                    </span>
                  </div>
                </div>
                <div className={styles.side}>
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
            </>
          )}
        </div>
      </div>
      {thumb ? null : <figcaption className="visually-hidden">{LABELS.summary}</figcaption>}
    </figure>
  );
}
