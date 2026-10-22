"use client";

import { ToleranceGraph } from "@/components/graphics/ToleranceGraph";
import { Still } from "@/components/media/Still";
import { PinnedChapter } from "@/components/motion/PinnedChapter";
import { precision } from "@/content/copy";
import styles from "./Precision.module.css";

/**
 * Precision: the record "15 µm" and its line, then the graph. The numeral never counts: a count can be paused on a
 * value that is not the claim. Pinned, the scrub settles the laser-scan still (K05, scale 1.08 to 1) and brings the
 * numeral and its line in together near the start, so from then on they always read as a pair. The server render and
 * reduced motion show the final state.
 */
export function Precision() {
  const { record } = precision;
  return (
    <>
      <PinnedChapter
        id="precision"
        nextId="precision-graph"
        labelledBy="precision-record"
        className={styles.chapter}
        length={1.2}
        build={(tl) => {
          tl.fromTo(`.${styles.media}`, { scale: 1.08 }, { scale: 1, duration: 0.85, ease: "power2.out" }, 0)
            .from(`.${styles.number}, .${styles.line}`, { opacity: 0, y: 16, duration: 0.16, ease: "power2.out" }, 0.02)
            .to({}, { duration: 0.1 }, 0.92);
        }}
      >
        <div className={styles.stage}>
          <div className={styles.media} aria-hidden="true">
            <Still id="K05" phoneId="K05-phone" phoneCrop="portrait" alt="" className={styles.still} />
          </div>
          <h2 id="precision-record" className={styles.record}>
            <span className={`t-record ${styles.number}`} aria-hidden="true">
              {record.to}
              <span className={`t-unit ${styles.unit}`}>{record.unit}</span>
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
