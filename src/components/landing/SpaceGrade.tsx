"use client";

import { Still } from "@/components/media/Still";
import { spaceGrade } from "@/content/copy";
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
 * Under the three points, the spec sheet (owner, 2026-11-02): mechanical, thermal and environmental, each figure with
 * the method that measures it, ruled like an Apple tech-specs page (specs.ts; provisional until the factory's values).
 * Not pinned.
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
          </li>
        ))}
      </Reveal>
      <SpecSheet />
    </Scrub>
  );
}

/** The spec sheet: a heading and one line, then a group per discipline, each row a term, its figure and its method. */
function SpecSheet() {
  const { sheet } = spaceGrade;
  return (
    <section className={styles.sheet} aria-labelledby="space-grade-specs">
      <Reveal className={styles.sheetHead}>
        <p className="t-eyebrow">{sheet.eyebrow}</p>
        <h3 id="space-grade-specs" className={`t-h3 ${styles.sheetTitle}`}>
          {sheet.headline}
        </h3>
        <p className="t-body">{sheet.lead}</p>
      </Reveal>
      <div className={styles.groups}>
      {sheet.groups.map((g) => (
        <section key={g.id} className={styles.group} aria-labelledby={`spec-${g.id}`}>
          <h4 id={`spec-${g.id}`} className={`t-label ${styles.groupTitle}`}>
            {g.title}
          </h4>
          <Reveal as="dl" className={styles.rows} items={`.${styles.row}`} stagger={0.04} y={10}>
            {g.specs.map((s) => (
              <div key={s.id} className={styles.row} data-provisional={s.provisional ? "" : undefined}>
                <dt className={styles.term}>
                  <span className={styles.termLabel}>{s.label}</span>
                  {s.note ? <span className={`t-fine ${styles.note}`}>{s.note}</span> : null}
                </dt>
                <dd className={`t-stat ${styles.figure}`}>
                  {s.bound ? <span className={styles.bound}>{`${s.bound}\u00a0`}</span> : null}
                  {s.value}
                  {s.unit ? <span className="t-unit">{s.unit}</span> : null}
                </dd>
                <dd className={`t-fine t-num ${styles.method}`}>
                  <span className="visually-hidden">{`${sheet.methodLabel}: `}</span>
                  {s.method}
                </dd>
              </div>
            ))}
          </Reveal>
        </section>
      ))}
      </div>
    </section>
  );
}
