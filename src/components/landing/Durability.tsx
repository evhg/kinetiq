import { LifespanGraph } from "@/components/graphics/LifespanGraph";
import { coreNote, durability, lifeNote } from "@/content/copy";
import { Reveal } from "./Reveal";
import styles from "./Durability.module.css";

/**
 * Durability, after Holes: a sealed core, no seams and no drilled holes. The claim and its lead beside G14
 * (five years against the one to two most padel rackets last), then the four reasons, then the fine print:
 * the usage profile in full (the hero's and finale's footnote markers land on it) and what "three times
 * longer" is measured against (the sealed-core point's marker lands on it).
 */
export function Durability() {
  return (
    <section id="durability" tabIndex={-1} className={styles.section} aria-labelledby="durability-title">
      <div className={styles.grid}>
        <Reveal className={styles.head}>
          <p className="t-eyebrow">{durability.eyebrow}</p>
          <h2 id="durability-title" className="t-h2">
            {durability.headline}
          </h2>
          <p className="t-lead">{durability.lead}</p>
        </Reveal>
        <div className={styles.graph}>
          <LifespanGraph />
        </div>
      </div>
      <Reveal as="ul" className={`pool ${styles.points}`}>
        {durability.points.map((p) => (
          <li key={p.title} className={styles.point}>
            <h3 className="t-h3">{p.title}</h3>
            <p className="t-body">
              {p.body}
              {p.note === "core" ? (
                <a href={`#${coreNote.id}`} className="footmark footmark-raised" aria-label={coreNote.label}>
                  {coreNote.mark}
                </a>
              ) : null}
            </p>
          </li>
        ))}
      </Reveal>
      {/* the usage profile the hero's and finale's markers point to, and the comparison behind the sealed core */}
      <div className={styles.notes}>
        {/* starts with the claim it qualifies, as under the editions: the hero's and finale's markers land here */}
        <p id={lifeNote.id} className={`t-fine ${styles.fine}`}>
          <span className={styles.claim}>
            <span className={styles.mark}>{lifeNote.mark}</span>
            {durability.headline}
          </span>{" "}
          {durability.finePrint}
        </p>
        <p id={coreNote.id} className={`t-fine ${styles.fine}`}>
          <span className={styles.mark}>{coreNote.mark}</span>
          {durability.coreFine}
        </p>
      </div>
    </section>
  );
}
