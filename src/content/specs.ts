// The engineering numbers behind the claims (owner, 2026-11-02, after the factory meeting: "the aim is to convey we
// can back up our claims with numbers"). One typed record per value: what it is, its figure and unit, whether it is
// still provisional, the test method that measures it, and where the figure comes from. Every claim here has a row in
// CLAIMS.md (rows 43, 46 and 47, and the provisional list under "Provisional numbers").
//
// PROVISIONAL: until the factory supplies tested values, every figure is a realistic placeholder taken from the
// 2026-11-02 research (conservative ends of published datasheets for the fibre and resin classes we name; see
// `source`). Each is flagged `provisional: true`. They render normally on the gated preview. A launch build
// (NEXT_PUBLIC_LAUNCHED=true) refuses to build while any value is still provisional: see `assertLaunchable` below.
// When the factory's value arrives, replace `value`, set `provisional: false`, and name the report in `source`.
//
// Never a brand, a maker, the factory, its town or its patents; never defence or military wording (CLAUDE.md).

export type Spec = {
  /** Stable id, used by the copy that quotes a value inline (`specValue`). */
  id: string;
  /** The term, as the spec sheet prints it. */
  label: string;
  /** "≤" (at most), "≥" (at least) or nothing (nominal). Printed before the figure. */
  bound?: "≤" | "≥";
  /** The figure, formatted as printed (thin grouping commas, a decimal where the house rules want one). */
  value: string;
  /** The unit, printed after the figure ("" for none). */
  unit: string;
  /** A short condition or qualifier printed under the label ("at 85 °C and 85% humidity"). */
  note?: string;
  /** The test method the value is measured by. Printed on the sheet. */
  method: string;
  /** True until the factory supplies a tested value: a launch build fails while any value is provisional. */
  provisional: boolean;
  /** Where the figure comes from: for a provisional value, the reference it was set from; then the test report. */
  source: string;
};

export type SpecGroup = { id: "mechanical" | "thermal" | "environmental" | "impact"; title: string; specs: Spec[] };

const RESEARCH = "Provisional (research 2026-11-02): ";

/** The carbon shell's specifications, shown under Space-grade carbon. The Command and Pace laminates both meet them. */
export const carbonSpecs: SpecGroup[] = [
  {
    id: "mechanical",
    title: "Mechanical",
    specs: [
      {
        id: "fibreStrength",
        label: "Fibre tensile strength",
        bound: "≥",
        value: "4,900",
        unit: "MPa",
        method: "ISO 10618",
        provisional: true,
        source: `${RESEARCH}the T700 class's datasheet value, the lower of the two fibre classes (T800 class: 5,880 MPa); standard-modulus T300 class about 3,530 MPa.`,
      },
      {
        id: "fibreModulus",
        label: "Fibre tensile modulus",
        bound: "≥",
        value: "230",
        unit: "GPa",
        method: "ISO 10618",
        provisional: true,
        source: `${RESEARCH}T700 class datasheet (T800 class: 294 GPa).`,
      },
      {
        id: "flexStrength",
        label: "Laminate flexural strength",
        bound: "≥",
        value: "900",
        unit: "MPa",
        method: "ISO 14125",
        provisional: true,
        source: `${RESEARCH}woven carbon/epoxy 600 to 900 MPa; a 3K 2x2 twill prepreg datasheet gives 882 MPa.`,
      },
      {
        id: "flexModulus",
        label: "Laminate flexural modulus",
        value: "60",
        unit: "GPa",
        method: "ISO 14125",
        provisional: true,
        source: `${RESEARCH}3K 2x2 twill prepreg datasheet 60.1 GPa; typical woven laminates 50 to 60 GPa.`,
      },
      {
        id: "ilss",
        label: "Interlaminar shear strength",
        bound: "≥",
        value: "70",
        unit: "MPa",
        method: "EN 2563",
        provisional: true,
        source: `${RESEARCH}3K twill prepreg datasheet 69.8 MPa; typical 50 to 70 MPa, falling about 8.5% per 1% of voids.`,
      },
      {
        id: "voids",
        label: "Void content",
        note: "porosity, by volume",
        bound: "≤",
        value: "0.8",
        unit: "%",
        method: "ASTM D2734",
        provisional: true,
        source: `${RESEARCH}autoclave-cured aerospace laminates are held under 1%; vacuum-bag prepreg about 1.3%. The factory says it controls porosity exceptionally well: its measured figure replaces this one.`,
      },
      {
        id: "fibreVolume",
        label: "Fibre volume fraction",
        bound: "≥",
        value: "58",
        unit: "%",
        method: "ASTM D3171",
        provisional: true,
        source: `${RESEARCH}aerospace datasheets normalise to 60%; hand-laid laminates typically 45 to 55%.`,
      },
    ],
  },
  {
    id: "thermal",
    title: "Thermal",
    specs: [
      {
        id: "tg",
        label: "Glass transition temperature",
        note: "resin, dry",
        bound: "≥",
        value: "180",
        unit: "°C",
        method: "ASTM D7028",
        provisional: true,
        source: `${RESEARCH}180 °C-cure aerospace epoxy (a published system: 200 °C dry, 154 °C wet); 120 °C-cure sports prepreg 140 to 148 °C.`,
      },
      {
        id: "service",
        label: "Service temperature",
        note: "stiffness held across the range",
        value: "−30 to +80",
        unit: "°C",
        method: "Thermal cycling, then ISO 14125",
        provisional: true,
        source: `${RESEARCH}our design range (a winter court to a car boot in summer), well inside the resin's Tg; 50 cycles −30/+80 °C, then a flexural test.`,
      },
      {
        id: "cte",
        label: "Thermal expansion",
        note: "in the plane of the face",
        value: "2.0",
        unit: "ppm/K",
        method: "ASTM E831",
        provisional: true,
        source: `${RESEARCH}woven carbon/epoxy 1 to 4 ppm/K; a generic carbon/epoxy sheet 2.1 ppm/K.`,
      },
    ],
  },
  {
    id: "environmental",
    title: "Environmental",
    specs: [
      {
        id: "moisture",
        label: "Moisture absorption",
        note: "at saturation, 85 °C and 85% humidity",
        bound: "≤",
        value: "0.5",
        unit: "% by weight",
        method: "ASTM D5229",
        provisional: true,
        source: `${RESEARCH}a published aerospace laminate saturates at 0.8 to 0.9% at 80 °C / 90% RH; the core is sealed inside the shell.`,
      },
      {
        id: "uv",
        label: "Colour change under UV",
        note: "after 1,000 hours of xenon-arc light",
        bound: "≤",
        value: "2",
        unit: "ΔE",
        method: "ISO 4892-2",
        provisional: true,
        source: `${RESEARCH}estimate; rarely published for rackets.`,
      },
      {
        id: "salt",
        label: "Strength after salt and sweat",
        note: "flexural strength kept after 500 hours of salt fog",
        bound: "≥",
        value: "95",
        unit: "%",
        method: "ISO 9227",
        provisional: true,
        source: `${RESEARCH}estimate; with artificial sweat to ISO 3160-2.`,
      },
    ],
  },
];

/** Impact absorption, quoted by Feel (CLAIMS.md row 14): what reaches the hand after a shot. */
export const impactSpecs: SpecGroup = {
  id: "impact",
  title: "Impact",
  specs: [
    {
      id: "decay",
      label: "Vibration decay",
      note: "at the grip, to 10% of the first peak",
      bound: "≤",
      value: "60",
      unit: "ms",
      method: "Accelerometer at the grip, robot impact at the sweet spot",
      provisional: true,
      source: `${RESEARCH}not published for padel; tennis frames ring for about 80 to 150 ms free. The factory will measure impact absorption.`,
    },
    {
      id: "damping",
      label: "Damping ratio",
      note: "first bending mode",
      value: "2.0",
      unit: "%",
      method: "Modal analysis",
      provisional: true,
      source: `${RESEARCH}carbon rackets about 0.5 to 2% free.`,
    },
  ],
};

const ALL: Spec[] = [...carbonSpecs.flatMap((g) => g.specs), ...impactSpecs.specs];

/** One value by id. Throws on an unknown id, so a typo fails the build rather than printing nothing. */
export function spec(id: string): Spec {
  const s = ALL.find((x) => x.id === id);
  if (!s) throw new Error(`specs.ts: no spec "${id}"`);
  return s;
}

/** A value as a sentence quotes it, with no-break spaces: "0.8%", "60 ms", "4,900 MPa". */
export function specValue(id: string): string {
  const s = spec(id);
  if (!s.unit) return s.value;
  return s.unit === "%" || s.unit === "°C" ? `${s.value}${s.unit}` : `${s.value} ${s.unit}`;
}

/** Every value still waiting for the factory (CLAIMS.md "Provisional numbers" lists the same). */
export const provisionalSpecs = (): Spec[] => ALL.filter((s) => s.provisional);

/**
 * The launch gate for numbers: a launch build (NEXT_PUBLIC_LAUNCHED=true) fails while any value shown on the site is
 * still provisional. It runs on the server only (the build's prerender imports this module through copy.ts), so a
 * visitor's browser never throws.
 */
export function assertLaunchable(launched = process.env.NEXT_PUBLIC_LAUNCHED === "true") {
  const open = provisionalSpecs();
  if (launched && open.length) {
    throw new Error(
      `NEXT_PUBLIC_LAUNCHED=true but ${open.length} spec values are still provisional (src/content/specs.ts; CLAIMS.md "Provisional numbers"): ${open.map((s) => s.id).join(", ")}`,
    );
  }
}

if (typeof window === "undefined") assertLaunchable();
