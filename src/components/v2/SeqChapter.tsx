"use client";

import { useRef } from "react";
import { Still } from "@/components/media/Still";
import { Swivel, hasSequence, type SwivelHandle } from "@/components/media/Swivel";
import { useMotion } from "@/components/motion/MotionProvider";
import generated from "@/content/sequences.generated.json";
import { gsap } from "@/lib/gsap";
import { useFeel } from "@/lib/feel-store";
import { V2Chapter } from "./V2Chapter";
import styles from "./SeqChapter.module.css";

type Entry = { frames: number; widths: number[]; formats: Record<string, { hash: string }> };
const manifest = generated as unknown as Record<string, Entry>;

/** Portrait screens take the 9:16 phone sequence (Swivel's portraitQuery, and the poster's art direction). */
const PORTRAIT = "(max-aspect-ratio: 4/5)";

type Props = {
  id: string;
  nextId: string;
  /** The sequence's common name: `<sequence>-<feel>-desktop|phone` in sequences.generated.json (e.g. "V2-assemble"). */
  sequence: string;
  eyebrow: string;
  headline: string;
  steps: string[];
  alt: string;
  /** Shown until the sequence is exported (a still in the same spirit), so the chapter reads whole without it. */
  fallback: { id: string; crop?: string; phoneCrop?: string };
  /** Pinned scroll length in screens. */
  length?: number;
};

/** One frame of an exported sequence, every width, as srcset (the file names Swivel downloads). */
function frameSet(name: string, frame: number, type: "avif" | "webp") {
  const e = manifest[name];
  const f = e?.formats[type];
  if (!e || !f) return null;
  const n = String(frame).padStart(3, "0");
  return e.widths.map((w) => `/stills/seq/${name}/${n}-${w}.${f.hash}.${type} ${w}w`).join(", ");
}

/**
 * Effects 1 to 3 (assembly, the dive into a hole, the exploded layers): a full-frame sequence scrubbed by scroll, an
 * Apple-style chapter. From 900 px the stage is pinned and the frames fill it, with the words in the lower left and
 * each step lighting as its part of the sequence plays; below 900 px the frame scrolls by in its own 9:16 box (the
 * phone sequence) and the sequence plays as it crosses the screen, with the steps under it. Under the canvas is a
 * picture of the sequence's first frame (Swivel draws over it from frame 1); with reduced motion, its last frame, the
 * finished state. Until the Mac's frames are exported, `fallback` shows instead and the steps simply read.
 */
export function SeqChapter({ id, nextId, sequence, eyebrow, headline, steps, alt, fallback, length = 3 }: Props) {
  const swivel = useRef<SwivelHandle>(null);
  const { feel } = useFeel();
  const { motionOn } = useMotion();
  const has = hasSequence(sequence);
  const desk = `${sequence}-${feel}-desktop`;
  const phone = `${sequence}-${feel}-phone`;
  const last = (name: string) => Math.max(0, (manifest[name]?.frames ?? 1) - 1);
  const pick = (name: string) => (motionOn ? 0 : last(name));
  const titleId = `${id}-title`;

  return (
    <V2Chapter
      id={id}
      nextId={nextId}
      labelledBy={titleId}
      length={length}
      className={styles.chapter}
      flow={`.${styles.frame}`}
      flowStart="top 80%"
      flowEnd="bottom 35%"
      build={(tl, mode) => {
        const state = { p: 0 };
        const stepEls = gsap.utils.toArray<HTMLElement>(`.${styles.step}`);
        gsap.set(stepEls, { opacity: 0.28 });
        if (mode === "pin") {
          gsap.set(`.${styles.copy}`, { autoAlpha: 0, y: 24 });
          tl.to(`.${styles.copy}`, { autoAlpha: 1, y: 0, duration: 0.06 }, 0.02);
        }
        // The sequence runs over most of the chapter and holds its last frame at the end.
        const t0 = mode === "pin" ? 0.06 : 0;
        const span = mode === "pin" ? 0.84 : 1;
        tl.fromTo(state, { p: 0 }, { p: 1, duration: span, immediateRender: true, onUpdate: () => swivel.current?.progress(state.p) }, t0);
        // Each step lights for its share of the sequence; the last stays lit.
        const each = span / stepEls.length;
        stepEls.forEach((el, i) => {
          const at = t0 + i * each;
          tl.to(el, { opacity: 1, duration: Math.min(0.04, each / 3) }, at);
          if (i < stepEls.length - 1) tl.to(el, { opacity: 0.28, duration: Math.min(0.04, each / 3) }, at + each);
        });
        if (mode === "pin") tl.to({}, { duration: 0.1 });
        return () => swivel.current?.progress(0);
      }}
    >
      <div className={styles.stage}>
        <div className={styles.frame} aria-hidden="true">
          {has ? (
            <picture>
              {manifest[phone] && <source media={PORTRAIT} type="image/avif" srcSet={frameSet(phone, pick(phone), "avif") ?? undefined} sizes="100vw" />}
              {manifest[phone] && <source media={PORTRAIT} type="image/webp" srcSet={frameSet(phone, pick(phone), "webp") ?? undefined} sizes="100vw" />}
              <source type="image/avif" srcSet={frameSet(desk, pick(desk), "avif") ?? undefined} sizes="100vw" />
              <img
                className={styles.picture}
                srcSet={frameSet(desk, pick(desk), "webp") ?? undefined}
                sizes="100vw"
                alt=""
                loading="lazy"
                decoding="async"
              />
            </picture>
          ) : (
            <Still id={fallback.id} crop={fallback.crop} phoneCrop={fallback.phoneCrop} phoneMedia={PORTRAIT} alt="" sizes="100vw" className={styles.picture} />
          )}
          {has && <Swivel ref={swivel} sequence={sequence} portraitQuery={PORTRAIT} lead={1.5} className={styles.canvas} />}
          <span className={styles.scrim} />
        </div>
        <div className={styles.copy}>
          <p className="t-eyebrow">{eyebrow}</p>
          <h2 id={titleId} className={`t-h2 ${styles.title}`}>
            {headline}
          </h2>
          <p className="visually-hidden">{alt}</p>
          <ol className={styles.steps}>
            {steps.map((s, i) => (
              <li key={s} className={styles.step}>
                <span className={styles.num} aria-hidden="true">
                  {String(i + 1).padStart(2, "0")}
                </span>
                {s}
              </li>
            ))}
          </ol>
        </div>
      </div>
    </V2Chapter>
  );
}
