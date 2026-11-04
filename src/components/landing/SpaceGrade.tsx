"use client";

import { Still } from "@/components/media/Still";
import { spaceGrade } from "@/content/copy";
import { spec } from "@/content/specs";
import { Reveal } from "./Reveal";
import { Scrub } from "./Scrub";
import styles from "./SpaceGrade.module.css";

/**
 * Space-grade carbon (owner, 2026-10-23), right after Unibody: what the racket is made of, before the mould that makes
 * it (Born whole). Owner, 2026-10-29: "rather show a piece of great looking carbon in a space setting", so K15 carries
 * the section, full bleed above the words: the racket's crown in white 3K twill (black 12K in Pace) floating over a
 * planet's limb. Two passes of one render: K15-base (before sunrise: the limb's glow on the edge) and K15-full (the sun
 * on the weave). As the section scrolls in, the sun comes up: the lit pass fades in over the base and the frame settles
 * (scale 1.06 to 1). Server render and reduced motion: the lit pass, at rest. G16 (CarbonLayup) lives on in /lab/g16.
 * Under each of the three points, the numbers that back it (owner, 2026-11-03: "the Carbon specs is too much, doesn't
 * need its own section"; it replaced the 2026-11-02 spec sheet): three figures in the stat face, each with its term and
 * the test method that measures it (specs.ts; provisional until the factory's values). Not pinned.
 */
export function SpaceGrade() {
  return (
    <Scrub
      id="space-grade"
      aria-labelledby="space-grade-title"
      className={styles.section}
      start="top 92%"
      end="top 12%"
      build={(tl) => {
        tl.fromTo(`.${styles.media}`, { scale: 1.06 }, { scale: 1, duration: 1 }, 0).fromTo(
          `.${styles.sun}`,
          { opacity: 0 },
          { opacity: 1, duration: 0.7, ease: "power1.inOut" },
          0.15,
        );
      }}
    >
      <div className={styles.band} aria-hidden="true">
        <div className={styles.media}>
          <Still id="K15-base" phoneCrop="card" alt="" sizes="100vw" className={styles.layer} />
          <Still id="K15-full" phoneCrop="card" alt="" sizes="100vw" className={`${styles.layer} ${styles.sun}`} />
        </div>
      </div>
      <div className={styles.grid}>
        <Reveal className={styles.head}>
          <p className="t-eyebrow">{spaceGrade.eyebrow}</p>
          <h2 id="space-grade-title" className="t-h2">
            {spaceGrade.headline}
          </h2>
        </Reveal>
        <Reveal className={styles.lead} y={12}>
          <p className="t-lead">{spaceGrade.lead}</p>
        </Reveal>
      </div>
      <Reveal as="ul" className={`pool ${styles.points}`}>
        {spaceGrade.points.map((p) => (
          <li key={p.title} className={styles.point}>
            <h3 className="t-h3">{p.title}</h3>
            <p className="t-body">{p.body}</p>
            <Figures ids={p.figures} />
          </li>
        ))}
      </Reveal>
    </Scrub>
  );
}

/**
 * A point's figures: each the number in the stat face (a bound, "≥" or "≤", muted and a step down; the unit in
 * t-unit), its term, then its test method. A description list, the term first; the number is set above it.
 */
function Figures({ ids }: { ids: string[] }) {
  return (
    <dl className={styles.figures}>
      {ids.map((id) => {
        const s = spec(id);
        return (
          <div key={id} className={styles.figure}>
            <dt className={`t-label ${styles.term}`}>{s.label}</dt>
            <dd className={`t-stat ${styles.value}`}>
              {s.bound ? <span className={styles.bound}>{`${s.bound}\u00a0`}</span> : null}
              {s.value}
              {s.unit ? <span className="t-unit">{s.unit}</span> : null}
            </dd>
            <dd className={`t-fine ${styles.method}`}>
              <span className="visually-hidden">{`${spaceGrade.methodLabel}: `}</span>
              {s.method}
              {s.note ? <span className={styles.note}>{s.note}</span> : null}
            </dd>
          </div>
        );
      })}
    </dl>
  );
}
