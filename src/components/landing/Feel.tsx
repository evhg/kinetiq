import { VibrationGraph } from "@/components/graphics/VibrationGraph";
import { feel } from "@/content/copy";
import { Reveal } from "./Reveal";
import styles from "./Feel.module.css";

/** Feel: the vibration graph, with the three reasons it settles. */
export function Feel() {
  return (
    <section id="feel" className={`lift ${styles.section}`} aria-labelledby="feel-title">
      <Reveal className={styles.head}>
        <h2 id="feel-title" className="t-h2">
          {feel.headline}
        </h2>
        <p className="t-lead">{feel.body}</p>
      </Reveal>
      <VibrationGraph />
      <Reveal as="ul" className={styles.points}>
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
