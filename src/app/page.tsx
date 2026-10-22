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
import { SpecStrip } from "@/components/landing/SpecStrip";
import { Unibody } from "@/components/landing/Unibody";
import { meta } from "@/content/copy";
import { productMetadata } from "@/lib/product-metadata";

// The product's title, description and social cards live with the pages that sell it, never in the root layout.
export const metadata: Metadata = productMetadata({ absolute: meta.title });

export default function Home() {
  return (
    <>
      <SiteHeader compactCta />
      <main id="main">
        <Hero />
        <SpecStrip />
        <Unibody />
        <BornWhole />
        <Precision />
        <Holes />
        <Durability />
        <Feel />
        <Identical />
        <ChooseFeel />
        <Editions />
        <Finale />
      </main>
      <SiteFooter />
    </>
  );
}
