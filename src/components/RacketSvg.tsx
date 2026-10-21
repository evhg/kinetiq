import { HANDLE, racketSvgPath } from "@/lib/racket-shape";

// Server-rendered still of the racket: the LCP-safe image under the 3D scene,
// and the whole picture when motion is off or WebGL is missing.
export function RacketSvg({ className, title }: { className?: string; title: string }) {
  const scale = 100;
  const ox = 150;
  const oy = 170;
  const { outline, holes } = racketSvgPath(scale, ox, oy);
  const handleTop = oy - HANDLE.top * scale;
  const handleW = HANDLE.radius * 2 * scale;
  return (
    <svg className={className} viewBox="0 0 300 470" role="img" aria-label={title}>
      <defs>
        <linearGradient id="rk-face" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#3b3b3d" />
          <stop offset="0.45" stopColor="#151516" />
          <stop offset="1" stopColor="#060606" />
        </linearGradient>
        <linearGradient id="rk-sheen" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0.3" stopColor="#ffffff" stopOpacity="0" />
          <stop offset="0.5" stopColor="#ffffff" stopOpacity="0.16" />
          <stop offset="0.7" stopColor="#ffffff" stopOpacity="0" />
        </linearGradient>
        <pattern id="rk-weave" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
          <rect width="3" height="6" fill="#ffffff" opacity="0.035" />
        </pattern>
      </defs>
      <rect x={ox - handleW / 2} y={handleTop - 4} width={handleW} height={HANDLE.length * scale} rx={handleW / 2} fill="#0b0b0b" stroke="#2a2a2c" />
      <path d={`${outline} ${holes}`} fillRule="evenodd" fill="url(#rk-face)" stroke="#4a4a4e" strokeWidth="1.2" />
      <path d={`${outline} ${holes}`} fillRule="evenodd" fill="url(#rk-weave)" />
      <path d={`${outline} ${holes}`} fillRule="evenodd" fill="url(#rk-sheen)" />
    </svg>
  );
}
