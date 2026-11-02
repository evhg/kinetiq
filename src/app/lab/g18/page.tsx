import { GripContact } from "@/components/graphics/GripContact";
import { surface } from "@/content/copy";

const section = { paddingBlock: "clamp(64px, 8vw, 200px)" } as const;
const head = { marginBottom: "clamp(32px, 3vw, 72px)", display: "grid", gap: "12px" } as const;

// Review page for G18 "How the face grips": the contact magnified from the side, at the Surface column's width and at
// 350 px (a phone's column). The landing section composes it beside the words (Surface.tsx); /lab/g17 shows it there.
export default function LabG18() {
  return (
    <section className="lift tech-grid" style={section}>
      <div className="wrap">
        <div style={head}>
          <p className="t-eyebrow">G18 How the face grips</p>
          <h2 className="t-h2">{surface.headline}</h2>
        </div>
        <div style={{ display: "grid", gap: "clamp(48px, 6vw, 120px)", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", alignItems: "start" }}>
          <GripContact legend={surface.contact} />
          <div style={{ width: "350px", maxWidth: "100%" }}>
            <GripContact legend={surface.contact} />
          </div>
        </div>
      </div>
    </section>
  );
}
