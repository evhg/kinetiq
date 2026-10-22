import { LifespanGraph } from "@/components/graphics/LifespanGraph";
import { durability } from "@/content/copy";
import styles from "./page.module.css";

// Review page for G14: the lifespan comparison at the full content width, then beside its copy on
// columns 6 to 12, as in the Durability section.
export default function LabG14() {
  return (
    <section className="lift tech-grid" style={{ paddingBlock: "clamp(64px, 8vw, 200px)" }}>
      <div className={`wrap ${styles.full}`}>
        <h2 className="t-h2" style={{ textAlign: "center" }}>
          {durability.headline}
        </h2>
        <LifespanGraph />
      </div>
      <div className={`wrap ${styles.grid}`}>
        <div className={styles.copy}>
          <p className="t-eyebrow">{durability.eyebrow}</p>
          <h2 className="t-h2">{durability.headline}</h2>
          <p className="t-lead">{durability.lead}</p>
        </div>
        <LifespanGraph className={styles.graphic} />
      </div>
    </section>
  );
}
