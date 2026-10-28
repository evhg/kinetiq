import { LifespanGraph } from "@/components/graphics/LifespanGraph";
import { Hyphens } from "@/components/text/Hyphens";
import { durability } from "@/content/copy";
import { Reveal } from "./Reveal";
import styles from "./Durability.module.css";

/**
 * Durability, the payoff's last beat after the sweet spot and Feel: a sealed core, no seams and no drilled holes. The claim and its lead beside G14
 * (five years against the one to two most padel rackets last), then the four reasons. The only place the page
 * says five years (owner, 2026-10-22); no fine print: the usage profile and the promised tests are point 4.
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
            {/* a hyphenated word ("90-minute") never breaks at its hyphen */}
            <p className="t-body">
              <Hyphens text={p.body} />
            </p>
          </li>
        ))}
      </Reveal>
    </section>
  );
}
