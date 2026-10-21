import type { Metadata, Viewport } from "next";
import { Archivo, Saira } from "next/font/google";
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

export const metadata: Metadata = {
  title: meta.title,
  description: meta.description,
  robots: launched ? undefined : { index: false, follow: false },
};

export const viewport: Viewport = {
  themeColor: "#060607",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" className={`${archivo.variable} ${saira.variable}`} data-motion="on" suppressHydrationWarning>
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
