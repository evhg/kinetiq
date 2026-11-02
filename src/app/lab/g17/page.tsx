import { SliceBounce } from "@/components/graphics/SliceBounce";
import { Surface } from "@/components/landing/Surface";
import { surface } from "@/content/copy";
import { KINETIQ, STANDARD } from "@/lib/graphics-slice";
import { surfaceSpecs } from "@/content/specs";

const section = { paddingBlock: "clamp(64px, 8vw, 200px)" } as const;
const head = { marginBottom: "clamp(32px, 3vw, 72px)", display: "grid", gap: "12px" } as const;
const cell = { borderTop: "1px solid var(--hairline)", paddingTop: "14px", display: "grid", gap: "6px" } as const;

// Review page for G17 "After the bounce": both framings (each plays once on entry), the modelled exits and the
// provisional surface numbers, then the landing section as composed.
export default function LabG17() {
  return (
    <>
      <section className="lift tech-grid" style={section}>
        <div className="wrap">
          <div style={head}>
            <p className="t-eyebrow">G17 After the bounce, wide framing (700 px and wider)</p>
            <h2 className="t-h2">{surface.graphic.title}</h2>
          </div>
          <SliceBounce variant="wide" scrub={false} />
        </div>
      </section>
      <section className="lift tech-grid" style={section}>
        <div className="wrap">
          <div style={head}>
            <p className="t-eyebrow">G17 portrait framing (phones, below 700 px), at 350 px</p>
          </div>
          <div style={{ width: "350px", maxWidth: "100%" }}>
            <SliceBounce variant="portrait" scrub={false} />
          </div>
          <dl style={{ display: "grid", gap: "20px", marginTop: "clamp(40px, 4vw, 96px)", maxWidth: "720px" }}>
            {[
              ["Standard exit (modelled)", `${STANDARD.turn}° off its line, rising to ${STANDARD.apex.toFixed(2)} m`],
              ["KINETIQ exit (modelled)", `${KINETIQ.turn}° off its line, rising to ${KINETIQ.apex.toFixed(2)} m`],
              ...surfaceSpecs.specs.map((s) => [`${s.label} (${s.provisional ? "provisional" : "measured"})`, `${s.value}${s.unit ? ` ${s.unit}` : ""}, ${s.method}`]),
            ].map(([k, v]) => (
              <div key={k} style={cell}>
                <dt className="t-label">{k}</dt>
                <dd className="t-num" style={{ color: "var(--text)" }}>
                  {v}
                </dd>
              </div>
            ))}
          </dl>
        </div>
      </section>
      <Surface />
    </>
  );
}
