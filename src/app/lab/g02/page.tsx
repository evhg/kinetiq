import { VibrationGraph } from "@/components/graphics/VibrationGraph";
import { feel } from "@/content/copy";

// Review page for G02: the graph as it sits in the Feel chapter, at the full content width.
export default function LabG02() {
  return (
    <section className="lift tech-grid" style={{ paddingBlock: "clamp(64px, 8vw, 200px)" }}>
      <div className="wrap">
        <h2 className="t-h2" style={{ textAlign: "center", marginBottom: "clamp(40px, 4vw, 112px)" }}>
          {feel.headline}
        </h2>
        <VibrationGraph />
      </div>
    </section>
  );
}
