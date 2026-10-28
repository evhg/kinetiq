"use client";

import { useRef } from "react";
import { Still } from "@/components/media/Still";
import { Swivel, hasSequence, type SwivelHandle } from "@/components/media/Swivel";
import { useMotion } from "@/components/motion/MotionProvider";
import { PinnedChapter } from "@/components/motion/PinnedChapter";
import { GluedSection, KinetiqSection, buildSectionTimeline } from "@/components/graphics/SectionComparison";
import { unibody } from "@/content/copy";
import { gsap, useGSAP } from "@/lib/gsap";
import styles from "./Unibody.module.css";

const { edge, section } = unibody;

/**
 * K02's swivel (Release 4, 2026-10-28): the edge-on racket turns about its handle until its face shows (K02-swivel,
 * 0 to 35 degrees, Command and Pace), drawn by the shared Swivel over the still. It plays where K02 is shown whole:
 * phones (the upright portrait master, `PHONE`, the still's own phoneMedia) and the pinned stage (from 900 px). The
 * stacked tablet layout (700 to 899 px) crops K02 to its 18:5 band, which a turned racket would overflow: the still
 * stays there. Plain media queries, never range syntax (older iOS Safari cannot parse it).
 */
const SWIVEL = "K02-swivel";
const PHONE = "(max-width: 699px)";
const SWIVEL_MEDIA = "(max-width: 699px), (min-width: 900px)";
const TURNS = hasSequence(SWIVEL);

/**
 * Unibody, pinned on wide screens (1.6 screens): beat A is the edge-on racket, with what we left out and three
 * callouts beside the parts they name; beat B the cut-through head between a tubular section and the KINETIQ shell,
 * where the chapter ends. The sealed core, once its last beat, is its own chapter after Holes (SealedCore.tsx; owner,
 * 2026-10-23), and beat C (three proofs) is retired: its points are told by beat A, the sweet-spot section and Feel.
 * Since 2026-10-28 it opens the story, straight after the hero, and its Skip link lands on Space-grade carbon.
 */
export function Unibody() {
  const beatA = useRef<HTMLDivElement>(null);
  const swivel = useRef<SwivelHandle>(null);
  const { motionOn } = useMotion();

  // Phones: not pinned. The racket turns as it crosses the screen, from its centre at 85% of the screen to 30%.
  useGSAP(
    () => {
      if (!motionOn || !TURNS) return;
      const mm = gsap.matchMedia();
      mm.add({ phone: PHONE, motion: "(prefers-reduced-motion: no-preference)" }, (ctx) => {
        const { phone, motion } = ctx.conditions as { phone: boolean; motion: boolean };
        if (!phone || !motion) return;
        const state = { p: 0 };
        gsap.to(state, {
          p: 1,
          ease: "none",
          scrollTrigger: { trigger: `.${styles.still}`, start: "center 85%", end: "center 30%", scrub: 0.4 },
          onUpdate: () => swivel.current?.progress(state.p),
        });
        return () => swivel.current?.progress(0);
      });
      return () => mm.revert();
    },
    { scope: beatA, dependencies: [motionOn], revertOnUpdate: true },
  );

  return (
    <PinnedChapter
      id="unibody"
      nextId="space-grade"
      labelledBy="unibody-title"
      className={`pin-layered ${styles.chapter}`}
      length={1.6}
      build={(tl) => {
        // fromTo with explicit start values throughout: a scrubbed .from() can record its end state late
        // (after a refresh) and blink. A staggered fromTo only renders its first target immediately, so
        // the staggered groups are also set to their start state up front: nothing shows before its reveal.
        const show = { autoAlpha: 1, y: 0, immediateRender: true } as const;
        gsap.set(`.${styles.beatA} .${styles.callout}`, { autoAlpha: 0, y: 12 });
        gsap.set(`.${styles.side}`, { autoAlpha: 0, y: 16 });
        // Beat A holds whole for about 0.16 of the timeline once the callouts are in (about 230 px of scroll on a 900 px
        // screen): the light line runs from the handle to the rim at once, and the callouts follow it in a quick
        // stagger. Then the words, the callouts and the light line step aside (they name the edge-on parts, and the
        // turned face rises behind the headline on short windows such as 1536 x 730) and the racket turns about its
        // handle alone until its face shows (K02's swivel, 0.42 to 0.60). Without a sequence the beat holds whole.
        const turn = { p: 0 };
        if (TURNS) {
          tl.to([`.${styles.beatA} .${styles.copy}`, `.${styles.callouts}`, `.${styles.edgeLight}`], { autoAlpha: 0, duration: 0.05 }, 0.4).fromTo(
            turn,
            { p: 0 },
            { p: 1, duration: 0.18, immediateRender: true, onUpdate: () => swivel.current?.progress(turn.p) },
            0.42,
          );
        }
        tl.fromTo(`.${styles.edgeLight}`, { scaleX: 0 }, { scaleX: 1, duration: 0.22, immediateRender: true }, 0.02)
          // The callouts follow the light line from the handle to the rim (the reverse of their reading order).
          .fromTo(
            `.${styles.beatA} .${styles.callout}`,
            { autoAlpha: 0, y: 12 },
            { ...show, stagger: { each: 0.02, from: "end" }, duration: 0.08 },
            0.12,
          )
          // Beat A leaves completely before beat B arrives: the two products never share the frame
          // (above 10% opacity), and K02 drifts up as it goes (30% of its band, about 6% of the screen).
          .to(`.${styles.beatA} .${styles.copy}`, { autoAlpha: 0, duration: 0.06 }, 0.62)
          .to(`.${styles.beatA} .${styles.media}`, { yPercent: -30, duration: 0.1 }, 0.62)
          .to(`.${styles.beatA}`, { autoAlpha: 0, duration: 0.1 }, 0.62)
          .fromTo(`.${styles.beatB}`, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.1, immediateRender: true }, 0.72)
          .fromTo(`.${styles.beatB} .${styles.copy}`, { autoAlpha: 0, y: 16 }, { ...show, duration: 0.08 }, 0.78)
          .fromTo(`.${styles.side}`, { autoAlpha: 0, y: 16 }, { ...show, stagger: 0.04, duration: 0.08 }, 0.78);
        // G07, once K03 is fully in: the tubular parts drift apart at their bond lines while the KINETIQ
        // shell draws in one stroke.
        buildSectionTimeline(tl, `.${styles.compare}`, { at: 0.86, duration: 0.2 });
        tl
          // The conventional tubular cut dissolves into the KINETIQ shell (both stills share one camera).
          .fromTo(`.${styles.tubular}`, { autoAlpha: 1 }, { autoAlpha: 0, duration: 0.1, immediateRender: true }, 0.98)
          // Beat B is the last beat: it holds while the stage is still pinned, then scrolls away into Feel.
          .to({}, { duration: 0.22 });
        return () => swivel.current?.progress(0);
      }}
    >
      <div ref={beatA} className={`beat ${styles.beatA}`}>
        {/* Phones: the eyebrow and headline, K02 standing upright, then the lead and the callouts. From 700 px the
            words come first and K02 lies across the screen with each callout under the part it names; pinned, the
            whole block (words, racket, callouts) is centred in the stage. */}
        <div className={`${styles.copy} ${styles.headA}`}>
          <p className="t-eyebrow">{edge.eyebrow}</p>
          <h2 id="unibody-title" className={`t-h2 ${styles.title}`}>
            {edge.headline}
          </h2>
        </div>
        <div className={styles.media} aria-hidden="true">
          {/* The still and, over it, its swivel's canvas (frame 0 is this still), in one box the still fills. */}
          <div className={styles.still}>
            <Still id="K02" phoneCrop="portrait" alt="" sizes="100vw" className={styles.picture} />
            <Swivel ref={swivel} sequence={SWIVEL} portraitQuery={PHONE} media={SWIVEL_MEDIA} lead={1} className={styles.swivel} />
          </div>
          <span className={styles.edgeLight} />
        </div>
        <div className={`${styles.copy} ${styles.ledeA}`}>
          <p className="t-lead">{edge.body}</p>
        </div>
        {/* Rim, bridge and handle: top to bottom on phones (K02 stands upright), beside each part on wide screens. */}
        <ul className={styles.callouts}>
          {edge.callouts.map((c) => (
            <li key={c.at} className={`t-label ${styles.callout} ${styles[c.at]}`}>
              {c.text}
            </li>
          ))}
        </ul>
      </div>

      <div className={`beat ${styles.beatB}`}>
        <div className={styles.media} aria-hidden="true">
          <Still id="K03" crop="wide" phoneCrop="card" alt="" sizes="100vw" className={styles.still} />
          <Still id="K03b-tubular" alt="" sizes="100vw" className={`${styles.still} ${styles.tubular}`} />
        </div>
        <div className={styles.copy}>
          <p className="t-eyebrow">{section.eyebrow}</p>
          <h3 className={`t-h2 ${styles.title}`}>{section.headline}</h3>
          <p className="t-lead">{section.body}</p>
        </div>
        <div className={styles.compare}>
          <div className={styles.side}>
            <GluedSection />
          </div>
          <div className={styles.side}>
            <KinetiqSection />
          </div>
        </div>
      </div>

    </PinnedChapter>
  );
}
