import { ConsistencySpikes } from "@/components/graphics/ConsistencySpikes";
import { identical } from "@/content/copy";
import styles from "./page.module.css";

// Review page for G04: the spikes on columns 1 to 7, as in the Identical chapter, screen 2.
export default function LabG04() {
  return (
    <section className="lift tech-grid" style={{ paddingBlock: "clamp(64px, 8vw, 200px)" }}>
      <div className={`wrap ${styles.grid}`}>
        <ConsistencySpikes className={styles.graphic} />
        <div className={styles.copy}>
          <h2 className="t-h2">{identical.headline}</h2>
          <p className="t-body">{identical.body}</p>
        </div>
      </div>
    </section>
  );
}
