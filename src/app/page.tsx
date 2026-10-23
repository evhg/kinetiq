import type { Metadata } from "next";
import { SiteFooter, SiteHeader } from "@/components/chrome/Chrome";
import { BornWhole } from "@/components/landing/BornWhole";
import { ChooseFeel } from "@/components/landing/ChooseFeel";
import { Durability } from "@/components/landing/Durability";
import { Editions } from "@/components/landing/Editions";
import { Feel } from "@/components/landing/Feel";
import { Finale } from "@/components/landing/Finale";
import { Hero } from "@/components/landing/Hero";
import { Holes } from "@/components/landing/Holes";
import { Identical } from "@/components/landing/Identical";
import { Precision } from "@/components/landing/Precision";
import { SealedCore } from "@/components/landing/SealedCore";
import { Specifications } from "@/components/landing/Specifications";
import { SweetSpot } from "@/components/landing/SweetSpot";
import { Unibody } from "@/components/landing/Unibody";
import { meta } from "@/content/copy";
import { productMetadata } from "@/lib/product-metadata";

// The product's title, description and social cards live with the pages that sell it, never in the root layout.
export const metadata: Metadata = productMetadata({ absolute: meta.title });

export default function Home() {
  return (
    <>
      <SiteHeader compactCta />
      {/* Three movements, one idea per screen (DESIGN.md "Page"): meet it, prove it, choose it. */}
      <main id="main">
        {/* Meet it: what the racket does for you, then why. */}
        <Hero />
        <SweetSpot />
        <Unibody />
        <Feel />
        {/* Prove it, as one story (owner, 2026-10-23): made whole in one mould, exact to 15 microns, every hole moulded
            and lined, so the core never touches the air, so it lasts; then the whole drawing as the recap. */}
        <BornWhole />
        <Precision />
        <Holes />
        <SealedCore />
        <Durability />
        <Specifications />
        {/* Choose it: sameness, feel, edition. */}
        <Identical />
        <ChooseFeel />
        <Editions />
        <Finale />
      </main>
      <SiteFooter />
    </>
  );
}
