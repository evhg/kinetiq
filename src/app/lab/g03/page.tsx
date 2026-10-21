import { ToleranceGraph } from "@/components/graphics/ToleranceGraph";
import { precision } from "@/content/copy";

// Review page for G03: the graph as it sits in Precision part B, at the full content width.
export default function LabG03() {
  return (
    <section className="lift tech-grid" style={{ paddingBlock: "clamp(64px, 8vw, 200px)" }}>
      <div className="wrap">
        <h2 className="t-h2" style={{ textAlign: "center", marginBottom: "clamp(40px, 4vw, 112px)" }}>
          {precision.headline}
        </h2>
        <ToleranceGraph />
      </div>
    </section>
  );
}
