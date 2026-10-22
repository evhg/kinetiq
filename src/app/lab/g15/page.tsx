import { SweetSpotField } from "@/components/graphics/SweetSpotField";
import { SweetSpot } from "@/components/landing/SweetSpot";
import { sweetSpot } from "@/content/copy";
import { SWEET, SWEET_CLAIM } from "@/lib/graphics-sweetspot";

const section = { paddingBlock: "clamp(64px, 8vw, 200px)" } as const;
const head = { marginBottom: "clamp(32px, 3vw, 72px)", display: "grid", gap: "12px" } as const;
const cell = { borderTop: "1px solid var(--hairline)", paddingTop: "14px", display: "grid", gap: "6px" } as const;

/** The claim's numbers as computed from racket-shape.ts, beside the words the page prints (built from SWEET_CLAIM). */
const CHECK: [string, string, string][] = [
  ["Face above the bridge", `${SWEET.face.toFixed(2)} cm²`, `${SWEET_CLAIM.face} cm² (fine print)`],
  ["Sweet spot, 4 mm in", `${SWEET.field.toFixed(2)} cm²`, `${SWEET_CLAIM.field} cm² (fine print)`],
  [
    "Share of the face",
    `${(SWEET.share * 100).toFixed(2)}%`,
    `${SWEET_CLAIM.nearly ? `${sweetSpot.share.nearly} ` : ""}${SWEET_CLAIM.share}${sweetSpot.share.unit} (lockup), ${SWEET_CLAIM.exact}% (fine print)`,
  ],
  ["Inset from the edge", `${SWEET.inset.toFixed(1)} mm`, `${SWEET_CLAIM.inset} ${sweetSpot.inset.unit} (lockup)`],
  ["Bridge line", `y ${SWEET.bridge.toFixed(1)} mm`, "the top of the throat"],
];

// Review page for G15 "Sweet spot": both framings (the reveal plays on entry), the numbers against the copy,
// then the landing section as composed (with K12 in place of G15 once the still is exported).
export default function LabG15() {
  // The lockup never rounds up without "Nearly" (as Apple rounds a display), and never says less than the geometry.
  const pct = SWEET.share * 100;
  const shown = Number(SWEET_CLAIM.share);
  const shareOk = shown <= Math.ceil(pct) && shown >= Math.floor(pct) && (shown <= pct || SWEET_CLAIM.nearly);
  return (
    <>
      <section className="lift tech-grid" style={section}>
        <div className="wrap">
          <div style={head}>
            <p className="t-eyebrow">G15 Sweet spot, wide framing (1000 px and wider, and 700 to 999 px)</p>
            <h2 className="t-h2">{sweetSpot.headline}</h2>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(min(100%, 420px), 1fr))", gap: "clamp(32px, 4vw, 96px)", alignItems: "center" }}>
            <SweetSpotField variant="wide" reveal />
            <dl style={{ display: "grid", gap: "20px", alignSelf: "center" }}>
              {CHECK.map(([k, v, copy]) => (
                <div key={k} style={cell}>
                  <dt className="t-label">{k}</dt>
                  <dd className="t-num" style={{ fontSize: "clamp(1.25rem, 1vw + 0.9rem, 2rem)", color: "var(--text)" }}>
                    {v}
                  </dd>
                  <dd className="t-fine">Copy: {copy}</dd>
                </div>
              ))}
              <div style={cell}>
                <dt className="t-label">Lockup matches the geometry</dt>
                <dd className="t-num" style={{ color: shareOk ? "var(--amber-hot)" : "var(--alert)" }}>
                  {shareOk ? "Yes" : "No: check SWEET_CLAIM in graphics-sweetspot.ts and CLAIMS.md row 6b"}
                </dd>
              </div>
            </dl>
          </div>
        </div>
      </section>

      <section className="lift tech-grid" style={section}>
        <div className="wrap">
          <div style={head}>
            <p className="t-eyebrow">G15 Portrait framing (phones, below 700 px), at 350 px and at 560 px</p>
          </div>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "clamp(32px, 4vw, 96px)", alignItems: "end" }}>
            <div style={{ width: "350px", maxWidth: "100%" }}>
              <SweetSpotField variant="portrait" reveal />
            </div>
            <div style={{ width: "min(100%, 560px)" }}>
              <SweetSpotField variant="portrait" reveal />
            </div>
          </div>
        </div>
      </section>

      <SweetSpot />
    </>
  );
}
