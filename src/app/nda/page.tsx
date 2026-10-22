import type { Metadata } from "next";
import { NdaGate } from "@/components/nda/NdaGate";
import { ndaCopy } from "@/content/nda";

// The NDA gate. src/proxy.ts rewrites every page request without the kq_nda cookie to this route (the URL stays
// as typed), and redirects /nda to / once the cookie is set. Metadata overrides the layout's whole set: a plain
// title, a confidential description, noindex and no og:image, so link previews show nothing about the product.
export const metadata: Metadata = {
  title: { absolute: ndaCopy.meta.title },
  description: ndaCopy.meta.description,
  robots: { index: false, follow: false },
  openGraph: {
    type: "website",
    siteName: ndaCopy.meta.title,
    title: ndaCopy.meta.title,
    description: ndaCopy.meta.description,
  },
  twitter: {
    card: "summary",
    title: ndaCopy.meta.title,
    description: ndaCopy.meta.description,
  },
};

export default function NdaPage() {
  return <NdaGate />;
}
