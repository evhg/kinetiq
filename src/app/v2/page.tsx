import type { Metadata } from "next";
import { SiteFooter, SiteHeader } from "@/components/chrome/Chrome";
import { BornWhole } from "@/components/landing/BornWhole";
import { ChooseFeel } from "@/components/landing/ChooseFeel";
import { Durability } from "@/components/landing/Durability";
import { Editions } from "@/components/landing/Editions";
import { Feel } from "@/components/landing/Feel";
import { Hero } from "@/components/landing/Hero";
import { Holes } from "@/components/landing/Holes";
import { Identical } from "@/components/landing/Identical";
import { Precision } from "@/components/landing/Precision";
import { SealedCore } from "@/components/landing/SealedCore";
import { SpaceGrade } from "@/components/landing/SpaceGrade";
import { Specifications } from "@/components/landing/Specifications";
import { Surface } from "@/components/landing/Surface";
import { SweetSpot } from "@/components/landing/SweetSpot";
import { Unibody } from "@/components/landing/Unibody";
import { DetailRail } from "@/components/v2/DetailRail";
import { FeelWipe } from "@/components/v2/FeelWipe";
import { SeqChapter } from "@/components/v2/SeqChapter";
import { TypeZoom } from "@/components/v2/TypeZoom";
import { WordFinale } from "@/components/v2/WordFinale";
import { v2 } from "@/content/v2";

/**
 * /v2 (owner, 2026-11-13: "I'd like to see 1 to 7 all of it together, but create a second version of the landing page,
 * keep the existing landing page"): every section of / in its order, with seven Apple-style scroll effects between them:
 * (6) the giant word into Unibody, (3) the exploded layers, (1) the racket made, (2) the dive into a hole, (7) the details
 * sideways, (4) the feel switch, (5) the closing line lit word by word. A preview on the preview/scroll-v2 branch:
 * linked from nowhere, never indexed, behind the NDA gate like every page (src/proxy.ts).
 */
export const metadata: Metadata = {
  title: "KINETIQ, version 2",
  robots: { index: false, follow: false, nocache: true },
};

export default function V2() {
  return (
    <>
      <SiteHeader compactCta />
      <main id="main">
        <Hero />
        <TypeZoom />
        <Unibody nextId={v2.explode.id} />
        <SeqChapter
          id={v2.explode.id}
          nextId="aerospace-grade"
          sequence="V2-explode"
          eyebrow={v2.explode.eyebrow}
          headline={v2.explode.headline}
          steps={v2.explode.steps}
          alt={v2.explode.alt}
          fallback={{ id: "K13", phoneCrop: "portrait" }}
          copyAt="right"
        />
        <SpaceGrade />
        <SeqChapter
          id={v2.assemble.id}
          nextId="born-whole"
          sequence="V2-assemble"
          eyebrow={v2.assemble.eyebrow}
          headline={v2.assemble.headline}
          steps={v2.assemble.steps}
          alt={v2.assemble.alt}
          fallback={{ id: "K06-full", phoneCrop: "card" }}
          length={3.4}
        />
        <BornWhole />
        <Precision />
        <SeqChapter
          id={v2.dive.id}
          nextId="holes"
          sequence="V2-dive"
          eyebrow={v2.dive.eyebrow}
          headline={v2.dive.headline}
          steps={v2.dive.steps}
          alt={v2.dive.alt}
          fallback={{ id: "K04-full", phoneCrop: "card" }}
          length={2.6}
        />
        <Holes />
        <SealedCore />
        <SweetSpot />
        <Surface />
        <Feel />
        <Durability />
        <DetailRail />
        {/* Focus targets for the Skip links of the two chapters before them (these sections take no focus of their own). */}
        <div id="v2-identical" tabIndex={-1}>
          <Identical />
        </div>
        <FeelWipe />
        <div id="v2-feels" tabIndex={-1}>
          <ChooseFeel />
        </div>
        <Specifications />
        <Editions />
        <WordFinale />
      </main>
      <SiteFooter />
    </>
  );
}
