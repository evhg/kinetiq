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
import { SpaceGrade } from "@/components/landing/SpaceGrade";
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
      {/* A climactic rise (owner, 2026-10-28: "Re-plan the storytelling ... to create a climactic rise"): meet it, see how
          it is made, reach the peak, feel the payoff, choose it (DESIGN.md "Page"). */}
      <main id="main">
        <Hero />
        {/* How it is made, rising: what it is (the first unibody), what it is made of, the one mould, 15 microns, then the
            peak, the moulded holes, and what they keep closed, the sealed core. */}
        <Unibody />
        <SpaceGrade />
        <BornWhole />
        <Precision />
        <Holes />
        <SealedCore />
        {/* The payoff, what all of that gives you: the sweet spot edge to edge, the feel, the five years. */}
        <SweetSpot />
        <Feel />
        <Durability />
        {/* Choose it: sameness, feel, the whole drawing, edition. */}
        <Identical />
        <ChooseFeel />
        <Specifications />
        <Editions />
        <Finale />
      </main>
      <SiteFooter />
    </>
  );
}
