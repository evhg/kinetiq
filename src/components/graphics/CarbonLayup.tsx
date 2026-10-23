import { spaceGrade } from "@/content/copy";
import styles from "./CarbonLayup.module.css";

/**
 * G16: the shell cut through and magnified, the standard carbon most padel rackets use beside KINETIQ's space-grade
 * carbon, as a micrograph shows a laminate: four plies, 0° plies seen end-on (each fibre a disc) between 90° plies
 * seen along their length (streaks). Drawn honestly from typical values, never from a measurement of either: the same
 * fibre diameter on both sides; about 50% fibre by volume, set unevenly with resin-rich bands and a few air pockets
 * (voids) for standard carbon; about 60%, packed close and even with no voids, for aerospace-grade prepreg (CLAIMS.md
 * row 44 asks for our own micrograph before launch). The words are HTML (15 px and up at every width); the drawing is
 * deterministic (a seeded generator), so the server and the client draw the same fibres.
 */

const W = 600;
const H = 400;
const R = 6.2; // fibre radius, in drawing units, the same on both sides
const PLY = 92; // ply pitch: four plies plus their resin bands fill the height

type Disc = { x: number; y: number };
type Streak = { x: number; y: number; w: number };
type Void = { x: number; y: number; rx: number; ry: number };
type Panel = { discs: Disc[]; streaks: Streak[]; voids: Void[] };

/** mulberry32: a small seeded generator, so every render draws the same fibres. */
function rng(seed: number) {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function panel(kind: "standard" | "kinetiq"): Panel {
  const rand = rng(kind === "standard" ? 1907 : 427);
  const even = kind === "kinetiq";
  // Hexagonal pitch for a fibre volume fraction vf: area per fibre = pi r^2 / vf = (sqrt(3) / 2) s^2.
  const vf = even ? 0.6 : 0.5;
  const s = Math.sqrt((Math.PI * R * R) / (vf * (Math.sqrt(3) / 2)));
  const jitter = even ? 0.5 : 2.6;
  const band = even ? 6 : 14; // resin between plies: thin and even, or a resin-rich band
  const discs: Disc[] = [];
  const streaks: Streak[] = [];
  const voids: Void[] = [];
  for (let p = 0; p < 4; p++) {
    const top = 8 + p * (PLY + 6) + band / 2 + (even ? 0 : (rand() - 0.5) * 6);
    const bottom = top + PLY - band;
    if (p % 2 === 0) {
      // 0° ply: fibres end-on, hexagonal rows
      const dy = (s * Math.sqrt(3)) / 2;
      for (let row = 0, y = top + R; y <= bottom - R; row++, y += dy) {
        for (let x = R + (row % 2 ? s / 2 : 0); x <= W - R; x += s) {
          // standard carbon: gaps where the tows did not spread (resin-rich pockets)
          if (!even && rand() < 0.07) continue;
          discs.push({ x: x + (rand() - 0.5) * jitter, y: y + (rand() - 0.5) * jitter });
        }
      }
    } else {
      // 90° ply: fibres along their length, as streaks broken where the cut meets them
      for (let y = top + R; y <= bottom - R; y += s * 0.8) {
        let x = -20 * rand();
        while (x < W) {
          const w = (even ? 120 : 70) + rand() * (even ? 160 : 120);
          streaks.push({ x, y: y + (rand() - 0.5) * jitter, w });
          x += w + (even ? 6 : 12) + rand() * (even ? 4 : 18);
        }
      }
    }
    // standard carbon: air trapped between the plies and in the resin-rich bands
    if (!even && p < 3) {
      const n = p === 1 ? 2 : 1;
      for (let i = 0; i < n; i++) {
        voids.push({ x: 60 + rand() * (W - 120), y: bottom + band / 2 + 3, rx: 9 + rand() * 12, ry: 5 + rand() * 4 });
      }
    }
  }
  // A void displaces the fibres it sits on.
  const clear = (d: { x: number; y: number }) =>
    voids.every((v) => ((d.x - v.x) / (v.rx + R)) ** 2 + ((d.y - v.y) / (v.ry + R)) ** 2 > 1);
  return { discs: discs.filter(clear), streaks: streaks.filter((t) => clear({ x: t.x + t.w / 2, y: t.y })), voids };
}

const PANELS = { standard: panel("standard"), kinetiq: panel("kinetiq") };

function Drawing({ kind }: { kind: "standard" | "kinetiq" }) {
  const p = PANELS[kind];
  const id = `g16-${kind}`;
  return (
    <svg viewBox={`0 0 ${W} ${H}`} className={styles.svg} aria-hidden="true" focusable="false">
      <defs>
        {/* each fibre lit from the upper left, as under a microscope's ring light */}
        <radialGradient id={`${id}-disc`} cx="0.38" cy="0.34" r="0.7">
          <stop offset="0" stopColor="#f1f1ee" />
          <stop offset="0.55" stopColor="#b9bcc3" />
          <stop offset="1" stopColor="#6f727a" />
        </radialGradient>
        <linearGradient id={`${id}-streak`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#d9dbe0" />
          <stop offset="0.5" stopColor="#a4a7ae" />
          <stop offset="1" stopColor="#5f626a" />
        </linearGradient>
        <radialGradient id={`${id}-void`} cx="0.5" cy="0.45" r="0.6">
          <stop offset="0" stopColor="#020203" />
          <stop offset="1" stopColor="#0d0d0f" />
        </radialGradient>
      </defs>
      <rect width={W} height={H} className={styles.resin} />
      {p.streaks.map((t, i) => (
        <rect key={`s${i}`} x={t.x} y={t.y - R * 0.82} width={t.w} height={R * 1.64} rx={R * 0.82} fill={`url(#${id}-streak)`} />
      ))}
      {p.discs.map((d, i) => (
        <circle key={`d${i}`} cx={d.x} cy={d.y} r={R} fill={`url(#${id}-disc)`} />
      ))}
      {p.voids.map((v, i) => (
        <g key={`v${i}`}>
          <ellipse cx={v.x} cy={v.y} rx={v.rx} ry={v.ry} fill={`url(#${id}-void)`} />
          {/* the one marked defect: an amber hairline around each air pocket */}
          <ellipse cx={v.x} cy={v.y} rx={v.rx + 5} ry={v.ry + 5} className={styles.voidRing} />
        </g>
      ))}
    </svg>
  );
}

export function CarbonLayup({ className }: { className?: string }) {
  const g = spaceGrade.graphic;
  return (
    <figure className={`${styles.figure} ${className ?? ""}`} role="img" aria-label={g.alt}>
      <p className={`t-label ${styles.kicker}`} aria-hidden="true">
        {g.kicker}
      </p>
      <div className={styles.panels} aria-hidden="true">
        <div className={styles.panel} data-kind="standard">
          <div className={styles.frame}>
            <Drawing kind="standard" />
          </div>
          <p className={styles.title}>{g.standard.title}</p>
          <p className={styles.note}>{g.standard.note}</p>
        </div>
        <div className={styles.panel} data-kind="kinetiq">
          <div className={styles.frame}>
            <Drawing kind="kinetiq" />
          </div>
          <p className={styles.title}>{g.kinetiq.title}</p>
          <p className={styles.note}>{g.kinetiq.note}</p>
        </div>
      </div>
    </figure>
  );
}
