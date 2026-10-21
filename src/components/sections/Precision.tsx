"use client";

import { useRef } from "react";
import { PinnedChapter } from "@/components/motion/PinnedChapter";
import { Cta } from "@/components/Cta";
import { claims } from "@/content/claims";

const compare = [
  { name: "A sheet of paper", um: 100 },
  { name: "A human hair", um: 70 },
  { name: "KINETIQ, every surface", um: claims.record.value, ours: true },
];

export function Precision() {
  const counter = useRef<HTMLSpanElement>(null);
  return (
    <>
      <PinnedChapter
        id="precision"
        nextId="precision-after"
        labelledBy="precision-title"
        className="precision"
        length={2}
        build={(tl) => {
          const num = { v: 500 };
          const write = (v: number) => {
            if (counter.current) counter.current.textContent = String(Math.round(v));
          };
          write(num.v);
          tl.to(num, {
            v: claims.record.value,
            duration: 1.4,
            ease: "power2.out",
            onUpdate: () => write(num.v),
          }, 0)
            .from(".bar-fill", { scaleX: 0, duration: 0.8, stagger: 0.15, ease: "power2.out" }, 0.3)
            .from(".precision-headline", { autoAlpha: 0, y: 24, duration: 0.4 }, 1.3)
            .to({}, { duration: 0.5 });
          // Motion switched off mid-way: show the real number again.
          return () => write(claims.record.value);
        }}
      >
        <h2 id="precision-title" className="eyebrow-title">
          Precision
        </h2>
        <p className="record" aria-label={`${claims.record.value} ${claims.record.unit}`}>
          <span ref={counter} className="record-num">
            {claims.record.value}
          </span>
          <span className="record-unit">{claims.record.unit}</span>
        </p>
        <p className="precision-headline display-2">{claims.record.headline}</p>
        <ul className="bars">
          {compare.map((c) => (
            <li key={c.name} className={c.ours ? "bar bar--ours" : "bar"}>
              <span className="bar-name">{c.name}</span>
              <span className="bar-track" aria-hidden="true">
                <span className="bar-fill" style={{ transform: `scaleX(${c.um / 100})` }} />
              </span>
              <span className="bar-value">{c.um} µm</span>
            </li>
          ))}
        </ul>
      </PinnedChapter>
      <div id="precision-after" className="beat-cta" tabIndex={-1}>
        <p className="beat-cta-line">{claims.record.detail}</p>
        <Cta />
      </div>
    </>
  );
}
