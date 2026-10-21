import { Still } from "@/components/media/Still";
import { feelChoice } from "@/content/copy";
import { Reveal } from "./Reveal";
import styles from "./ChooseFeel.module.css";

/**
 * Two feels: Command (3K) and Pace (12K). On wide screens one K08 frame holds both rackets, split by a
 * hairline, with each feel's words in the band below its racket; phones stack a 4:5 crop of each.
 */
export function ChooseFeel() {
  return (
    <section id="feels" className={styles.section} aria-labelledby="feels-title">
      <Reveal className={styles.intro}>
        <p className="t-eyebrow">{feelChoice.eyebrow}</p>
        <h2 id="feels-title" className="t-h2">
          {feelChoice.headline}
        </h2>
      </Reveal>
      <div className={styles.stage}>
        <div className={styles.wide} aria-hidden="true">
          <Still id="K08" alt="" className={styles.still} />
        </div>
        <div className={styles.panels}>
          {feelChoice.feels.map((f, i) => (
            <article key={f.id} className={styles.panel} aria-labelledby={`feel-${f.id}`}>
              <div className={styles.phoneMedia} aria-hidden="true">
                <Still id="K08" crop={i === 0 ? "left" : "right"} alt="" sizes="100vw" className={styles.still} />
              </div>
              <Reveal className={styles.text}>
                <p className={`t-eyebrow ${styles.sub}`}>{f.sub}</p>
                <h3 id={`feel-${f.id}`} className={styles.name}>
                  {f.name}
                </h3>
                <p className="t-lead">{f.line}</p>
                <p className={`t-label ${styles.spec}`}>{f.spec}</p>
              </Reveal>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
