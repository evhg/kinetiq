import { Badges } from "@/components/graphics/Badges";
import { bornWhole } from "@/content/copy";
import { reserveCopy } from "@/content/reserve";

const section = { paddingBlock: "clamp(64px, 8vw, 200px)" } as const;

export default function LabG13() {
  return (
    <>
      <section className="lift tech-grid" style={section}>
        <div className="wrap center" style={{ display: "grid", gap: "clamp(20px, 1.6vw, 40px)", justifyItems: "center" }}>
          <p className="t-eyebrow">{bornWhole.eyebrow}</p>
          <h2 className="t-h2">{bornWhole.headline}</h2>
          <p className="t-lead">{bornWhole.body}</p>
          <Badges align="center" />
        </div>
      </section>

      <section className="lift" style={section}>
        <div className="wrap" style={{ display: "grid", justifyItems: "center" }}>
          <div style={{ width: "min(100%, 560px)", display: "grid", gap: 20 }}>
            <p className="t-eyebrow">G13 in the reserve trust list (stack)</p>
            <ul style={{ display: "grid" }}>
              {reserveCopy.trustLines.map((t) => (
                <li key={t} className="t-body" style={{ padding: "14px 0", borderTop: "1px solid var(--hairline)", color: "var(--steel)" }}>
                  {t}
                </li>
              ))}
            </ul>
            <Badges layout="stack" />
          </div>
        </div>
      </section>
    </>
  );
}
