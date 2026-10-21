"use client";

import { useEffect, useRef, useState, type CSSProperties, type KeyboardEvent } from "react";
import { CourtPlan } from "@/components/graphics/CourtPlan";
import { MeasurementCard } from "@/components/graphics/MeasurementCard";
import { Still } from "@/components/media/Still";
import { tierById, type TierId } from "@/content/lineup";
import { reserveCopy } from "@/content/reserve";
import type { FeelId } from "@/content/site";
import styles from "./Reserve.module.css";

type Slide =
  | { kind: "still"; id: string; crop?: string; phoneCrop?: string; position?: string; alt: string }
  | { kind: "card"; alt: string }
  | { kind: "court"; alt: string };

function slidesFor(tier: TierId, feel: FeelId): Slide[] {
  switch (tier) {
    case "reserve":
      return [
        { kind: "still", id: "K01-full", phoneCrop: "card", alt: "A KINETIQ racket standing in a single beam of light" },
        { kind: "still", id: "K02", alt: "The racket edge-on: one unbroken 38.0 mm carbon wall from handle to tip" },
        { kind: "still", id: "K04-full", phoneCrop: "card", alt: "Close-up of a moulded hole, the carbon weave flowing around its rim" },
        {
          kind: "still",
          id: "K08",
          position: feel === "command" ? "24% 50%" : "76% 50%",
          phoneCrop: feel === "command" ? "left" : "right",
          alt: feel === "command" ? "Command: a fine 3K carbon twill face" : "Pace: a wide 12K spread-tow carbon face",
        },
      ];
    case "limited":
      return [
        { kind: "still", id: "K06-full", phoneCrop: "card", alt: "The precision steel mould, its cavity glowing warm" },
        { kind: "still", id: "K07", alt: "Five identical KINETIQ rackets, each in its own shaft of light" },
        { kind: "still", id: "K03", phoneCrop: "card", alt: "The head cut through: one continuous carbon shell around the core" },
        { kind: "card", alt: "A numbered certificate of measurement, Edition No. 017 of 500" },
      ];
    case "invite":
      return [
        { kind: "still", id: "K09", phoneCrop: "card", alt: "Three KINETIQ rackets in a machined, felt-lined case" },
        { kind: "court", alt: "A plan of a padel court marking the one-on-one session" },
        { kind: "still", id: "K07", alt: "Five identical KINETIQ rackets, each in its own shaft of light" },
        { kind: "still", id: "K01-finale", phoneCrop: "card", alt: "A KINETIQ racket in its beam, above a lit horizon" },
      ];
  }
}

/** Tesla-style gallery: crossfading slides with prev and next, dots and a counter; swipe on phones. */
export function Gallery({ tierId, feel }: { tierId: TierId; feel: FeelId }) {
  const slides = slidesFor(tierId, feel);
  const [index, setIndex] = useState(0);
  const track = useRef<HTMLDivElement>(null);
  const tier = tierById(tierId)!;

  // A new edition starts from its first slide.
  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect -- reset on edition change
    setIndex(0);
    track.current?.scrollTo({ left: 0 });
  }, [tierId]);

  // Phones swipe with scroll-snap: follow the scroll to keep the dots in step.
  useEffect(() => {
    const el = track.current;
    if (!el) return;
    const onScroll = () => {
      if (getComputedStyle(el).overflowX !== "auto") return;
      setIndex(Math.round(el.scrollLeft / el.clientWidth));
    };
    el.addEventListener("scroll", onScroll, { passive: true });
    return () => el.removeEventListener("scroll", onScroll);
  }, []);

  const go = (i: number) => {
    const n = (i + slides.length) % slides.length;
    setIndex(n);
    const el = track.current;
    if (el && getComputedStyle(el).overflowX === "auto") el.scrollTo({ left: n * el.clientWidth, behavior: "smooth" });
  };
  const onKey = (e: KeyboardEvent) => {
    if (e.key === "ArrowRight") go(index + 1);
    else if (e.key === "ArrowLeft") go(index - 1);
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
      <div ref={track} key={tierId} className={styles.track}>
        {slides.map((s, i) => (
          <div
            key={`${s.kind}-${"id" in s ? s.id : ""}-${i}`}
            className={styles.slide}
            data-active={i === index}
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
              <div className={styles.slideGraphic} role="img" aria-label={s.alt}>
                <MeasurementCard edition="Edition No. 017 / 500" />
              </div>
            ) : (
              <div className={styles.slideGraphic} role="img" aria-label={s.alt}>
                <CourtPlan />
              </div>
            )}
          </div>
        ))}
      </div>
      <div className={styles.controls}>
        <button type="button" className={styles.arrow} onClick={() => go(index - 1)} aria-label="Previous image">
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
        <button type="button" className={styles.arrow} onClick={() => go(index + 1)} aria-label="Next image">
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path d="m9.5 6 6 6-6 6" />
          </svg>
        </button>
      </div>
    </section>
  );
}
