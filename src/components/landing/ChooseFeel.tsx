import { Still } from "@/components/media/Still";
import { feelChoice } from "@/content/copy";
import { Reveal } from "./Reveal";
import styles from "./ChooseFeel.module.css";

/** Two feels, side by side: Command (3K) and Pace (12K). */
export function ChooseFeel() {
  return (
    <section id="feels" className={styles.section} aria-labelledby="feels-title">
      <Reveal className={styles.intro}>
        <p className="t-eyebrow">{feelChoice.eyebrow}</p>
        <h2 id="feels-title" className="t-h2">
          {feelChoice.headline}
        </h2>
      </Reveal>
      <div className={styles.panels}>
        {feelChoice.feels.map((f, i) => (
          <article key={f.id} className={styles.panel} aria-labelledby={`feel-${f.id}`}>
            <div className={styles.media} aria-hidden="true">
              <Still id="K08" crop={i === 0 ? "left" : "right"} alt="" sizes="(max-width: 699px) 100vw, 50vw" className={styles.still} />
            </div>
            <p className={`t-label ${styles.sub}`}>{f.sub}</p>
            <div className={styles.text}>
              <h3 id={`feel-${f.id}`} className={styles.name}>
                {f.name}
              </h3>
              <p className="t-lead">{f.line}</p>
              <p className={`t-label ${styles.spec}`}>{f.spec}</p>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
