import { FibreFlow } from "@/components/graphics/FibreFlow";
import { holes } from "@/content/copy";
import styles from "./lab.module.css";

// Review page for G05: the full-bleed band (copy on the left, the field fading under it), as it
// sits over K04 in the Holes chapter, then the 390 x 260 phone strip on its own.
export default function LabG05() {
  return (
    <>
      <section className={`lift tech-grid ${styles.band}`} aria-labelledby="g05-title">
        <div className={styles.flow} aria-hidden="true">
          <FibreFlow fadeSide="left" decorative />
        </div>
        <div className={`wrap ${styles.copy}`}>
          <h2 id="g05-title" className="t-h2">
            {holes.headline}
          </h2>
          <p className="t-body">{holes.body}</p>
        </div>
        <div className={styles.phoneFlow} aria-hidden="true">
          <FibreFlow mode="strip" decorative />
        </div>
      </section>
      <section className={`lift tech-grid ${styles.stripSection}`}>
        <div className="wrap">
          <p className={`t-label ${styles.note}`}>Phone strip, 390 × 260</p>
          <div className={styles.stripBox}>
            <FibreFlow mode="strip" />
          </div>
        </div>
      </section>
    </>
  );
}
