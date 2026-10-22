import { GluedSection, KinetiqSection, SectionComparison } from "@/components/graphics/SectionComparison";
import { unibody } from "@/content/copy";
import styles from "./page.module.css";

const section = { paddingBlock: "clamp(64px, 8vw, 200px)" } as const;
const head = { marginBottom: "clamp(32px, 3vw, 72px)", display: "grid", gap: "12px", justifyItems: "center", textAlign: "center" } as const;

// Review page for G07. First: the pair as a plain comparison (plays once on entry). Second: the two
// drawings in the left and right thirds around the K03 photo, as beat B of the Unibody chapter.
export default function LabG07() {
  return (
    <>
      <section className="lift tech-grid" style={section}>
        <div className="wrap">
          <div style={head}>
            <p className="t-eyebrow">{unibody.section.eyebrow}</p>
            <h2 className="t-h2">{unibody.section.headline}</h2>
          </div>
          <SectionComparison play />
        </div>
      </section>

      <section className="lift tech-grid" style={section}>
        <div className="wrap">
          <div style={head}>
            <p className="t-eyebrow">G07 in the thirds around K03</p>
          </div>
          <div className={styles.thirds}>
            <GluedSection play />
            <div className={styles.photo} aria-hidden="true">
              K03
            </div>
            <KinetiqSection play />
          </div>
        </div>
      </section>
    </>
  );
}
