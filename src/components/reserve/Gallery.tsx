"use client";

import { useEffect, useLayoutEffect, useRef, useState, useSyncExternalStore, type CSSProperties, type KeyboardEvent } from "react";
import { CourtPlan } from "@/components/graphics/CourtPlan";
import { MeasurementCard } from "@/components/graphics/MeasurementCard";
import { Still, hasStill } from "@/components/media/Still";
import { useMotion } from "@/components/motion/MotionProvider";
import { identical } from "@/content/copy";
import { ambassador, sampleSet, tierById, type TierId } from "@/content/lineup";
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
       * "contain" for wide shots (letterboxed), "portrait" for a tall crop (pillarboxed). Below 1024 px a "contain"
       * slide without a phoneFit shows its square phone crop (K07's trio) whole, across the frame's width.
       */
      fit?: "contain" | "portrait";
      /**
       * Below 1024 px: the phone crop is taller than the frame (K02 edge-on), so it is contained, never cropped. It
       * fills the frame's height and its sides feather into the slide.
       */
      phoneFit?: "portrait";
      /** The racket in the buyer's feel (K08's crop, K11's set): the slide a change of feel shows. */
      feel?: FeelId;
      /** K08 whole: Command and Pace together, the first slide until the buyer chooses a feel. */
      both?: boolean;
      /** A separate still for phones and tablets (the stacked layout), e.g. K07's trio, which fits a 4:5 frame. */
      phoneId?: string;
      alt: string;
    }
  | {
      /**
       * K12's base render alone: its lit pass is shown nowhere (the landing dropped K12 on 2026-10-28), so the checkout never shows it. One crop at every size, contained and centred (Reserve.module.css .reveal).
       */
      kind: "reveal";
      base: string;
      crop: string;
      alt: string;
    }
  /**
   * The measurement card: one for a single racket (its own serial; Pace's is identical.card.second's, the racket K08
   * shows), or a set's two, numbered A and B.
   */
  | { kind: "card"; alt: string; feel: FeelId; set: boolean }
  | { kind: "court"; alt: string };

/**
 * K12's base pass (a face-on Command racket, white 3K twill, with its own serial on the throat), uncaptioned: the lit
 * pass, an illustration of the sweet spot, is shown nowhere (the landing dropped K12 on 2026-10-28), so at the
 * payment the racket always looks as the feel picker says. Only once it is exported, and only for a single Command
 * racket, as the render shows one. A set's throats carry its set number instead, and Pace is black 12K. Its 4:5
 * portrait crop at every size, so the whole racket shows, from the crown to the engraved cap, clear of the controls.
 */
/**
 * Where the gallery stacks above the options at the screen's full width (Reserve.module.css): below 1024 px, and any
 * portrait window (the 12.9-inch iPad Pro at 1024 x 1366), as the Hero treats it. Side by side it is about 66vw.
 */
const STACKED = "(max-width: 1023px), (max-aspect-ratio: 4/5)";
const SIZES = "(max-width: 1023px) 100vw, (max-aspect-ratio: 4/5) 100vw, 66vw";

const SWEET_SPOT: Slide | null = hasStill("K12-base", "portrait")
  ? { kind: "reveal", base: "K12-base", crop: "portrait", alt: "A white KINETIQ Command racket face-on" }
  : null;

/**
 * Until the buyer chooses a feel, every edition's gallery opens on the two feels together (owner, 2026-10-23): K08's
 * wide render, Command's white 3K face beside Pace's black 12K, kept whole. Once a feel is chosen it gives way, and the
 * gallery shows that feel's renders where they exist (K08's half, K11's set, and any still with a Pace version, through
 * Still's `feel`) and the Command renders otherwise.
 */
const BOTH_FEELS: Slide = {
  kind: "still",
  id: "K08",
  both: true,
  fit: "contain",
  // Stacked (phones, tablets): K08's 16:9 frame would sit small in the 4:5 track, so K07's square trio (Pace, Command,
  // Pace) shows both feels instead.
  phoneId: "K07",
  phoneCrop: "trio",
  alt: "Command and Pace together: white 3K carbon twill faces beside black 12K spread-tow faces",
};

function slidesFor(tier: TierId, feel: FeelId, chosen: boolean): Slide[] {
  const slides = feelSlides(tier, feel);
  return chosen ? slides : [BOTH_FEELS, ...slides];
}

function feelSlides(tier: TierId, feel: FeelId): Slide[] {
  const name = tierById(tier)!.name;
  const feelName = feels[feel].name;
  switch (tier) {
    case "reserve": {
      // The chosen feel's racket alone (the pair's other racket would be cut by the frame). The other stills show
      // white Command, the canon's default, so a Pace buyer sees their racket first.
      const face: Slide = {
        kind: "still",
        id: "K08",
        feel,
        crop: feel === "command" ? "left" : "right",
        fit: "portrait",
        // phones and tablets: the racket stays whole and centred in a frame shorter than the crop (4:5 to square)
        position: "50% 25%",
        alt: feel === "command" ? "Command: a white 3K carbon twill face, the finer weave" : "Pace: a black 12K spread-tow carbon face, the bolder weave",
      };
      const shots: Slide[] = [
        { kind: "still", id: "K01-full", phoneCrop: "card", alt: "A KINETIQ racket standing in a single beam of light" },
        ...(feel === "command" && SWEET_SPOT ? [SWEET_SPOT] : []),
        { kind: "still", id: "K02", phoneCrop: "portrait", fit: "contain", phoneFit: "portrait", alt: "The racket edge-on: one carbon shell from the tip into the handle" },
        { kind: "still", id: "K04-full", phoneCrop: "card", alt: "Close-up of a moulded hole, the carbon weave flowing around its rim" },
      ];
      const card: Slide = {
        kind: "card",
        feel,
        set: false,
        alt: `The measurement card for a ${feelName} racket, serial ${feel === "pace" ? identical.card.second.serial : identical.card.serial}: its measured weight, balance, thickness and surface deviation, and a flatness map of the head`,
      };
      return feel === "pace" ? [face, ...shots, card] : [...shots, face, card];
    }
    case "limited":
      // The set first, in the chosen feel, with its set number on both throats; then the mark up close (K10, whose
      // Pace export the gallery's feel picks).
      return [
        {
          kind: "still",
          id: `K11-${feel}`,
          feel,
          phoneCrop: "card",
          // phones and tablets: both crowns stay in a frame shorter than the crop (4:5 to square)
          position: "50% 30%",
          alt: `A ${name} set: two identical ${feelName} rackets, ${sampleSet.words}, the set number laser-marked on both throats`,
        },
        {
          kind: "still",
          id: "K10",
          phoneCrop: "card",
          alt: `Close-up of a ${name} throat, laser-marked ${sampleSet.mark} above the KINETIQ wordmark`,
        },
        { kind: "still", id: "K07", phoneCrop: "trio", fit: "contain", alt: "Identical KINETIQ rackets, each in its own shaft of light" },
        { kind: "still", id: "K06-full", phoneCrop: "card", alt: "The mould, its cavity glowing warm" },
        { kind: "still", id: "K03", phoneCrop: "card", alt: "The head cut through: one carbon shell closed around the core, lining every hole" },
        {
          kind: "card",
          feel,
          set: true,
          alt: `The set's two measurement cards, ${sampleSet.card("A")} and ${sampleSet.card("B")}, one for each ${feelName} racket`,
        },
      ];
    case "invite":
      return [
        {
          kind: "still",
          id: "K09",
          phoneCrop: "card",
          // phones and tablets: the open lid stays in a frame shorter than the crop (4:5 to square)
          position: "50% 27%",
          alt: `The three rackets of a ${name} set in their fitted case`,
        },
        {
          kind: "court",
          alt: `A plan of a padel court marking the exclusive coaching session${ambassador.named ? ` with ${ambassador.name}` : ""}`,
        },
        { kind: "still", id: "K07", phoneCrop: "trio", fit: "contain", alt: "Identical KINETIQ rackets, each in its own shaft of light" },
        { kind: "still", id: "K01-finale", phoneCrop: "card", alt: "A KINETIQ racket in its beam, above a lit horizon" },
      ];
  }
}

/** A slide's identity, the same in both feels: the chosen feel's racket (K08's crop, K11's set) is one slide. */
const slideKey = (s: Slide) =>
  s.kind === "still" ? (s.both ? "both" : s.feel ? "feel" : s.id) : s.kind === "reveal" ? s.base : s.kind;

/** Whether a slide changes with the feel: the chosen feel's racket, and the measurement card in that feel. */
const showsFeel = (s: Slide) => s.kind === "card" || (s.kind === "still" && Boolean(s.feel));

/**
 * The slide to show after a change of feel: the one on show if it changes with the feel (to compare the two), or
 * else the chosen feel's racket. An edition without one (One of Ten) stays on its slide.
 */
function keyAfterFeel(slides: Slide[], key: string | null): string | null {
  const current = slides.find((s) => slideKey(s) === key);
  if (current && showsFeel(current)) return key;
  const racket = slides.find((s) => s.kind === "still" && s.feel);
  return racket ? slideKey(racket) : key;
}

const noSubscribe = () => () => {};

/** Tesla-style gallery: crossfading slides with prev and next, dots and a counter; swipe on phones. */
export function Gallery({ tierId, feel, chosen }: { tierId: TierId; feel: FeelId; chosen: boolean }) {
  const slides = slidesFor(tierId, feel, chosen);
  // The two measurement cards are about 160 KB of markup and sit on the last slide: they render after hydration, so
  // the server HTML (and the edition a link asked for) reaches the screen sooner.
  const hydrated = useSyncExternalStore(noSubscribe, () => true, () => false);
  // The slide on show, by identity rather than position, as a change of feel changes the slides (K12 is Command's
  // alone, and Pace's racket leads): the index can never point past the end or at another picture. A new edition
  // starts from its first slide; a new feel shows its own racket (keyAfterFeel).
  // Choosing a feel (even Command, already on show) counts as a change of feel: the two-feel slide gives way.
  const shown = chosen ? feel : null;
  const [view, setView] = useState<{ tierId: TierId; feel: FeelId | null; key: string | null }>({ tierId, feel: shown, key: null });
  if (view.tierId !== tierId || view.feel !== shown) {
    setView({ tierId, feel: shown, key: view.tierId !== tierId ? null : keyAfterFeel(slides, view.key) });
  }
  const index = Math.max(0, slides.findIndex((s) => slideKey(s) === view.key));
  const track = useRef<HTMLDivElement>(null);
  const tier = tierById(tierId)!;
  const { motionOn } = useMotion();

  // A new edition starts from its first slide.
  useEffect(() => {
    track.current?.scrollTo({ left: 0 });
  }, [tierId]);

  // Phones: a change of feel moves the track to the slide on show at once (wide screens show only that slide).
  const trackFeel = useRef(shown);
  useLayoutEffect(() => {
    const el = track.current;
    if (!el || trackFeel.current === shown) return;
    trackFeel.current = shown;
    if (getComputedStyle(el).overflowX === "auto") el.scrollTo({ left: index * el.clientWidth, behavior: "instant" });
  }, [shown, index]);

  // Phones swipe with scroll-snap: follow the scroll to keep the dots in step. The track is keyed
  // by edition, so the listener moves to each new track; it reads the slide from the DOM, which always
  // holds the current feel's slides.
  useEffect(() => {
    const el = track.current;
    if (!el) return;
    const onScroll = () => {
      if (getComputedStyle(el).overflowX !== "auto") return;
      const key = (el.children[Math.round(el.scrollLeft / el.clientWidth)] as HTMLElement | undefined)?.dataset.key;
      // the same object while the slide is unchanged, so a swipe re-renders only when it reaches another slide
      if (key) setView((v) => (v.key === key ? v : { ...v, key }));
    };
    el.addEventListener("scroll", onScroll, { passive: true });
    return () => el.removeEventListener("scroll", onScroll);
  }, [tierId]);

  // Keyboard steps and reduced motion jump; pointer steps glide.
  const go = (i: number, instant = false) => {
    const n = (i + slides.length) % slides.length;
    setView((v) => ({ ...v, key: slideKey(slides[n]) }));
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
            key={s.kind === "still" && s.both ? "both" : "id" in s ? s.id : slideKey(s)}
            className={styles.slide}
            data-key={slideKey(s)}
            data-active={i === index}
            data-fit={s.kind === "still" ? s.fit : undefined}
            data-phone-fit={s.kind === "still" ? s.phoneFit : undefined}
            role="group"
            aria-roledescription="slide"
            aria-label={`${i + 1} of ${slides.length}`}
            aria-hidden={i !== index}
            style={"position" in s && s.position ? ({ "--pos": s.position } as CSSProperties) : undefined}
          >
            {s.kind === "still" ? (
              // Stacked (below 1024 px, or a portrait window), the frame is full width, 4:5 to square: the 4:5 crops.
              <Still
                id={s.id}
                crop={s.crop}
                phoneCrop={s.phoneCrop}
                phoneId={s.phoneId}
                phoneMedia={STACKED}
                alt={s.alt}
                sizes={SIZES}
                className={styles.slideStill}
                priority={i === 0}
                // A still with a Pace version (K01, K02) shows the checkout's feel, never the landing's toggle alone.
                feel={feel}
              />
            ) : s.kind === "reveal" ? (
              // K12's base render alone, contained and feathered (its lit pass is shown nowhere).
              <div className={styles.reveal}>
                <Still id={s.base} crop={s.crop} alt={s.alt} sizes={SIZES} className={styles.slideStill} />
              </div>
            ) : s.kind === "card" ? (
              <div className={`${styles.slideGraphic} ${styles.slideCard}`} role="img" aria-label={s.alt}>
                {/* A set's two cards, numbered to match: B rests behind A with only its header and set number showing
                    above it (phones: its set number alone, so A fits the frame whole), both in the buyer's feel, under
                    one soft shadow. A single racket's card carries its own serial (for Pace, the racket K08 shows). */}
                {hydrated ? (
                  s.set ? (
                    <div className={`${styles.cardFit} ${styles.cardPair}`}>
                      <MeasurementCard className={styles.cardBack} set="B" feel={feels[s.feel].name} peek plate={false} enter={false} dense />
                      <MeasurementCard className={styles.cardFront} set="A" feel={feels[s.feel].name} plate={false} enter={false} dense />
                    </div>
                  ) : (
                    <div className={`${styles.cardFit} ${styles.cardSingle}`}>
                      <MeasurementCard feel={feels[s.feel].name} second={s.feel === "pace"} plate={false} enter={false} />
                    </div>
                  )
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
