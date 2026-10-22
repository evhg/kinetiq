import { VibrationGraph } from "@/components/graphics/VibrationGraph";
import { feel } from "@/content/copy";
import { Reveal } from "./Reveal";
import styles from "./Feel.module.css";

/**
 * Feel, right after its cause (the Unibody chapter, whose Skip link lands here, so it takes focus): the vibration
 * graph, with three reasons the racket feels as it does.
 */
export function Feel() {
  return (
    <section id="feel" tabIndex={-1} className={`lift ${styles.section}`} aria-labelledby="feel-title">
      <Reveal className={styles.head}>
        <h2 id="feel-title" className="t-h2">
          {feel.headline}
        </h2>
        <p className="t-lead">{feel.body}</p>
      </Reveal>
      <div className={styles.graph}>
        <VibrationGraph />
      </div>
      <Reveal as="ul" className={`pool ${styles.points}`}>
        {feel.points.map((p) => (
          <li key={p.title} className={styles.point}>
            <h3 className="t-h3">{p.title}</h3>
            <p className="t-body">{p.body}</p>
          </li>
        ))}
      </Reveal>
    </section>
  );
}
