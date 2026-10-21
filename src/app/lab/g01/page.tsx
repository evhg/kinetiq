import { GhostContour, TechnicalDrawing } from "@/components/graphics/TechnicalDrawing";
import { precision, specStrip } from "@/content/copy";

const section = { paddingBlock: "clamp(64px, 8vw, 200px)" } as const;
const head = { marginBottom: "clamp(32px, 3vw, 72px)", display: "grid", gap: "12px" } as const;

export default function LabG01() {
  return (
    <>
      <section className="lift tech-grid" style={section}>
        <div className="wrap">
          <div style={head}>
            <p className="t-eyebrow">G01 Technical drawing, full sheet</p>
            <h2 className="t-h2">{precision.headline}</h2>
          </div>
          <TechnicalDrawing />
        </div>
      </section>

      <section className="lift tech-grid" style={section}>
        <div className="wrap">
          <div style={head}>
            <p className="t-eyebrow">G01 Quiet tone, behind the spec strip</p>
          </div>
          <TechnicalDrawing tone="quiet" titleBlock={false} />
        </div>
      </section>

      <section className="lift tech-grid" style={section}>
        <div className="wrap">
          <div style={head}>
            <p className="t-eyebrow">G01 Front view only (phones, Specifications disclosure)</p>
          </div>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(min(100%, 320px), 1fr))",
              gap: "clamp(32px, 4vw, 96px)",
              alignItems: "end",
            }}
          >
            <TechnicalDrawing variant="front" />
            <TechnicalDrawing variant="front" annotate={false} />
            <dl style={{ display: "grid", gap: "20px", alignSelf: "center" }}>
              {specStrip.map((s) => (
                <div key={s.label} style={{ borderTop: "1px solid var(--hairline)", paddingTop: "14px" }}>
                  <dt className="t-stat" style={{ fontSize: "clamp(2.5rem, 3vw, 4.5rem)" }}>
                    {s.value}
                    {s.unit ? <span className="t-unit">{s.unit}</span> : null}
                  </dt>
                  <dd className="t-label">{s.label}</dd>
                </div>
              ))}
            </dl>
          </div>
        </div>
      </section>

      <section className="lift" style={{ ...section, position: "relative", overflow: "clip" }}>
        <GhostContour side="right" />
        <div className="wrap center" style={{ position: "relative" }}>
          <p className="t-eyebrow">G10c Ghost contour (visible at 1920px and wider)</p>
          <h2 className="t-h2" style={{ marginTop: 16 }}>
            {precision.headline}
          </h2>
          <p className="t-lead" style={{ marginTop: 24 }}>
            {precision.body}
          </p>
        </div>
      </section>
    </>
  );
}
