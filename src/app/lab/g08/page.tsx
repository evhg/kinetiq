import { MeasurementCard } from "@/components/graphics/MeasurementCard";
import { identical } from "@/content/copy";
import styles from "./page.module.css";

const section = { paddingBlock: "clamp(64px, 8vw, 200px)" } as const;
const head = { marginBottom: "clamp(32px, 3vw, 72px)", display: "grid", gap: "12px", justifyItems: "center", textAlign: "center" } as const;

// Review page for G08. First: the Identical chapter's second screen, the card in columns 9 to 12,
// resting at -3 degrees. Second: the Tier 2 edition variant (reserve gallery slide 4) and the
// text-free thumbnail for the reserve trust list.
export default function LabG08() {
  return (
    <>
      <section className="lift tech-grid" style={section}>
        <div className="wrap">
          <div style={head}>
            <h2 className="t-h2">{identical.headline}</h2>
            <p className="t-lead">{identical.body}</p>
          </div>
          <div className={styles.grid}>
            <dl className={styles.stats}>
              {identical.stats.map((s) => (
                <div key={s.label} className={styles.stat}>
                  <dt className="t-stat">
                    {s.value}
                    <span className="t-unit">{s.unit}</span>
                  </dt>
                  <dd className="t-label">{s.label}</dd>
                </div>
              ))}
            </dl>
            <MeasurementCard rotate className={styles.card} />
          </div>
        </div>
      </section>

      <section className="lift tech-grid" style={section}>
        <div className="wrap">
          <div style={head}>
            <p className="t-eyebrow">G08 Tier 2 edition card and trust-list thumbnail</p>
          </div>
          <div className={styles.pair}>
            <MeasurementCard edition="Edition No. 017 / 500" className={styles.slide} />
            <div className={styles.thumbs}>
              <MeasurementCard variant="thumb" className={styles.thumb} />
              <MeasurementCard variant="thumb" rotate className={styles.thumb} />
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
