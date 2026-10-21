import { ICON_NAMES, Icon, TierGlyph } from "@/components/graphics/Icons";
import { tiers } from "@/content/lineup";
import { reserveCopy } from "@/content/reserve";

const section = { paddingBlock: "clamp(64px, 8vw, 200px)" } as const;
const cell = {
  display: "grid",
  justifyItems: "center",
  alignContent: "center",
  gap: "14px",
  minHeight: "clamp(120px, 6vw + 60px, 200px)",
  padding: "20px 12px",
  borderTop: "1px solid var(--hairline)",
  borderLeft: "1px solid var(--hairline)",
} as const;
const grid = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fill, minmax(min(100%, 150px), 1fr))",
  borderRight: "1px solid var(--hairline)",
  borderBottom: "1px solid var(--hairline)",
} as const;
const trustIcons = ["refundArrow", "deliveryBox", "measurementCard"] as const;

export default function LabG11() {
  return (
    <>
      <section className="lift tech-grid" style={section}>
        <div className="wrap" style={{ display: "grid", gap: "clamp(40px, 4vw, 96px)" }}>
          <div style={{ display: "grid", gap: 12 }}>
            <p className="t-eyebrow">G11 Icons and tier glyphs</p>
            <h2 className="t-h2">Three editions. One standard.</h2>
          </div>

          <div style={{ display: "grid", gap: 16 }}>
            <p className="t-label">24 px, --steel</p>
            <div style={grid}>
              {ICON_NAMES.map((n) => (
                <div key={n} style={{ ...cell, color: "var(--steel)" }}>
                  <Icon name={n} />
                  <span className="t-label">{n}</span>
                </div>
              ))}
            </div>
          </div>

          <div style={{ display: "grid", gap: 16 }}>
            <p className="t-label">48 px, --amber</p>
            <div style={grid}>
              {ICON_NAMES.map((n) => (
                <div key={n} style={{ ...cell, color: "var(--amber)" }}>
                  <Icon name={n} size={48} />
                  <span className="t-label">{n}</span>
                </div>
              ))}
            </div>
          </div>

          <div style={{ display: "grid", gap: 16 }}>
            <p className="t-label">Tier glyphs, unselected and selected</p>
            <div style={grid}>
              {tiers.flatMap((t) =>
                [false, true].map((sel) => (
                  <div key={`${t.id}-${sel}`} style={cell}>
                    <TierGlyph tier={t.id} selected={sel} />
                    <span className="t-label">
                      {t.availability}
                      {sel ? ", selected" : ""}
                    </span>
                  </div>
                )),
              )}
            </div>
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(min(100%, 340px), 1fr))",
              gap: "clamp(32px, 3vw, 80px)",
            }}
          >
            <div style={{ display: "grid", gap: 0 }}>
              <p className="t-label" style={{ marginBottom: 16 }}>
                In context: edition rows
              </p>
              {tiers.map((t, i) => (
                <div
                  key={t.id}
                  style={{
                    display: "grid",
                    gridTemplateColumns: "auto 1fr auto",
                    alignItems: "center",
                    gap: 16,
                    padding: "20px 0",
                    borderTop: "1px solid var(--hairline)",
                  }}
                >
                  <TierGlyph tier={t.id} selected={i === 1} />
                  <span className="t-h3" style={{ color: i === 1 ? "var(--text)" : t.id === "invite" ? "var(--muted)" : "var(--text)" }}>
                    {t.name}
                  </span>
                  <span className="t-label">{t.availability}</span>
                </div>
              ))}
            </div>
            <div>
              <p className="t-label" style={{ marginBottom: 16 }}>
                In context: reserve trust list
              </p>
              <ul style={{ display: "grid", gap: 0 }}>
                {reserveCopy.trustLines.map((line, i) => (
                  <li
                    key={line}
                    className="t-body"
                    style={{
                      display: "grid",
                      gridTemplateColumns: "auto 1fr",
                      gap: 16,
                      alignItems: "center",
                      padding: "18px 0",
                      borderTop: "1px solid var(--hairline)",
                      color: "var(--steel)",
                    }}
                  >
                    <Icon name={trustIcons[i]} />
                    {line}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
