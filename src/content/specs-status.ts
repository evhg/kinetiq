// Server only: whether each number in specs.ts is still provisional, and where its figure comes from. Never import
// this from a client component: the sources are internal notes (CLAIMS.md "Provisional numbers" mirrors them), and
// the browser bundle must carry only what the page prints (review, 2026-11-02). The root layout imports it, so the
// launch gate below runs in every server render and in the build's prerender.
//
// Never a brand, a maker, a fibre grade, the factory, its town or its patents; never defence or military wording.

import { ALL_SPECS } from "./specs";

const RESEARCH = "Provisional (research 2026-11-02): ";

export type SpecStatus = {
  /** True until the factory supplies a tested value: a launch build fails while any value is provisional. */
  provisional: boolean;
  /** Where the figure comes from: for a provisional value, the reference it was set from; then the test report. */
  source: string;
};

export const SPEC_STATUS: Record<string, SpecStatus> = {
  fibreStrength: { provisional: true, source: `${RESEARCH}the lower end of the intermediate-modulus fibre class (about 5,500 to 5,900 MPa on datasheets), the class the space-grade claim needs (row 42: stronger for its weight than the standard-modulus class most padel rackets use, about 3,500 to 4,900 MPa). The factory confirms the load-bearing plies are of this class, per feel.` },
  fibreModulus: { provisional: true, source: `${RESEARCH}the lower end of the intermediate-modulus fibre class (about 275 to 295 GPa; standard-modulus class about 230 GPa). The factory confirms the class, per feel.` },
  flexStrength: { provisional: true, source: `${RESEARCH}woven carbon/epoxy 600 to 900 MPa; a 3K 2x2 twill prepreg datasheet gives 882 MPa.` },
  flexModulus: { provisional: true, source: `${RESEARCH}3K 2x2 twill prepreg datasheet 60.1 GPa; typical woven laminates 50 to 60 GPa.` },
  ilss: { provisional: true, source: `${RESEARCH}3K twill prepreg datasheet 69.8 MPa; typical 50 to 70 MPa, falling about 8.5% per 1% of voids.` },
  voids: { provisional: true, source: `${RESEARCH}autoclave-cured aerospace laminates are held under 1%; vacuum-bag prepreg about 1.3%. The factory says it controls porosity exceptionally well: its measured figure replaces this one.` },
  fibreVolume: { provisional: true, source: `${RESEARCH}aerospace datasheets normalise to 60%; hand-laid laminates typically 45 to 55%.` },
  tg: { provisional: true, source: `${RESEARCH}a 120 to 135 °C-cure racket prepreg gives a dry Tg of about 130 to 150 °C. A 180 °C aerospace cure is ruled out: the shell is co-moulded around a sealed EVA core, which would degrade at that temperature.` },
  service: { provisional: true, source: `${RESEARCH}our design range (a winter court to a car boot in summer), well inside the resin's Tg; 50 cycles −30/+80 °C, then a flexural test.` },
  cte: { provisional: true, source: `${RESEARCH}woven carbon/epoxy 1 to 4 ppm/K; a generic carbon/epoxy sheet 2.1 ppm/K.` },
  moisture: { provisional: true, source: `${RESEARCH}a published aerospace laminate saturates at 0.8 to 0.9% at 80 °C / 90% RH, so 1.0% at 85 °C / 85% RH is a realistic ceiling; the core is sealed inside the shell.` },
  uv: { provisional: true, source: `${RESEARCH}estimate, rarely published for rackets; assumes a UV-stable clear coat over the face (a white epoxy face without one yellows well past 4 ΔE). The factory must confirm the coat.` },
  salt: { provisional: true, source: `${RESEARCH}estimate; with artificial sweat to ISO 3160-2.` },
  decay: { provisional: true, source: `${RESEARCH}not published for padel; tennis frames ring for about 80 to 150 ms free. The factory will measure impact absorption.` },
  damping: { provisional: true, source: `${RESEARCH}carbon rackets about 0.5 to 2% free.` },
  friction: { provisional: true, source: `${RESEARCH}a published padel spin study measured three rackets' faces at 0.18, 0.33 and 0.50 (a court surface 0.65) with the same tilt test; ours to be measured by the factory the same way.` },
  roughness: { provisional: true, source: `${RESEARCH}estimate; gloss clear-coat faces about 0.1 to 0.4 µm, matte 0.5 to 2 µm, sand-textured padel faces about 5 to 12 µm (no published padel data). Set at 16 rather than the research's 15 µm so it never reads as the 15 µm precision figure (row 2).` },
  roughnessRz: { provisional: true, source: `${RESEARCH}estimate; textured faces about 30 to 60 µm. FIP Rule 7: both faces must be flat but may be smooth or rough (no numeric limit published).` },
};

// Every printed value has a status, and every status a value: a new spec without one fails the build.
for (const s of ALL_SPECS) if (!SPEC_STATUS[s.id]) throw new Error(`specs-status.ts: no status for spec "${s.id}"`);
for (const id of Object.keys(SPEC_STATUS))
  if (!ALL_SPECS.some((s) => s.id === id)) throw new Error(`specs-status.ts: status for unknown spec "${id}"`);

/** Every value still waiting for the factory (CLAIMS.md "Provisional numbers" lists the same). */
export const provisionalSpecs = () => ALL_SPECS.filter((s) => SPEC_STATUS[s.id].provisional);

/**
 * The launch gate for numbers: a launch build (NEXT_PUBLIC_LAUNCHED=true) fails while any value shown on the site is
 * still provisional.
 */
export function assertLaunchable(launched = process.env.NEXT_PUBLIC_LAUNCHED === "true") {
  const open = provisionalSpecs();
  if (launched && open.length) {
    throw new Error(
      `NEXT_PUBLIC_LAUNCHED=true but ${open.length} spec values are still provisional (src/content/specs-status.ts; CLAIMS.md "Provisional numbers"): ${open.map((s) => s.id).join(", ")}`,
    );
  }
}

assertLaunchable();
