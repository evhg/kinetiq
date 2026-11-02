import styles from "./GripContact.module.css";

/**
 * G18 "How the face grips" (review, 2026-11-02: owner note 2a asks to show HOW the ball gets its slice; K17 alone shows
 * a ball on a textured face). A magnified side section at the contact: the face sweeping across under the ball (the
 * straight arrow), its moulded micro-domes catching the felt, which drags with the face instead of sliding (the warm
 * fibres in the patch), and the ball leaving with more spin (the curved arrow, the way a sweep to the right turns it).
 * The physics it draws, and nothing more: friction acts along the face, so a brushed contact turns into spin; it says
 * nothing about how long the ball stays on the face. A diagram, not a measurement (CLAIMS.md row 49). The words are the
 * HTML legend (15 px and up), so the drawing carries no text and reads at any width. Server component: no script.
 */

const W = 600;
const H = 440;
const CX = 300;
const CY = 200;
const R = 140;
const FACE_Y = 330;
const FACE_B = 384;
const PITCH = 14;
const SPIN_R = 168;

/** The ball's outline above the face, a flat chord where it presses on the domes. */
const half = Math.sqrt(R * R - (FACE_Y - CY) ** 2);
const ball = `M${CX - half} ${FACE_Y} A${R} ${R} 0 1 1 ${CX + half} ${FACE_Y} Z`;

/** The face's top edge: a row of micro-domes. */
const domes = (() => {
  let d = `M24 ${FACE_Y + 2}`;
  for (let x = 24; x < W - 24; x += PITCH) d += ` a${PITCH / 2} 5 0 0 1 ${PITCH} 0`;
  return `${d} V${FACE_B} H24 Z`;
})();

/** Felt fuzz on the ball's outline: short strokes, out along the normal, deterministic. */
const fuzz = (() => {
  const out: string[] = [];
  // from the right end of the chord, up over the top, to its left end (decreasing angle on screen)
  const a0 = Math.atan2(FACE_Y - CY, half) - 0.06;
  const span = Math.PI + 2 * a0 - 0.12;
  for (let i = 0; i < 96; i++) {
    const ang = a0 - ((i + 0.5) / 96) * span;
    const len = 5 + ((i * 37) % 7);
    const x0 = CX + R * Math.cos(ang);
    const y0 = CY + R * Math.sin(ang);
    const x1 = CX + (R + len) * Math.cos(ang + 0.03);
    const y1 = CY + (R + len) * Math.sin(ang + 0.03);
    out.push(`M${x0.toFixed(1)} ${y0.toFixed(1)}L${x1.toFixed(1)} ${y1.toFixed(1)}`);
  }
  return out.join("");
})();

/** The pressed felt in the contact patch, dragged along the face's travel (to the right) into the domes. */
const drag = (() => {
  const out: string[] = [];
  for (let x = CX - half - 8; x <= CX + half + 4; x += 6) {
    const lean = 10 + ((x * 13) % 5);
    out.push(`M${x.toFixed(1)} ${FACE_Y - 9}L${(x + lean).toFixed(1)} ${FACE_Y - 1}`);
  }
  return out.join("");
})();

/** The spin: an arc around the ball, from its right side up over the top, the way a sweep to the right turns it. */
const pt = (deg: number, r = SPIN_R) => [CX + r * Math.cos((deg * Math.PI) / 180), CY + r * Math.sin((deg * Math.PI) / 180)];
const [s0x, s0y] = pt(10);
const [s1x, s1y] = pt(-125);
const spin = `M${s0x.toFixed(1)} ${s0y.toFixed(1)} A${SPIN_R} ${SPIN_R} 0 0 0 ${s1x.toFixed(1)} ${s1y.toFixed(1)}`;
// arrowhead along the tangent at the end (moving counter-clockwise on screen)
const tA = (-125 * Math.PI) / 180;
const tx = Math.sin(tA);
const ty = -Math.cos(tA);
const head = (x: number, y: number, dx: number, dy: number, s = 16) => {
  const nx = -dy;
  const ny = dx;
  return `M${(x - dx * s + nx * s * 0.55).toFixed(1)} ${(y - dy * s + ny * s * 0.55).toFixed(1)}L${x.toFixed(1)} ${y.toFixed(1)}L${(x - dx * s - nx * s * 0.55).toFixed(1)} ${(y - dy * s - ny * s * 0.55).toFixed(1)}`;
};
const spinHead = head(s1x + tx * 6, s1y + ty * 6, tx, ty);

const SWEEP_Y = 414;
const sweep = `M170 ${SWEEP_Y}H430`;
const sweepHead = head(436, SWEEP_Y, 1, 0);

type Props = {
  /** The legend, in the order of the drawing's three marks: the sweep, the grip, the spin. */
  legend: { sweep: string; grip: string; spin: string };
  className?: string;
};

export function GripContact({ legend, className }: Props) {
  return (
    <figure className={`${styles.root} ${className ?? ""}`}>
      <svg className={styles.svg} viewBox={`0 0 ${W} ${H}`} aria-hidden="true" focusable="false">
        <defs>
          <radialGradient id="g18-patch" cx="50%" cy="50%" r="50%">
            <stop offset="0" stopColor="var(--amber)" stopOpacity="0.45" />
            <stop offset="1" stopColor="var(--amber)" stopOpacity="0" />
          </radialGradient>
          <radialGradient id="g18-ball" cx="38%" cy="30%" r="75%">
            <stop offset="0" stopColor="#3a3a33" />
            <stop offset="1" stopColor="#1d1d1f" />
          </radialGradient>
        </defs>
        {/* the face: graphite with its moulded domes along the top, a ply line inside */}
        <path className={styles.face} d={domes} />
        <path className={styles.ply} d={`M24 ${FACE_Y + 22}H${W - 24}M24 ${FACE_Y + 38}H${W - 24}`} />
        {/* the ball, pressed flat on the domes, its felt fuzz around it */}
        <path className={styles.ball} d={ball} fill="url(#g18-ball)" />
        <path className={styles.fuzz} d={fuzz} />
        {/* the contact: warm light and the felt dragged along the face's travel */}
        <ellipse cx={CX} cy={FACE_Y - 2} rx={half + 34} ry={16} fill="url(#g18-patch)" />
        <path className={styles.drag} d={drag} />
        {/* the face's travel under the ball, and the spin it gives */}
        <path className={styles.arrow} d={sweep} />
        <path className={styles.arrow} d={sweepHead} />
        <path className={styles.arrow} d={spin} />
        <path className={styles.arrow} d={spinHead} />
      </svg>
      <figcaption>
        <ol className={styles.legend}>
          <li>
            <svg className={styles.glyph} viewBox="0 0 32 16" aria-hidden="true" focusable="false">
              <path d="M2 8H28M21 2L28 8L21 14" />
            </svg>
            <span>{legend.sweep}</span>
          </li>
          <li>
            <svg className={styles.glyph} viewBox="0 0 32 16" aria-hidden="true" focusable="false">
              <path d="M3 5L9 12M11 5L17 12M19 5L25 12" />
            </svg>
            <span>{legend.grip}</span>
          </li>
          <li>
            <svg className={styles.glyph} viewBox="0 0 32 16" aria-hidden="true" focusable="false">
              <path d="M27 14A12 12 0 0 0 6 7M4 2L6 7L11 6" />
            </svg>
            <span>{legend.spin}</span>
          </li>
        </ol>
      </figcaption>
    </figure>
  );
}
