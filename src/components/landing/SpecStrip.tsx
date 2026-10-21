import { TechnicalDrawing } from "@/components/graphics/TechnicalDrawing";
import { specStrip } from "@/content/copy";
import { Reveal } from "./Reveal";
import styles from "./SpecStrip.module.css";

/**
 * Four numbers on one line of light, then the engineering drawing that backs them, whole and in its own
 * band: the full sheet with its title block on wide screens, the dimensioned front view on narrow ones.
 */
export function SpecStrip() {
  return (
    <section className={`lift ${styles.strip}`} aria-label="Specifications">
      <hr className={`lightline ${styles.line}`} />
      <Reveal as="dl" className={styles.grid} items={`.${styles.cell}`}>
        {specStrip.map((s) => (
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
