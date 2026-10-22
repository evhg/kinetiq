import type { CSSProperties } from "react";
import { ICON_NAMES, Icon, TierGlyph } from "@/components/graphics/Icons";
import { editionsIntro, tiers } from "@/content/lineup";
import { reserveCopy } from "@/content/reserve";

// Saira's hinted advances round badly on Linux and Windows Chromium; the components set the same.
const section: CSSProperties = { paddingBlock: "clamp(64px, 8vw, 200px)", textRendering: "geometricPrecision" };
const hair = "1px solid var(--hairline)";
// The legend cell spans what is left of the last icon row, so the icon grid ends level at 2, 3, 4 and
// 6 columns whatever the icon count; the 6 glyph cells divide evenly into 2, 3 and 6
const legendSpan = (cols: number) => cols - (ICON_NAMES.length % cols);
const grid = (cols: string): CSSProperties => ({
  display: "grid",
  gridTemplateColumns: cols,
  borderTop: hair,
  borderLeft: hair,
});
const cell: CSSProperties = {
  display: "grid",
  justifyItems: "center",
  alignContent: "center",
  gap: "clamp(14px, 0.8vw + 8px, 28px)",
  minHeight: "clamp(150px, 6vw + 110px, 260px)",
  padding: "clamp(20px, 1.2vw + 12px, 44px) 12px",
  borderRight: hair,
  borderBottom: hair,
  textAlign: "center",
};
const pair: CSSProperties = { display: "flex", alignItems: "center", gap: "clamp(18px, 1vw + 10px, 36px)" };
const logotype: CSSProperties = {
  fontFamily: "var(--font-display)",
  fontVariationSettings: '"wdth" 125',
  fontWeight: 500,
  textTransform: "uppercase",
  letterSpacing: "0.08em",
  fontSize: "var(--fs-h3)",
  lineHeight: 1.1,
};
const glyphSize: CSSProperties = { width: "clamp(36px, 1.2vw + 20px, 48px)", height: "clamp(36px, 1.2vw + 20px, 48px)" };
const trustIcons = ["refundArrow", "deliveryBox", "measurementCard"] as const;
const css = `
.g11-icons { grid-template-columns: repeat(2, minmax(0, 1fr)); }
.g11-glyphs { grid-template-columns: repeat(2, minmax(0, 1fr)); }
.g11-legend { grid-column: span ${legendSpan(2)}; }
@media (min-width: 700px) {
  .g11-icons, .g11-glyphs { grid-template-columns: repeat(3, minmax(0, 1fr)); }
  .g11-legend { grid-column: span ${legendSpan(3)}; }
}
@media (min-width: 1024px) {
  .g11-icons { grid-template-columns: repeat(4, minmax(0, 1fr)); }
  .g11-legend { grid-column: span ${legendSpan(4)}; }
}
@media (min-width: 1400px) {
  .g11-icons, .g11-glyphs { grid-template-columns: repeat(6, minmax(0, 1fr)); }
  .g11-legend { grid-column: span ${legendSpan(6)}; }
}
`;

export default function LabG11() {
  return (
    <section className="lift tech-grid" style={section}>
      <style>{css}</style>
      <div className="wrap" style={{ display: "grid", gap: "clamp(48px, 4vw, 120px)" }}>
        <div style={{ display: "grid", gap: 12 }}>
          <p className="t-eyebrow">G11 Icons and tier glyphs</p>
          <h2 className="t-h2">{editionsIntro.headline}</h2>
        </div>

        <div style={{ display: "grid", gap: 16 }}>
          <p className="t-label">Icons at 24 px in --steel and 48 px in --amber</p>
          <div className="g11-icons" style={grid("")}>
            {ICON_NAMES.map((n) => (
              <div key={n} style={cell}>
                <div style={pair}>
                  <Icon name={n} className="g11-steel" />
                  <span style={{ color: "var(--amber)", display: "inline-flex" }}>
                    <Icon name={n} size={48} />
                  </span>
                </div>
                <span className="t-label">{n}</span>
              </div>
            ))}
            <div
              className="g11-legend"
              style={{ ...cell, justifyItems: "start", textAlign: "left", alignContent: "center", color: "var(--steel)" }}
            >
              <span className="t-label" style={{ color: "var(--steel)" }}>
                24 px grid
                <br />
                1.25 px stroke
                <br />
                Round caps
              </span>
            </div>
          </div>
        </div>

        <div style={{ display: "grid", gap: 16 }}>
          <p className="t-label">Tier glyphs, unselected and selected</p>
          <div className="g11-glyphs" style={grid("")}>
            {tiers.flatMap((t) =>
              [false, true].map((sel) => (
                <div key={`${t.id}-${sel}`} style={cell}>
                  <TierGlyph tier={t.id} selected={sel} className="g11-glyph" />
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
            gridTemplateColumns: "repeat(auto-fit, minmax(min(100%, 420px), 1fr))",
            gap: "clamp(40px, 4vw, 120px)",
          }}
        >
          <div>
            <p className="t-label" style={{ marginBottom: 16 }}>
              In context: edition rows
            </p>
            <ul style={{ display: "grid" }}>
              {tiers.map((t, i) => (
                <li
                  key={t.id}
                  style={{
                    display: "grid",
                    gridTemplateColumns: "auto 1fr auto",
                    alignItems: "center",
                    gap: "clamp(16px, 1vw + 8px, 32px)",
                    padding: "clamp(18px, 0.8vw + 12px, 32px) 0",
                    borderTop: hair,
                  }}
                >
                  <span style={{ ...glyphSize, display: "inline-flex" }}>
                    <TierGlyph tier={t.id} selected={i === 1} className="g11-fill" />
                  </span>
                  <span style={{ ...logotype, color: t.id === "invite" ? "var(--muted)" : "var(--text)" }}>{t.name}</span>
                  <span className="t-label">{t.availability}</span>
                </li>
              ))}
            </ul>
          </div>
          <div>
            <p className="t-label" style={{ marginBottom: 16 }}>
              In context: reserve trust list
            </p>
            <ul style={{ display: "grid" }}>
              {reserveCopy.trustLines.map((line, i) => (
                <li
                  key={line}
                  className="t-body"
                  style={{
                    display: "grid",
                    gridTemplateColumns: "24px 1fr",
                    gap: 16,
                    alignItems: "center",
                    padding: "clamp(16px, 0.6vw + 12px, 28px) 0",
                    borderTop: hair,
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
      <style>{`.g11-steel { color: var(--steel); } .g11-glyph { width: 48px; height: 48px; } .g11-fill { width: 100%; height: 100%; }`}</style>
    </section>
  );
}
