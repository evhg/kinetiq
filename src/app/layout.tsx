import type { Metadata, Viewport } from "next";
import { Archivo, Saira } from "next/font/google";
import { hasStill } from "@/components/media/Still";
import { MotionProvider } from "@/components/motion/MotionProvider";
import { SmoothScroll } from "@/components/motion/SmoothScroll";
import { meta } from "@/content/copy";
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

// scripts/stills.mjs writes /stills/og.jpg (1200 x 630) together with the K01-full "og" crop.
const ogImages = hasStill("K01-full", "og")
  ? [{ url: "/stills/og.jpg", width: 1200, height: 630, alt: "The KINETIQ padel racket in a single beam of light" }]
  : undefined;

export const metadata: Metadata = {
  metadataBase: siteUrl(),
  title: { default: meta.title, template: "%s | KINETIQ" },
  description: meta.description,
  robots: launched ? undefined : { index: false, follow: false },
  openGraph: {
    type: "website",
    siteName: "KINETIQ",
    title: meta.title,
    description: meta.description,
    images: ogImages,
  },
  twitter: {
    card: "summary_large_image",
    title: meta.title,
    description: meta.description,
    images: ogImages,
  },
};

export const viewport: Viewport = {
  themeColor: "#060607",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" className={`${archivo.variable} ${saira.variable}`} data-motion="off" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: motionInitScript }} />
      </head>
      <body>
        <MotionProvider>
          <SmoothScroll />
          {children}
        </MotionProvider>
      </body>
    </html>
  );
}
