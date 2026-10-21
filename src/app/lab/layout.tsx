import type { Metadata } from "next";
import type { ReactNode } from "react";
import { notFound } from "next/navigation";

// Review pages for the data graphics. Never served in production.
export const metadata: Metadata = { title: "Lab | KINETIQ", robots: { index: false, follow: false } };

export default function LabLayout({ children }: { children: ReactNode }) {
  if (process.env.NODE_ENV === "production" && process.env.KQ_LAB !== "1") notFound();
  return <main id="main" style={{ minHeight: "100svh" }}>{children}</main>;
}
