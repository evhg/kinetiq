import { CarbonLayup } from "@/components/graphics/CarbonLayup";
import { Still, hasStill } from "@/components/media/Still";
import { spaceGrade } from "@/content/copy";
import { Reveal } from "./Reveal";
import styles from "./SpaceGrade.module.css";

/** K13, the carbon layup up close, once the render team's still is exported; until then G16 carries the section. */
const K13 = hasStill("K13");

/**
 * Space-grade carbon (owner, 2026-10-23), the opening of Prove it: what the racket is made of, before the mould that
 * makes it (Born whole). K13 full bleed as the chapter's photograph when it exists; the copy beside G16 (standard
 * carbon against ours, cut through and magnified), then three points. Reads whole without K13. Not pinned.
 */
export function SpaceGrade() {
  return (
    <section id="space-grade" tabIndex={-1} className={styles.section} aria-labelledby="space-grade-title">
      {K13 ? (
        <div className={styles.band} aria-hidden="true">
          <Still id="K13" phoneCrop="card" alt="" sizes="100vw" className={styles.still} />
        </div>
      ) : null}
      <div className={styles.grid}>
        <Reveal className={styles.head}>
          <p className="t-eyebrow">{spaceGrade.eyebrow}</p>
          <h2 id="space-grade-title" className="t-h2">
            {spaceGrade.headline}
          </h2>
          <p className="t-lead">{spaceGrade.lead}</p>
        </Reveal>
        <Reveal className={styles.graph} y={12}>
          <CarbonLayup />
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
    </section>
  );
}
