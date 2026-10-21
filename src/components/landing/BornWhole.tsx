"use client";

import { Badges } from "@/components/graphics/Badges";
import { Still } from "@/components/media/Still";
import { bornWhole } from "@/content/copy";
import { Scrub } from "./Scrub";
import styles from "./BornWhole.module.css";

/** The mould: the one image of the process, with the Swiss Made lockup. */
export function BornWhole() {
  return (
    <Scrub
      id="born-whole"
      aria-labelledby="born-whole-title"
      className={styles.section}
      build={(tl) => {
        tl.fromTo(`.${styles.media}`, { scale: 1 }, { scale: 1.06, duration: 1 }, 0)
          .fromTo(`.${styles.glow}`, { opacity: 0.35 }, { opacity: 1, duration: 0.45 }, 0.1)
          .from(`.${styles.lockup} > *`, { opacity: 0, y: 12, stagger: 0.03, duration: 0.12 }, 0.32);
      }}
    >
      <div className={styles.copy}>
        <p className="t-eyebrow">{bornWhole.eyebrow}</p>
        <h2 id="born-whole-title" className="t-h2">
          {bornWhole.headline}
        </h2>
        <p className="t-lead">{bornWhole.body}</p>
      </div>
      {/* The mould gets the whole frame; the lockup sits over the plate's dark front face (y 78-96%). */}
      <div className={styles.stage}>
        <div className={styles.media} aria-hidden="true">
          <Still id="K06-base" phoneCrop="card" alt="" className={styles.layer} />
          <Still id="K06-full" phoneCrop="card" alt="" className={`${styles.layer} ${styles.glow}`} />
        </div>
        <div className={styles.lockup}>
          <p className={styles.swiss}>
            <span className={`t-stat ${styles.pct}`}>{bornWhole.lockup.value}</span>
            <span className={styles.made}>
              <svg viewBox="0 0 32 32" className={styles.cross} aria-hidden="true">
                <rect width="32" height="32" rx="2" fill="var(--swiss)" />
                <path d="M13 6h6v7h7v6h-7v7h-6v-7H6v-6h7z" fill="#fff" />
              </svg>
              {bornWhole.lockup.label}
            </span>
          </p>
          <Badges className={styles.badges} reveal="none" align="center" />
        </div>
      </div>
    </Scrub>
  );
}
