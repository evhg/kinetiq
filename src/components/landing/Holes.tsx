"use client";

import { DrilledVsMoulded } from "@/components/graphics/DrilledVsMoulded";
import { Still } from "@/components/media/Still";
import { holes } from "@/content/copy";
import { Reveal } from "./Reveal";
import { Scrub } from "./Scrub";
import styles from "./Holes.module.css";

/** 42 moulded holes: the macro (weave wrapping one hole wall), then drilled against moulded. */
export function Holes() {
  return (
    <>
      <Scrub
        id="holes"
        aria-labelledby="holes-title"
        className={styles.band}
        start="top bottom"
        end="bottom top"
        build={(tl) => {
          tl.fromTo(`.${styles.media}`, { yPercent: -3 }, { yPercent: 3, duration: 1 }, 0).fromTo(
            `.${styles.ring}`,
            { opacity: 0 },
            { opacity: 1, duration: 0.4 },
            0.1,
          );
        }}
      >
        <div className={styles.media} aria-hidden="true">
          <Still id="K04-base" phoneCrop="card" alt="" className={styles.layer} />
          <Still id="K04-full" phoneCrop="card" alt="" className={`${styles.layer} ${styles.ring}`} />
        </div>
        <Reveal className={styles.copy}>
          <h2 id="holes-title" className="t-h2">
            {holes.headline}
          </h2>
          <p className="t-lead">{holes.body}</p>
          <dl className={styles.stats}>
            {holes.stats.map((s) => (
              <div key={s.label} className={styles.stat}>
                <dt className={`t-label ${styles.statLabel}`}>{s.label}</dt>
                <dd className={`t-stat ${styles.statValue}`}>{s.value}</dd>
              </div>
            ))}
          </dl>
        </Reveal>
      </Scrub>
      <section className={`lift ${styles.pair}`} aria-label="Drilled holes compared with moulded holes">
        <DrilledVsMoulded />
      </section>
    </>
  );
}
