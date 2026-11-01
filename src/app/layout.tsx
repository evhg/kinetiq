import type { CSSProperties } from "react";
import type { Metadata, Viewport } from "next";
import { Archivo, Saira } from "next/font/google";
import { MotionProvider } from "@/components/motion/MotionProvider";
import { Arrival } from "@/components/nda/Arrival";
import { SmoothScroll } from "@/components/motion/SmoothScroll";
import { DEFAULT_FEEL } from "@/content/site";
import { motionInitScript } from "@/lib/motion-preference";
import "./font-fallbacks.css";
import "./globals.css";

// Only `latin` is preloaded (2026-10-29): every word on the site is in it. latin-ext keeps its @font-face (unicode-range),
// so a name or address that needs it still loads it on demand, but its 112 KB no longer share a phone's first second
// with the CSS and the hero still (phone-profile LCP).
// adjustFontFallback is off for both: next/font's one Arial fallback is sized for Archivo at wdth 100 and weight 400, and
// the headings are wider and heavier, so the swap re-wrapped the hero. font-fallbacks.css (scripts/font-fallbacks.mjs)
// has one metric-matched fallback family per wdth and weight range instead; globals.css names them (--font-display-*).
const archivo = Archivo({
  subsets: ["latin"],
  axes: ["wdth"],
  display: "swap",
  adjustFontFallback: false,
  variable: "--font-archivo",
});

const saira = Saira({
  subsets: ["latin"],
  display: "swap",
  adjustFontFallback: false,
  variable: "--font-saira",
});

// Only the web font's own family goes into the stacks. Under Turbopack (Next 16's default build) adjustFontFallback: false
// is ignored, so var(--font-archivo) is still "Archivo, Archivo Fallback" and that local(Arial) face, sized for wdth 100 at
// weight 400, would win over the KQ faces wherever Arial is installed (iOS, macOS, Windows). globals.css reads these.
function webFace(fontFamily: string) {
  return fontFamily.split(",")[0].trim();
}
const fontFaces = {
  "--font-archivo-face": webFace(archivo.style.fontFamily),
  "--font-saira-face": webFace(saira.style.fontFamily),
} as CSSProperties;

const launched = process.env.NEXT_PUBLIC_LAUNCHED === "true";

// Absolute URLs for social cards: the configured site URL, else Vercel's production domain.
function siteUrl() {
  const raw =
    process.env.NEXT_PUBLIC_SITE_URL ||
    (process.env.VERCEL_PROJECT_PRODUCTION_URL ? `https://${process.env.VERCEL_PROJECT_PRODUCTION_URL}` : "");
  try {
    return raw ? new URL(raw) : undefined;
  } catch {
    return undefined;
  }
}

// Neutral on purpose (NDA gate): every route inherits this, including a 404 for a path the proxy lets through, so it
// carries no claim, description or og:image. The pages that sell the product add theirs (src/lib/product-metadata.ts).
export const metadata: Metadata = {
  metadataBase: siteUrl(),
  title: { default: "KINETIQ", template: "%s | KINETIQ" },
  robots: launched ? undefined : { index: false, follow: false },
};

export const viewport: Viewport = {
  themeColor: "#060607",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" className={`${archivo.variable} ${saira.variable}`} data-motion="off" data-feel={DEFAULT_FEEL} style={fontFaces} suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: motionInitScript }} />
      </head>
      <body>
        <MotionProvider>
          <SmoothScroll />
          <Arrival />
          {children}
        </MotionProvider>
      </body>
    </html>
  );
}
