import type { Metadata, Viewport } from "next";
import { Archivo, Saira } from "next/font/google";
import { MotionProvider } from "@/components/motion/MotionProvider";
import { Arrival } from "@/components/nda/Arrival";
import { SmoothScroll } from "@/components/motion/SmoothScroll";
import { DEFAULT_FEEL } from "@/content/site";
import { motionInitScript } from "@/lib/motion-preference";
import "./globals.css";

const archivo = Archivo({
  subsets: ["latin", "latin-ext"],
  axes: ["wdth"],
  display: "swap",
  variable: "--font-archivo",
});

const saira = Saira({
  subsets: ["latin", "latin-ext"],
  display: "swap",
  variable: "--font-saira",
});

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
    <html lang="en" className={`${archivo.variable} ${saira.variable}`} data-motion="off" data-feel={DEFAULT_FEEL} suppressHydrationWarning>
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
