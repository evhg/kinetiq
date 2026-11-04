import { useId } from "react";

/**
 * The 1 mm line on K14 (the sweet spot's raking-light macro of the face running out to the rim; owner, 2026-11-03:
 * "When scrolling down sweet spot section the page doesn't pause and there is no animation?"). Traced from the export
 * (K14-wide at 2560 x 1440, the Command and Pace renders share one camera): for every 32 px column, the rim's outer edge
 * (the first pixel over luma 90 above the dark studio) and the inner end of its highlight (the 1.0 mm edge radius,
 * where the flat face begins), each fitted with a smooth polynomial (residual under 1 px at 1280). So the amber line
 * runs exactly where the flat face, the sweet spot, ends, and the lit band between it and the outline is the 1 mm the
 * lockup names (`FACE_INSET`, racket-shape.ts). Drawn in the still's own pixel space (1280 x 720 for the wide crop) and
 * fitted like the image (object-fit: cover, centred = xMidYMid slice); the portrait crop (x 0.385 to 0.835 of the
 * master, phones and the stacked tablets) uses the same paths through a narrower viewBox. Decorative: the lockup and the
 * still's alt text say it, so it is hidden from assistive technology.
 */
export const K14_RIM_OUTER =
  "M0 605.5 L32 576.2 64 548.3 96 521.5 128 496 160 471.5 192 448.2 224 425.9 256 404.6 288 384.2 320 364.8 352 346.2 384 328.5 416 311.6 448 295.4 480 279.9 512 265.2 544 251.1 576 237.7 608 224.8 640 212.6 672 200.9 704 189.8 736 179.2 768 169.1 800 159.5 832 150.3 864 141.6 896 133.4 928 125.5 960 118.2 992 111.2 1024 104.6 1056 98.4 1088 92.7 1120 87.3 1152 82.4 1184 77.8 1216 73.7 1248 69.9 1280 66.6";
export const K14_RIM_INNER =
  "M0 618.4 L32 588.2 64 559.3 96 531.7 128 505.3 160 480.2 192 456.1 224 433.2 256 411.3 288 390.4 320 370.5 352 351.5 384 333.4 416 316.1 448 299.6 480 283.9 512 268.9 544 254.6 576 241 608 228.1 640 215.7 672 204 704 192.8 736 182.1 768 172 800 162.4 832 153.3 864 144.6 896 136.4 928 128.7 960 121.4 992 114.5 1024 108 1056 101.9 1088 96.3 1120 91 1152 86.2 1184 81.7 1216 77.7 1248 74.1 1280 70.8";

const VIEW = { wide: "0 0 1280 720", portrait: "492.8 0 576 720" } as const;

export function SweetSpotEdge({ className, crop = "wide" }: { className?: string; crop?: keyof typeof VIEW }) {
  const glow = `${useId().replace(/[^a-zA-Z0-9]/g, "")}-glow`;
  return (
    <svg
      className={className}
      viewBox={VIEW[crop]}
      preserveAspectRatio="xMidYMid slice"
      aria-hidden="true"
      focusable="false"
      data-sweet-edge={crop}
    >
      <defs>
        <filter id={glow} x="-10%" y="-10%" width="120%" height="120%">
          <feGaussianBlur stdDeviation="2.2" />
        </filter>
      </defs>
      {/* the 1 mm line where the flat face ends: a soft amber glow under a fine amber-hot hairline */}
      <path d={K14_RIM_INNER} fill="none" stroke="var(--amber)" strokeWidth="3.2" opacity="0.55" filter={`url(#${glow})`} pathLength={1} data-sweet-line="" />
      <path d={K14_RIM_INNER} fill="none" stroke="var(--amber-hot)" strokeWidth="0.9" strokeLinecap="round" pathLength={1} data-sweet-line="" />
    </svg>
  );
}
