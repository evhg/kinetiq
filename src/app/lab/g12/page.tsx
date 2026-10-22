import { CourtPlan } from "@/components/graphics/CourtPlan";
import { tiers } from "@/content/lineup";
import styles from "./page.module.css";

const section = { paddingBlock: "clamp(64px, 8vw, 200px)" } as const;
const head = { marginBottom: "clamp(32px, 3vw, 72px)", display: "grid", gap: "12px", justifyItems: "center", textAlign: "center" } as const;

// Review page for G12: the reserve gallery's One of Ten slide 2 in both shapes, then the extras thumbnail.
const invite = tiers.find((t) => t.id === "invite")?.name;
export default function LabG12() {
  return (
    <section className="lift tech-grid" style={section}>
      <div className="wrap">
        <div style={head}>
          <p className="t-eyebrow">G12 Coaching court plan</p>
          <h2 className="t-h2">{invite}, slide 2</h2>
        </div>
        <div className={styles.grid}>
          <div className={styles.wide}>
            <CourtPlan aspect="16:10" className={styles.slide} />
          </div>
          <div className={styles.tall}>
            <CourtPlan aspect="4:5" className={styles.slide} />
          </div>
          <div className={styles.thumbs}>
            <CourtPlan aspect="4:5" className={styles.thumb} />
            <CourtPlan aspect="16:10" className={styles.thumb} />
          </div>
        </div>
      </div>
    </section>
  );
}
