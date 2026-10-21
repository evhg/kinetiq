import { DrilledVsMoulded } from "@/components/graphics/DrilledVsMoulded";
import { holes } from "@/content/copy";

// Review page for G06: the pair as it sits in the Holes chapter, band 2, at the full content width.
export default function LabG06() {
  return (
    <section className="lift tech-grid" style={{ paddingBlock: "clamp(64px, 8vw, 200px)" }}>
      <div className="wrap">
        <h2 className="t-h2" style={{ textAlign: "center", marginBottom: "clamp(40px, 4vw, 112px)" }}>
          {holes.headline}
        </h2>
        <DrilledVsMoulded />
      </div>
    </section>
  );
}
