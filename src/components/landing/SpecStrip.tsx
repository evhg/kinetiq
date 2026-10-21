import { TechnicalDrawing } from "@/components/graphics/TechnicalDrawing";
import { specStrip } from "@/content/copy";
import { Reveal } from "./Reveal";
import styles from "./SpecStrip.module.css";

/** Four numbers on one line of light, over the engineering drawing. */
export function SpecStrip() {
  return (
    <section className={`lift ${styles.strip}`} aria-label="Specifications">
      <hr className={`lightline ${styles.line}`} />
      <div className={styles.drawing} aria-hidden="true">
        <TechnicalDrawing variant="full" tone="quiet" className={styles.wide} />
        <TechnicalDrawing variant="front" tone="quiet" annotate={false} titleBlock={false} className={styles.narrow} />
      </div>
      <Reveal as="dl" className={styles.grid} items={`.${styles.cell}`}>
        {specStrip.map((s) => (
          <div key={s.label} className={styles.cell}>
            <dt className={`t-stat ${styles.value}`}>
              {s.value}
              {s.unit ? <span className="t-unit">{s.unit}</span> : null}
            </dt>
            <dd className={`t-label ${styles.label}`}>{s.label}</dd>
          </div>
        ))}
      </Reveal>
    </section>
  );
}
