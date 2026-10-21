"use client";

import { PinnedChapter } from "@/components/motion/PinnedChapter";
import { claims } from "@/content/claims";

const layers = [
  { name: "Carbon face", glue: false },
  { name: "Glue", glue: true },
  { name: "Foam core", glue: false },
  { name: "Glue", glue: true },
  { name: "Carbon face", glue: false },
  { name: "Frame", glue: false },
];

const beats = [
  { title: "Most rackets are assembled.", body: "Two faces, a foam core and a frame, glued and pressed together. Then the holes are drilled through." },
  { title: "Every joint is a compromise.", body: "Glue lines soften the feel. Drilled holes cut the fibres. No two rackets come out quite the same." },
  { title: "Ours leaves the mould in one piece.", body: claims.onePieceDetail },
];

export function OnePiece() {
  return (
    <PinnedChapter
      id="one-piece"
      nextId="precision"
      labelledBy="one-piece-title"
      className="onepiece"
      length={2.6}
      build={(tl) => {
        tl.to(".beat-1", { autoAlpha: 0, y: -20, duration: 0.25 }, 0.75)
          .from(".beat-2", { autoAlpha: 0, y: 20, duration: 0.25 }, 1.05)
          .to(".layer", { y: 0, duration: 1, ease: "power2.inOut" }, 1.1)
          .to(".layer-label", { autoAlpha: 0, duration: 0.3 }, 1.4)
          .to(".layer--glue", { autoAlpha: 0, duration: 0.4 }, 1.5)
          .to(".beat-2", { autoAlpha: 0, y: -20, duration: 0.25 }, 2.0)
          .from(".beat-3", { autoAlpha: 0, y: 20, duration: 0.25 }, 2.3)
          .from(".stack-one", { autoAlpha: 0, duration: 0.3 }, 2.3)
          .to({}, { duration: 0.4 });
      }}
    >
      <div className="onepiece-copy">
        <h2 id="one-piece-title" className="eyebrow-title">
          One piece
        </h2>
        <div className="beats">
          {beats.map((b, i) => (
            <div className={`beat beat-${i + 1}`} key={b.title}>
              <p className="beat-title">{b.title}</p>
              <p className="beat-body">{b.body}</p>
            </div>
          ))}
        </div>
      </div>
      <div className="stack-scene" aria-hidden="true">
        <div className="stack">
          {layers.map((l, i) => (
            <div
              key={`${l.name}-${i}`}
              className={`layer${l.glue ? " layer--glue" : ""}${l.name === "Frame" ? " layer--frame" : ""}`}
              style={{ "--i": i } as React.CSSProperties}
            >
              <span className="layer-plate" />
              <span className="layer-label">{l.name}</span>
            </div>
          ))}
        </div>
        <p className="stack-one">1 part</p>
      </div>
    </PinnedChapter>
  );
}
