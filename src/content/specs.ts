// The engineering numbers behind the claims (owner, 2026-11-02, after the factory meeting: "the aim is to convey we
// can back up our claims with numbers"). One typed record per value: what it is, its figure and unit, and the test
// method that measures it. Every claim here has a row in CLAIMS.md (rows 43, 46 and 47, and "Provisional numbers").
//
// This module ships to the browser (the spec sheet and Surface are client components), so it holds only what the page
// prints. Whether a value is still provisional, and where each figure comes from, live in `specs-status.ts`, which only
// server code imports: a launch build (NEXT_PUBLIC_LAUNCHED=true) fails while any value is still provisional. When the
// factory's value arrives, replace `value` here and mark it measured there, naming the report.
//
// Never a brand, a maker, a fibre grade, the factory, its town or its patents; never defence or military wording.

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
};

export type SpecGroup = { id: "mechanical" | "thermal" | "environmental" | "impact" | "surface"; title: string; specs: Spec[] };

/**
 * The carbon shell's specifications. Three are printed, one under each of Aerospace-grade carbon's points (copy.ts
 * `spaceGrade.points[].figure`: fibreStrength, voids, service; owner 2026-11-07: "the 9 numbers are too much, reduce it
 * to 3"); the rest are held here for the factory's reports.
 * The Command and Pace laminates both meet them.
 */
export const carbonSpecs: SpecGroup[] = [
  {
    id: "mechanical",
    title: "Mechanical",
    specs: [
      {
        id: "fibreStrength",
        label: "Fibre tensile strength",
        bound: "≥",
        value: "5,500",
        unit: "MPa",
        method: "ISO 10618",
      },
      {
        id: "fibreModulus",
        label: "Fibre tensile modulus",
        bound: "≥",
        value: "275",
        unit: "GPa",
        method: "ISO 10618",
      },
      {
        id: "flexStrength",
        label: "Laminate flexural strength",
        bound: "≥",
        value: "900",
        unit: "MPa",
        method: "ISO 14125",
      },
      {
        id: "flexModulus",
        label: "Laminate flexural modulus",
        value: "60",
        unit: "GPa",
        method: "ISO 14125",
      },
      {
        id: "ilss",
        label: "Interlaminar shear strength",
        bound: "≥",
        value: "70",
        unit: "MPa",
        method: "EN 2563",
      },
      {
        id: "voids",
        label: "Void content",
        note: "porosity, by volume",
        bound: "≤",
        value: "0.8",
        unit: "%",
        method: "ASTM D2734",
      },
      {
        id: "fibreVolume",
        label: "Fibre volume fraction",
        bound: "≥",
        value: "58",
        unit: "%",
        method: "ASTM D3171",
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
        value: "130",
        unit: "°C",
        method: "ASTM D7028",
      },
      {
        id: "service",
        label: "Service temperature",
        note: "stiffness held across the range",
        value: "−30 to +80",
        unit: "°C",
        method: "Thermal cycling, then ISO 14125",
      },
      {
        id: "cte",
        label: "Thermal expansion",
        note: "in the plane of the face",
        value: "2.0",
        unit: "ppm/K",
        method: "ASTM E831",
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
        value: "1.0",
        unit: "% by weight",
        method: "ASTM D5229",
      },
      {
        id: "uv",
        label: "Colour change under UV",
        note: "after 1,000 hours of xenon-arc light",
        bound: "≤",
        value: "4",
        unit: "ΔE",
        method: "ISO 4892-2",
      },
      {
        id: "salt",
        label: "Strength after salt and sweat",
        note: "flexural strength kept after 500 hours of salt fog",
        bound: "≥",
        value: "95",
        unit: "%",
        method: "ISO 9227",
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
      note: "at the grip, to 5% of the first peak",
      bound: "≤",
      value: "60",
      unit: "ms",
      method: "Accelerometer at the grip, robot impact at the sweet spot",
    },
    {
      id: "damping",
      label: "Damping ratio",
      note: "first bending mode",
      value: "2.0",
      unit: "%",
      method: "Modal analysis",
    },
  ],
};

/**
 * The face's moulded texture, quoted by High-Friction MicroWeave (the Surface section; CLAIMS.md rows 48, 49 and 53; owner, 2026-11-02: "unique surface
 * roughness"). The headline number is grip, the friction between face and ball, because that is what turns a brushed
 * contact into spin (a published padel study: a face's friction changes the spin only when the ball slides across it,
 * on a slice or a drop shot, not on a flat hit). Never a comparison with a named racket or brand on the page.
 */
export const surfaceSpecs: SpecGroup = {
  id: "surface",
  title: "High-Friction MicroWeave",
  specs: [
    {
      id: "friction",
      label: "Friction against the ball",
      note: "static friction against a padel ball",
      value: "0.65",
      unit: "",
      method: "Tilt test with a padel ball on the face",
    },
    {
      id: "roughness",
      label: "Surface roughness",
      note: "average, Ra, moulded\u00a0into the face",
      value: "16",
      unit: "µm",
      method: "ISO 21920, stylus profilometer",
    },
    {
      id: "roughnessRz",
      label: "Texture depth",
      note: "Rz, peak to valley, within a flat face",
      value: "80",
      unit: "µm",
      method: "ISO 21920",
    },
  ],
};

export const ALL_SPECS: Spec[] = [...carbonSpecs.flatMap((g) => g.specs), ...impactSpecs.specs, ...surfaceSpecs.specs];

/** One value by id. Throws on an unknown id, so a typo fails the build rather than printing nothing. */
export function spec(id: string): Spec {
  const s = ALL_SPECS.find((x) => x.id === id);
  if (!s) throw new Error(`specs.ts: no spec "${id}"`);
  return s;
}

/** A value as a sentence quotes it, with no-break spaces: "0.8%", "60 ms", "5,500 MPa". */
export function specValue(id: string): string {
  const s = spec(id);
  if (!s.unit) return s.value;
  return s.unit === "%" || s.unit === "°C" ? `${s.value}${s.unit}` : `${s.value} ${s.unit}`;
}
