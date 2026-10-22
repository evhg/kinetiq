"use client";

import { useEffect, useRef, useState, useSyncExternalStore, type CSSProperties, type KeyboardEvent } from "react";
import { CourtPlan } from "@/components/graphics/CourtPlan";
import { MeasurementCard } from "@/components/graphics/MeasurementCard";
import { Still } from "@/components/media/Still";
import { useMotion } from "@/components/motion/MotionProvider";
import { tierById, type TierId } from "@/content/lineup";
import { reserveCopy } from "@/content/reserve";
import { feels, type FeelId } from "@/content/site";
import styles from "./Reserve.module.css";

type Slide =
  | {
      kind: "still";
      id: string;
      crop?: string;
      phoneCrop?: string;
      position?: string;
      /**
       * The whole product stays in frame on wide galleries, its edges feathered into the slide:
       * "contain" for wide shots (letterboxed), "portrait" for a tall crop (pillarboxed).
       */
      fit?: "contain" | "portrait";
      alt: string;
    }
  | { kind: "card"; alt: string; feel: FeelId }
  | { kind: "court"; alt: string };

function slidesFor(tier: TierId, feel: FeelId): Slide[] {
  switch (tier) {
    case "reserve":
      return [
        { kind: "still", id: "K01-full", phoneCrop: "card", alt: "A KINETIQ racket standing in a single beam of light" },
        { kind: "still", id: "K02", phoneCrop: "portrait", fit: "contain", alt: "The racket edge-on: one unbroken 38.0 mm carbon wall from handle to tip" },
        { kind: "still", id: "K04-full", phoneCrop: "card", alt: "Close-up of a moulded hole, the carbon weave flowing around its rim" },
        {
          kind: "still",
          id: "K08",
          // The chosen feel's racket alone (the pair's other racket would be cut by the frame).
          crop: feel === "command" ? "left" : "right",
          fit: "portrait",
          alt: feel === "command" ? "Command: a fine 3K carbon twill face" : "Pace: a wide 12K spread-tow carbon face",
        },
      ];
    case "limited":
      // The set first: two rackets of the chosen feel, both throats marked 027/500; then the mark up close.
      return [
        {
          kind: "still",
          id: `K11-${feel}`,
          phoneCrop: "card",
          alt: `A matched pair of KINETIQ ${feels[feel].name} rackets, both throats laser-marked 027/500`,
        },
        { kind: "still", id: "K10", phoneCrop: "card", alt: "Close-up of a throat laser-marked 027/500 above the KINETIQ wordmark" },
        { kind: "still", id: "K07", phoneCrop: "trio", fit: "contain", alt: "Identical KINETIQ rackets, each in its own shaft of light" },
        { kind: "still", id: "K06-full", phoneCrop: "card", alt: "The precision steel mould, its cavity glowing warm" },
        { kind: "still", id: "K03", phoneCrop: "card", alt: "The head cut through: one carbon shell closed around the core, lining every hole" },
        {
          kind: "card",
          feel,
          alt: `Two certificates of measurement for set 027 of 500, one for each ${feels[feel].name} racket, numbered A and B`,
        },
      ];
    case "invite":
      return [
        { kind: "still", id: "K09", phoneCrop: "card", alt: "Three KINETIQ rackets in a machined, felt-lined case" },
        { kind: "court", alt: "A plan of a padel court marking the exclusive coaching session" },
        { kind: "still", id: "K07", phoneCrop: "trio", fit: "contain", alt: "Identical KINETIQ rackets, each in its own shaft of light" },
        { kind: "still", id: "K01-finale", phoneCrop: "card", alt: "A KINETIQ racket in its beam, above a lit horizon" },
      ];
  }
}

const noSubscribe = () => () => {};

/** Tesla-style gallery: crossfading slides with prev and next, dots and a counter; swipe on phones. */
export function Gallery({ tierId, feel }: { tierId: TierId; feel: FeelId }) {
  const slides = slidesFor(tierId, feel);
  // The two measurement cards are about 160 KB of markup and sit on the last slide: they render after hydration, so
  // the server HTML (and the edition a link asked for) reaches the screen sooner.
  const hydrated = useSyncExternalStore(noSubscribe, () => true, () => false);
  const [index, setIndex] = useState(0);
  const track = useRef<HTMLDivElement>(null);
  const tier = tierById(tierId)!;
  const { motionOn } = useMotion();

  // A new edition starts from its first slide.
  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- reset on edition change
    setIndex(0);
    track.current?.scrollTo({ left: 0 });
  }, [tierId]);

  // Phones swipe with scroll-snap: follow the scroll to keep the dots in step. The track is keyed
  // by edition, so the listener moves to each new track.
  useEffect(() => {
    const el = track.current;
    if (!el) return;
    const onScroll = () => {
      if (getComputedStyle(el).overflowX !== "auto") return;
      setIndex(Math.round(el.scrollLeft / el.clientWidth));
    };
    el.addEventListener("scroll", onScroll, { passive: true });
    return () => el.removeEventListener("scroll", onScroll);
  }, [tierId]);

  // Keyboard steps and reduced motion jump; pointer steps glide.
  const go = (i: number, instant = false) => {
    const n = (i + slides.length) % slides.length;
    setIndex(n);
    const el = track.current;
    if (el && getComputedStyle(el).overflowX === "auto") {
      el.scrollTo({ left: n * el.clientWidth, behavior: motionOn && !instant ? "smooth" : "instant" });
    }
  };
  const onKey = (e: KeyboardEvent) => {
    if (e.key === "ArrowRight") go(index + 1, true);
    else if (e.key === "ArrowLeft") go(index - 1, true);
    else return;
    e.preventDefault();
  };

  return (
    <section
      className={styles.gallery}
      aria-roledescription="carousel"
      aria-label={`${tier.name} ${reserveCopy.galleryLabel}`}
      tabIndex={0}
      onKeyDown={onKey}
    >
      <div ref={track} key={tierId} className={styles.track} tabIndex={-1}>
        {slides.map((s, i) => (
          <div
            key={`${s.kind}-${"id" in s ? s.id : ""}-${i}`}
            className={styles.slide}
            data-active={i === index}
            data-fit={s.kind === "still" ? s.fit : undefined}
            role="group"
            aria-roledescription="slide"
            aria-label={`${i + 1} of ${slides.length}`}
            aria-hidden={i !== index}
            style={"position" in s && s.position ? ({ "--pos": s.position } as CSSProperties) : undefined}
          >
            {s.kind === "still" ? (
              <Still
                id={s.id}
                crop={s.crop}
                phoneCrop={s.phoneCrop}
                alt={s.alt}
                sizes="(max-width: 1023px) 100vw, 66vw"
                className={styles.slideStill}
                priority={i === 0}
              />
            ) : s.kind === "card" ? (
              <div className={`${styles.slideGraphic} ${styles.slideCard}`} role="img" aria-label={s.alt}>
                {/* The set's two cards, numbered to match: B rests behind A with only its header and set number
                    showing above it, both in the buyer's feel, under one soft shadow. */}
                {hydrated ? (
                  <div className={`${styles.cardFit} ${styles.cardPair}`}>
                    <MeasurementCard
                      className={styles.cardBack}
                      edition="Set No. 027 / 500 B"
                      feel={feels[s.feel].name}
                      second
                      peek
                      plate={false}
                      enter={false}
                    />
                    <MeasurementCard className={styles.cardFront} edition="Set No. 027 / 500 A" feel={feels[s.feel].name} plate={false} enter={false} />
                  </div>
                ) : null}
              </div>
            ) : (
              <div className={`${styles.slideGraphic} ${styles.slideCourt}`} role="img" aria-label={s.alt}>
                {/* The court stands up in the phone's 4:5 frame and lies across on wide screens. */}
                <CourtPlan active={i === index} field={false} aspect="4:5" className={styles.courtTall} />
                <CourtPlan active={i === index} field={false} aspect="16:10" className={styles.courtWide} />
              </div>
            )}
          </div>
        ))}
      </div>
      <div className={styles.controls}>
        <button type="button" className={styles.arrow} onClick={(e) => go(index - 1, e.detail === 0)} aria-label={reserveCopy.previousImage}>
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path d="M14.5 6 8.5 12l6 6" />
          </svg>
        </button>
        <div className={styles.dots} aria-hidden="true">
          {slides.map((_, i) => (
            <span key={i} data-active={i === index} />
          ))}
        </div>
        <p className={styles.counter} aria-live="polite">
          {index + 1} / {slides.length}
        </p>
        <button type="button" className={styles.arrow} onClick={(e) => go(index + 1, e.detail === 0)} aria-label={reserveCopy.nextImage}>
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path d="m9.5 6 6 6-6 6" />
          </svg>
        </button>
      </div>
    </section>
  );
}
