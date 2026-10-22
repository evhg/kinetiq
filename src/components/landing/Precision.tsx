"use client";

import { ToleranceGraph } from "@/components/graphics/ToleranceGraph";
import { Still } from "@/components/media/Still";
import { PinnedChapter } from "@/components/motion/PinnedChapter";
import { precision } from "@/content/copy";
import styles from "./Precision.module.css";

/**
 * Precision: the record numeral counts down to 15 µm while the laser-scan still (K05) settles, then the graph. The
 * line under the numeral fades in as the count lands, so it never sits under a number it does not describe.
 */
export function Precision() {
  const { record } = precision;
  // While pinned, the numeral sits in a box as wide as its longest value, so the count never shifts it; a
  // matching ghost after the unit keeps the final reading centred (Precision.module.css).
  const digits = String(Math.max(record.from, record.to)).length;
  return (
    <>
      <PinnedChapter
        id="precision"
        nextId="precision-graph"
        labelledBy="precision-record"
        className={styles.chapter}
        length={1.2}
        build={(tl) => {
          const out = document.querySelector<HTMLElement>(`.${styles.digits}`);
          const counter = { v: record.from };
          tl.fromTo(
            counter,
            { v: record.from },
            {
              v: record.to,
              duration: 0.85,
              ease: "power2.out",
              onUpdate: () => {
                if (out) out.textContent = String(Math.round(counter.v));
              },
            },
            0,
          )
            .fromTo(`.${styles.media}`, { scale: 1.08 }, { scale: 1, duration: 0.85, ease: "power2.out" }, 0)
            .from(`.${styles.line}`, { opacity: 0, y: 12, duration: 0.23 }, 0.62)
            .to({}, { duration: 0.1 }, 0.92);
          return () => {
            if (out) out.textContent = String(record.to);
          };
        }}
      >
        <div className={styles.stage}>
          <div className={styles.media} aria-hidden="true">
            <Still id="K05" phoneId="K05-phone" phoneCrop="portrait" alt="" className={styles.still} />
          </div>
          <h2 id="precision-record" className={styles.record}>
            <span className={`t-record ${styles.number}`} aria-hidden="true">
              <span className={styles.value}>
                <span className={styles.ghost}>{"0".repeat(digits)}</span>
                <span className={styles.digits}>{record.to}</span>
              </span>
              <span className={`t-unit ${styles.unit}`}>{record.unit}</span>
              <span className={styles.ghost}>{"0".repeat(digits - String(record.to).length)}</span>
            </span>
            {/* Spoken once and in words: the graph section's own h2 says the headline. */}
            <span className="visually-hidden">{`${record.to} ${record.spokenUnit}`}</span>
          </h2>
          <p className={`t-lead ${styles.line}`}>{precision.recordLine}</p>
        </div>
      </PinnedChapter>

      <section id="precision-graph" tabIndex={-1} className={`lift tech-grid ${styles.graphSection}`} aria-labelledby="precision-title">
        <div className={styles.head}>
          <h2 id="precision-title" className="t-h2">
            {precision.headline}
          </h2>
          <p className="t-lead">{precision.body}</p>
        </div>
        <ToleranceGraph />
      </section>
    </>
  );
}
