import { Hero } from "@/components/sections/Hero";
import { OnePiece } from "@/components/sections/OnePiece";
import { Precision } from "@/components/sections/Precision";
import { Feel } from "@/components/sections/Feel";
import { Identical } from "@/components/sections/Identical";
import { Swiss } from "@/components/sections/Swiss";
import { Reserve } from "@/components/sections/Reserve";
import { Faq } from "@/components/sections/Faq";

export default function Home() {
  return (
    <main id="main">
      <Hero />
      <OnePiece />
      <Precision />
      <Feel />
      <Identical />
      <Swiss />
      <Reserve />
      <Faq />
    </main>
  );
}
