import type { Metadata, Viewport } from "next";
import { MotionProvider } from "@/components/motion/MotionProvider";
import { SmoothScroll } from "@/components/motion/SmoothScroll";
import { motionInitScript } from "@/lib/motion-preference";
import "./globals.css";

export const metadata: Metadata = {
  title: "KINETIQ",
  description: "Pipeline smoke test for the KINETIQ website.",
  robots: { index: false, follow: false },
};

export const viewport: Viewport = {
  themeColor: "#121212",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" data-motion="off" suppressHydrationWarning>
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
