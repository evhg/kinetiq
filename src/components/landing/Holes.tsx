"use client";

import { DrilledVsMoulded } from "@/components/graphics/DrilledVsMoulded";
import { FibreFlow } from "@/components/graphics/FibreFlow";
import { Still } from "@/components/media/Still";
import { holes } from "@/content/copy";
import { Reveal } from "./Reveal";
import { Scrub } from "./Scrub";
import styles from "./Holes.module.css";

/** 42 moulded holes: the macro, the fibre flow around every hole, then drilled against moulded. */
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
        <div className={styles.flow} aria-hidden="true">
          <FibreFlow fadeSide="left" />
        </div>
        <Reveal className={styles.copy}>
          <h2 id="holes-title" className="t-h2">
            {holes.headline}
          </h2>
          <p className="t-body">{holes.body}</p>
          <dl className={styles.stats}>
            {holes.stats.map((s) => (
              <div key={s.label}>
                <dt className={`t-stat ${styles.statValue}`}>{s.value}</dt>
                <dd className={`t-label ${styles.statLabel}`}>{s.label}</dd>
              </div>
            ))}
          </dl>
        </Reveal>
        <div className={styles.phoneFlow} aria-hidden="true">
          <FibreFlow mode="strip" />
        </div>
      </Scrub>
      <section className={`lift ${styles.pair}`} aria-label="Drilled holes compared with moulded holes">
        <DrilledVsMoulded />
      </section>
    </>
  );
}
