import { useId } from "react";

/**
 * The sealed core, traced over the K03 cut-through (pinned Unibody chapter, sealed-core beat; CLAIMS.md row 30).
 * Drawn in the still's own pixel space (the "wide" crop, 1280 x 720 here) and fitted like the image (object-fit:
 * cover, centred = preserveAspectRatio xMidYMid slice), so every line sits on the render at any window size:
 * - one continuous amber line around the core on the cut face: the carbon shell closing around it;
 * - the core inside it lifted and stippled, so it reads as foam, not as a separate plate;
 * - an amber rim on both bores, with the lined wall stepping down inside each opening: the holes are lined in
 *   carbon all the way down.
 * Decorative (the words beside it say all of this), so it is hidden from assistive technology.
 */
const VIEW = "0 0 1280 720";

// The core's outline on the cut face, along the inner edge of the shell (traced from K03 at 2560 x 1440).
const CORE =
  "M450 343 L652.5 373.5 C677.5 377.5 690 395 690.5 417.5 L691.5 525 C691.5 545 682.5 557.5 667.5 557 L451 530 Z";
// The two bores on the top face (centre, radii). The far wall shows in the upper half of each opening.
const BORES = [
  { cx: 547.8, cy: 249.3, rx: 35.3, ry: 11.3 },
  { cx: 544.5, cy: 298.8, rx: 37.5, ry: 12.5 },
];
// How far each ring of the lined wall sits below the rim (image px), and how strongly it shows.
const WALL = [
  { dy: 3.2, o: 0.75 },
  { dy: 6.4, o: 0.5 },
  { dy: 9.6, o: 0.3 },
  { dy: 12.8, o: 0.16 },
];

export function SealedCoreTrace({ className }: { className?: string }) {
  const uid = useId().replace(/[^a-zA-Z0-9]/g, "");
  const cells = `${uid}-cells`;
  const core = `${uid}-core`;
  const glow = `${uid}-glow`;
  return (
    <svg className={className} viewBox={VIEW} preserveAspectRatio="xMidYMid slice" aria-hidden="true" focusable="false" data-seal-trace="">
      <defs>
        {/* closed-cell foam: a fine, irregular stipple, a little lighter than the cut face */}
        <pattern id={cells} width="9" height="8" patternUnits="userSpaceOnUse" patternTransform="skewY(8.5)" fill="#fff">
          <circle cx="2.2" cy="2.1" r="1.55" />
          <circle cx="6.8" cy="5.9" r="1.35" />
          <circle cx="6.6" cy="1.6" r="0.9" />
          <circle cx="2.6" cy="6.4" r="0.8" />
        </pattern>
        <clipPath id={core}>
          <path d={CORE} />
        </clipPath>
        {BORES.map((b, i) => (
          <clipPath key={i} id={`${uid}-bore${i}`}>
            <ellipse cx={b.cx} cy={b.cy} rx={b.rx} ry={b.ry} />
          </clipPath>
        ))}
        <filter id={glow} x="-20%" y="-20%" width="140%" height="140%">
          <feGaussianBlur stdDeviation="2.4" />
        </filter>
      </defs>

      <g data-seal-core="">
        <path d={CORE} fill="rgb(255 255 255 / 0.035)" />
        <rect x="440" y="330" width="260" height="235" fill={`url(#${cells})`} clipPath={`url(#${core})`} opacity="0.07" />
      </g>

      {/* the shell's line around the core, then its glow */}
      <path d={CORE} fill="none" stroke="var(--amber)" strokeWidth="5" opacity="0.45" filter={`url(#${glow})`} pathLength={1} data-seal-line="" />
      <path d={CORE} fill="none" stroke="var(--amber-hot)" strokeWidth="1.15" strokeLinejoin="round" pathLength={1} data-seal-line="" />

      {BORES.map((b, i) => (
        <g key={i} data-seal-bore="">
          <g clipPath={`url(#${uid}-bore${i})`}>
            {WALL.map((w) => (
              <ellipse key={w.dy} cx={b.cx} cy={b.cy + w.dy} rx={b.rx} ry={b.ry} fill="none" stroke="var(--amber)" strokeWidth="0.9" opacity={w.o} />
            ))}
          </g>
          <ellipse cx={b.cx} cy={b.cy} rx={b.rx} ry={b.ry} fill="none" stroke="var(--amber)" strokeWidth="4" opacity="0.4" filter={`url(#${glow})`} />
          <ellipse cx={b.cx} cy={b.cy} rx={b.rx} ry={b.ry} fill="none" stroke="var(--amber-hot)" strokeWidth="1.1" />
        </g>
      ))}
    </svg>
  );
}
