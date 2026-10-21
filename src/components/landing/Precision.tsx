"use client";

import { ToleranceGraph } from "@/components/graphics/ToleranceGraph";
import { Still } from "@/components/media/Still";
import { PinnedChapter } from "@/components/motion/PinnedChapter";
import { precision } from "@/content/copy";
import styles from "./Precision.module.css";

/** Precision: the record numeral counts down to 15 µm as a scan line crosses the racket, then the graph. */
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
          const out = document.querySelector<HTMLElement>(`.${styles.value}`);
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
            .fromTo(`.${styles.scan}`, { xPercent: 0, opacity: 1 }, { xPercent: 100, duration: 0.85 }, 0)
            .to(`.${styles.scan}`, { opacity: 0, duration: 0.1 }, 0.85)
            .from(`.${styles.line}`, { opacity: 0, y: 12, duration: 0.1 }, 0.82)
            .to({}, { duration: 0.1 });
          return () => {
            if (out) out.textContent = String(record.to);
          };
        }}
      >
        <div className={styles.stage}>
          <div className={styles.media} aria-hidden="true">
            <Still id="K05" phoneCrop="portrait" alt="" className={styles.still} />
          </div>
          <div className={styles.scanTrack} aria-hidden="true">
            <span className={styles.scan} />
          </div>
          <h2 id="precision-record" className={styles.record}>
            <span className={`t-record ${styles.number}`}>
              <span className={styles.value}>{record.to}</span>
              <span className={`t-unit ${styles.unit}`}>{record.unit}</span>
            </span>
            <span className="visually-hidden">: {precision.headline}</span>
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
