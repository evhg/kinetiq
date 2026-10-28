import { TechnicalDrawing } from "@/components/graphics/TechnicalDrawing";
import { specifications } from "@/content/copy";
import { Reveal } from "./Reveal";
import styles from "./Specifications.module.css";

/**
 * Specifications, the whole racket in numbers, just before the editions (since 2026-10-28, after Two feels): the claim and its lead, six numbers (three by two, two by
 * three on phones), then the engineering drawing that backs them, whole and in its own band: the full sheet with
 * its title block on wide screens, the dimensioned front view on narrow ones.
 */
export function Specifications() {
  return (
    <section id="specifications" className={`lift ${styles.section}`} aria-labelledby="specifications-title">
      <hr className={`lightline ${styles.line}`} />
      <Reveal className={styles.head}>
        <div className={styles.claim}>
          <p className="t-eyebrow">{specifications.eyebrow}</p>
          <h2 id="specifications-title" className="t-h2">
            {specifications.headline}
          </h2>
        </div>
        <p className="t-lead">{specifications.lead}</p>
      </Reveal>
      <Reveal as="dl" className={styles.grid} items={`.${styles.cell}`}>
        {specifications.cells.map((s) => (
          <div key={s.label} className={styles.cell}>
            <dt className={`t-label ${styles.label}`}>{s.label}</dt>
            <dd className={`t-stat ${styles.value}`}>
              {s.value}
              {s.unit ? <span className="t-unit">{s.unit}</span> : null}
            </dd>
          </div>
        ))}
      </Reveal>
      <div className={styles.drawing}>
        <TechnicalDrawing variant="full" className={styles.wide} />
        <TechnicalDrawing variant="front" className={styles.narrow} />
      </div>
    </section>
  );
}
