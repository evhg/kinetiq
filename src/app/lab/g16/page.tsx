import { CarbonLayup } from "@/components/graphics/CarbonLayup";
import { spaceGrade } from "@/content/copy";

// Review page for G16: the two cross-sections at the full content width, then in the 7 of 12 columns the Space-grade
// carbon section gives it from 1000 px, then at a phone's measure; the text alternative is printed under them.
export default function LabG16() {
  return (
    <section className="lift tech-grid" style={{ paddingBlock: "clamp(64px, 8vw, 200px)", display: "grid", gap: 96 }}>
      <div className="wrap">
        <h2 className="t-h2" style={{ marginBottom: 32 }}>
          {spaceGrade.headline}
        </h2>
        <CarbonLayup />
      </div>
      <div className="wrap" style={{ maxWidth: "58vw" }}>
        <CarbonLayup />
      </div>
      <div className="wrap" style={{ maxWidth: 390 }}>
        <CarbonLayup />
      </div>
      <p className="wrap t-body" style={{ maxWidth: "70ch", color: "var(--muted)" }}>
        {spaceGrade.graphic.alt}
      </p>
    </section>
  );
}
