import type { Metadata } from "next";
import { hasStill } from "@/components/media/Still";
import { meta } from "@/content/copy";

/**
 * The product's description and social cards, for the pages that sell it (/ and /reserve) and nothing else.
 * The root layout carries only a neutral "KINETIQ" title: anything the proxy does not gate (a 404 for an unknown
 * path, a route added later) inherits no claim, description or og:image (NDA gate, CLAUDE.md).
 */
// scripts/stills.mjs writes /stills/og.jpg (1200 x 630) together with the K01-full "og" crop.
const ogImages = hasStill("K01-full", "og")
  ? [{ url: "/stills/og.jpg", width: 1200, height: 630, alt: "The KINETIQ padel racket in a single beam of light" }]
  : undefined;

export function productMetadata(title: Metadata["title"]): Metadata {
  return {
    title,
    description: meta.description,
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
}
