"use client";

import { useRef } from "react";
import { Still } from "@/components/media/Still";
import { useMotion } from "@/components/motion/MotionProvider";
import { PinnedChapter } from "@/components/motion/PinnedChapter";
import { gsap, useGSAP } from "@/lib/gsap";
import styles from "./EdgeOptions.module.css";

/**
 * /preview/edge-to-edge (owner, 2026-11-11: "a private preview page so I can preview each option including the
 * animation"): the three candidates for the image under the Sweet spot's "Edge to edge.", each played by scroll the
 * way it would run on the landing page. Pinned and scrubbed from 900 px with motion (PinnedChapter, the site's CSS
 * pin); below 900 px an unpinned scrub while the image crosses the screen; reduced motion and the server render show
 * each option's final frame. Every frame is a Still with a Pace twin, so the header's feel toggle switches them.
 * The stages of A and B are pixel-registered passes of one render: stacked, each fades in over the one before.
 */

type Layer = { id: string; alt: string };
type Option = {
  key: "a" | "b" | "c";
  next: string;
  name: string;
  line: string;
  /** Phone frame shape: the ephone crop's own aspect ratio. */
  phone: "portrait" | "band";
  layers: Layer[];
  /** The scrubbed timeline (0 to 1): the same one pinned and, below 900 px, while the image crosses the screen. */
  build: (tl: gsap.core.Timeline, layer: (i: number) => string) => void;
};

const A_STAGES = ["s000", "s020", "s040", "s060", "s080", "s100", "s100-line"];
const B_STAGES = ["s1", "s2", "s3", "s4", "s5", "s6"];

/** Each layer after the first fades in over the one below it, one after another between `from` and `to`. */
function dissolve(tl: gsap.core.Timeline, layer: (i: number) => string, count: number, from: number, to: number, overlap = 0) {
  const step = (to - from) / (count - 1);
  for (let i = 1; i < count; i++) {
    tl.fromTo(layer(i), { opacity: 0 }, { opacity: 1, duration: step * (1 + overlap), ease: "none", immediateRender: true }, from + step * (i - 1));
  }
}

const OPTIONS: Option[] = [
  {
    key: "a",
    next: "option-b",
    name: "The face fills with light",
    line: "A warm light spreads from the centre of the face and reaches the edge all the way round at once, then a fine line draws where the flat face ends: the sweet spot, as designed, runs edge to edge.",
    phone: "portrait",
    layers: A_STAGES.map((s, i) => ({
      id: `E2E-A-${s}`,
      alt:
        i === 0
          ? "A KINETIQ racket face-on in the dark studio."
          : i === A_STAGES.length - 1
            ? "The whole face lit warm out to its edge, with a fine bright line where the flat face ends."
            : "A warm light spreading across the face toward its edge.",
    })),
    build: (tl, layer) => {
      tl.fromTo(`.${styles.frame}`, { scale: 1.05 }, { scale: 1, duration: 0.7, ease: "power2.out", immediateRender: true }, 0);
      // the light, 0 to 100 % in five steps, then the line once the face is full
      dissolve(tl, layer, A_STAGES.length - 1, 0.06, 0.7);
      tl.fromTo(layer(A_STAGES.length - 1), { opacity: 0 }, { opacity: 1, duration: 0.12, ease: "power1.inOut", immediateRender: true }, 0.76);
      tl.to({}, { duration: 0.12 }, 0.88);
    },
  },
  {
    key: "b",
    next: "option-c",
    name: "Flat to the edge",
    line: "Seen along the face, a warm line runs from the throat to the crown, dead straight across the flat face, and bends only where it meets the edge: flat, and sweet, as designed, right out to it.",
    phone: "band",
    layers: B_STAGES.map((s, i) => ({
      id: `E2E-B-${s}`,
      alt: i === 0 ? "A KINETIQ face seen low along its surface, a warm line of light near the throat." : "The warm line further along the face toward the crown.",
    })),
    build: (tl, layer) => {
      tl.fromTo(`.${styles.frame}`, { scale: 1.04 }, { scale: 1, duration: 0.8, ease: "power2.out", immediateRender: true }, 0);
      // the line travels throat to crown; each pass overlaps the next a little so the light never blinks
      dissolve(tl, layer, B_STAGES.length, 0.06, 0.82, 0.35);
      tl.to({}, { duration: 0.1 }, 0.9);
    },
  },
  {
    key: "c",
    next: "edge-reference",
    name: "A ball at the very edge",
    line: "A ball meets the face at its widest point, right at the rim, as soft rings of light spread evenly across the whole face: as designed, a shot that far out still meets the sweet spot.",
    phone: "portrait",
    layers: [
      { id: "E2E-C-full", alt: "A padel ball pressed onto a KINETIQ face at its widest point, right at the rim." },
      { id: "E2E-C-rings", alt: "The same ball at the rim, soft rings of warm light spreading evenly across the face." },
      { id: "E2E-Cwide-rings", alt: "The whole racket, the ball at the rim and the rings across the face." },
    ],
    build: (tl, layer) => {
      tl.fromTo(layer(0), { scale: 1.06 }, { scale: 1, duration: 0.4, ease: "power2.out", immediateRender: true }, 0)
        .fromTo(layer(1), { scale: 1.06 }, { scale: 1, duration: 0.4, ease: "power2.out", immediateRender: true }, 0)
        // the rings come up over the face
        .fromTo(layer(1), { opacity: 0 }, { opacity: 1, duration: 0.24, ease: "power1.inOut", immediateRender: true }, 0.1)
        // then the camera pulls back: the close frame grows and goes, the whole racket settles in
        .to([layer(0), layer(1)], { scale: 1.12, duration: 0.3, ease: "power1.in" }, 0.5)
        .fromTo(layer(2), { opacity: 0, scale: 1.18 }, { opacity: 1, scale: 1, duration: 0.3, ease: "power2.out", immediateRender: true }, 0.52)
        .to({}, { duration: 0.14 }, 0.86);
    },
  },
];

const PHONE_MEDIA = "(max-width: 899px)";

function OptionChapter({ option, index }: { option: Option; index: number }) {
  const beat = useRef<HTMLDivElement>(null);
  const { motionOn } = useMotion();
  const layer = (i: number) => `.${styles.layer}[data-layer="${i}"]`;

  // Below the pin (phones, tablets): the same timeline, scrubbed while the image crosses the screen.
  useGSAP(
    () => {
      const el = beat.current;
      if (!motionOn || !el) return;
      const mm = gsap.matchMedia();
      mm.add(`(prefers-reduced-motion: no-preference) and ${PHONE_MEDIA}`, () => {
        const media = el.querySelector(`.${styles.media}`);
        const tl = gsap.timeline({
          defaults: { ease: "none" },
          scrollTrigger: { trigger: media, start: "top 62%", end: "top 10%", scrub: 0.5, invalidateOnRefresh: true },
        });
        option.build(tl, layer);
      });
      return () => mm.revert();
    },
    { scope: beat, dependencies: [motionOn], revertOnUpdate: true },
  );

  return (
    <PinnedChapter
      id={`option-${option.key}`}
      nextId={option.next}
      labelledBy={`option-${option.key}-eyebrow option-${option.key}-title`}
      className={`pin-layered ${styles.chapter}`}
      length={2}
      build={(tl) => option.build(tl, layer)}
    >
      <div ref={beat} className={`beat ${styles.beat}`} data-phone={option.phone}>
        <div className={styles.words}>
          <p id={`option-${option.key}-eyebrow`} className="t-eyebrow">
            {`Option ${option.key.toUpperCase()} · ${index + 1} of ${OPTIONS.length}`}
          </p>
          <h2 id={`option-${option.key}-title`} className={`t-h2 ${styles.title}`}>
            {option.name}
          </h2>
          <p className={`t-lead ${styles.line}`}>{option.line}</p>
        </div>
        <div className={styles.media}>
          <div className={styles.frame}>
            {option.layers.map((l, i) => (
              <div key={l.id} className={styles.layer} data-layer={i}>
                <Still
                  id={l.id}
                  crop="ewide"
                  phoneCrop="ephone"
                  phoneMedia={PHONE_MEDIA}
                  sizes="(min-width: 900px) 92vw, 100vw"
                  alt={l.alt}
                  bare={false}
                  loading={i === 0 && index === 0 ? "eager" : "lazy"}
                  className={styles.still}
                />
              </div>
            ))}
          </div>
        </div>
      </div>
    </PinnedChapter>
  );
}

export function EdgeOptions() {
  return (
    <>
      {OPTIONS.map((o, i) => (
        <OptionChapter key={o.key} option={o} index={i} />
      ))}
    </>
  );
}
