import { SiteFooter, SiteHeader } from "@/components/chrome/Chrome";
import { BornWhole } from "@/components/landing/BornWhole";
import { ChooseFeel } from "@/components/landing/ChooseFeel";
import { Editions } from "@/components/landing/Editions";
import { Feel } from "@/components/landing/Feel";
import { Finale } from "@/components/landing/Finale";
import { Hero } from "@/components/landing/Hero";
import { Holes } from "@/components/landing/Holes";
import { Identical } from "@/components/landing/Identical";
import { OnePiece } from "@/components/landing/OnePiece";
import { Precision } from "@/components/landing/Precision";
import { SpecStrip } from "@/components/landing/SpecStrip";

export default function Home() {
  return (
    <>
      <SiteHeader compactCta />
      <main id="main">
        <Hero />
        <SpecStrip />
        <OnePiece />
        <BornWhole />
        <Precision />
        <Holes />
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
