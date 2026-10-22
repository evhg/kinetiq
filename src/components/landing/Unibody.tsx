"use client";

import { Fragment } from "react";
import { Still } from "@/components/media/Still";
import { PinnedChapter } from "@/components/motion/PinnedChapter";
import { SealedCoreTrace } from "@/components/graphics/SealedCoreTrace";
import { GluedSection, KinetiqSection, buildSectionTimeline } from "@/components/graphics/SectionComparison";
import { unibody } from "@/content/copy";
import { gsap } from "@/lib/gsap";
import styles from "./Unibody.module.css";

const { edge, section, sealed } = unibody;

/**
 * K03's lowest point (the slab's front edge and its contact shadow), in px below the centre of the 1280 x 720
 * "wide" crop. The still covers the stage (object-fit: cover, centred), so its scale is max(w / 1280, h / 720).
 */
const SLAB_BOTTOM = 232;

/**
 * Beat C's resting pose for the shell: full frame where the slab clears the three proofs along the foot of the
 * stage; on short windows (1440 x 900 and the like) smaller, and if that is not enough also lifted, so it never
 * runs under them. Re-read on every refresh (the timeline uses function values with invalidateOnRefresh).
 */
const MIN_BEAT_C_SCALE = 0.8;
function beatCPose(proofs: string) {
  const stage = document.querySelector<HTMLElement>("#unibody .pin-stage");
  const list = document.querySelector<HTMLElement>(`#unibody ${proofs}`);
  if (!stage || !list) return { scale: 1, yPercent: 0 };
  const h = stage.clientHeight;
  const s = Math.max(stage.clientWidth / 1280, h / 720);
  const top = list.getBoundingClientRect().top - stage.getBoundingClientRect().top;
  const room = top - 24 - h / 2;
  const scale = gsap.utils.clamp(MIN_BEAT_C_SCALE, 1, room / (SLAB_BOTTOM * s));
  const over = SLAB_BOTTOM * s * scale - room;
  return { scale, yPercent: over > 0 ? -(over / h) * 100 : 0 };
}

/**
 * A two-sentence headline, one sentence per line where each fits ("Zero seams." / "No joint to work loose.",
 * "No tube." / "The shell is the frame."), each wrapping evenly inside itself on phones.
 */
function Sentences({ text }: { text: string }) {
  return text.split(/(?<=\.) /).map((sentence, i) => (
    <Fragment key={i}>
      {i > 0 ? " " : null}
      <span className={styles.sentence}>{sentence}</span>
    </Fragment>
  ));
}

/**
 * Unibody, pinned on wide screens: beat A is the edge-on racket (one unbroken wall), beat B the
 * cut-through head between a tubular section and the KINETIQ shell, then the sealed core (words on the
 * left, the cut-through moved right so its lined holes and closed edge face them), then beat C, the three
 * proofs over the shell.
 */
export function Unibody() {
  return (
    <PinnedChapter
      id="unibody"
      nextId="born-whole"
      labelledBy="unibody-title"
      className={`pin-layered ${styles.chapter}`}
      length={2.5}
      build={(tl) => {
        // fromTo with explicit start values throughout: a scrubbed .from() can record its end state late
        // (after a refresh) and blink. A staggered fromTo only renders its first target immediately, so
        // the staggered groups are also set to their start state up front: nothing shows before its reveal.
        const show = { autoAlpha: 1, y: 0, immediateRender: true } as const;
        gsap.set(`.${styles.beatA} .${styles.callout}`, { autoAlpha: 0, y: 12 });
        gsap.set(`.${styles.side}`, { autoAlpha: 0, y: 16 });
        gsap.set(`.${styles.sealedCallout}`, { autoAlpha: 0, y: 12 });
        gsap.set(`.${styles.proof}`, { autoAlpha: 0, y: 12 });
        gsap.set(`.${styles.trace}`, { autoAlpha: 0 });
        gsap.set(`.${styles.trace} [data-seal-line]`, { strokeDasharray: 1, strokeDashoffset: 1 });
        tl.fromTo(`.${styles.edgeLight}`, { scaleX: 0 }, { scaleX: 1, duration: 0.35, immediateRender: true }, 0.1)
          .fromTo(`.${styles.beatA} .${styles.callout}`, { autoAlpha: 0, y: 12 }, { ...show, stagger: 0.03, duration: 0.1 }, 0.3)
          // Beat A leaves completely before beat B arrives: the two products never share the frame
          // (above 10% opacity), and K02 drifts up as it goes.
          .to(`.${styles.beatA} .${styles.copy}`, { autoAlpha: 0, duration: 0.06 }, 0.56)
          .to(`.${styles.beatA} .${styles.media}`, { yPercent: -6, duration: 0.1 }, 0.56)
          .to(`.${styles.beatA}`, { autoAlpha: 0, duration: 0.1 }, 0.56)
          .fromTo(`.${styles.beatB}`, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.1, immediateRender: true }, 0.66)
          .fromTo(`.${styles.beatB} .${styles.copy}`, { autoAlpha: 0, y: 16 }, { ...show, duration: 0.08 }, 0.72)
          .fromTo(`.${styles.side}`, { autoAlpha: 0, y: 16 }, { ...show, stagger: 0.04, duration: 0.08 }, 0.72);
        // G07, once K03 is fully in: the tubular parts drift apart at their bond lines while the KINETIQ
        // shell draws in one stroke.
        buildSectionTimeline(tl, `.${styles.compare}`, { at: 0.8, duration: 0.2 });
        tl
          // The conventional tubular cut dissolves into the KINETIQ shell (both stills share one camera).
          .fromTo(`.${styles.tubular}`, { autoAlpha: 1 }, { autoAlpha: 0, duration: 0.1, immediateRender: true }, 0.92)
          // Sealed core: the words and drawings leave the shell first (no overlapping fades), then the cut-through
          // moves right and closer while the sealed-core words rise on the left.
          .to(`.${styles.beatB} .${styles.copy}, .${styles.compare}`, { autoAlpha: 0, duration: 0.08 }, 1.12)
          .to(
            `.${styles.beatB} .${styles.media}`,
            { xPercent: 19, yPercent: 4, y: 0, scale: 0.92, duration: 0.14, ease: "power2.inOut" },
            1.12,
          )
          .fromTo(`.${styles.beatS}`, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.02, immediateRender: true }, 1.2)
          .fromTo(`.${styles.beatS} .${styles.copy}`, { autoAlpha: 0, y: 16 }, { ...show, duration: 0.08 }, 1.22)
          .fromTo(`.${styles.sealedCallout}`, { autoAlpha: 0, y: 12 }, { ...show, stagger: 0.03, duration: 0.08 }, 1.3)
          // The proof on the still: the shell's line draws once around the core, and the bores light up lined.
          .fromTo(`.${styles.trace}`, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.04, immediateRender: true }, 1.28)
          .fromTo(
            `.${styles.trace} [data-seal-line]`,
            { strokeDashoffset: 1 },
            { strokeDashoffset: 0, duration: 0.14, immediateRender: true },
            1.28,
          )
          // Beat C, in sequence so the shell never crosses visible words: the sealed-core words and the trace
          // leave completely (1.54 to 1.60), then the shell moves back and grows to its beat C size (from 1.60),
          // then the proofs rise.
          .to(`.${styles.beatS}, .${styles.trace}`, { autoAlpha: 0, duration: 0.06 }, 1.54)
          .to(
            `.${styles.beatB} .${styles.media}`,
            {
              xPercent: 0,
              yPercent: () => beatCPose(`.${styles.proofs}`).yPercent,
              scale: () => beatCPose(`.${styles.proofs}`).scale,
              duration: 0.12,
              ease: "power2.inOut",
            },
            1.6,
          )
          .fromTo(`.${styles.beatC}`, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.02, immediateRender: true }, 1.7)
          .fromTo(`.${styles.proof}`, { autoAlpha: 0, y: 12 }, { ...show, stagger: 0.03, duration: 0.08 }, 1.72)
          .to({}, { duration: 0.12 });
      }}
    >
      <div className={`beat ${styles.beatA}`}>
        <div className={styles.media} aria-hidden="true">
          <Still id="K02" phoneCrop="portrait" alt="" sizes="100vw" className={styles.still} />
          <span className={styles.edgeLight} />
        </div>
        <div className={styles.copy}>
          <p className="t-eyebrow">{edge.eyebrow}</p>
          <h2 id="unibody-title" className={`t-h2 ${styles.title}`}>
            <Sentences text={edge.headline} />
          </h2>
          <p className="t-lead">{edge.body}</p>
        </div>
        <ul className={styles.callouts}>
          {edge.callouts.map((c) => (
            <li key={c} className={`t-label ${styles.callout}`}>
              {c}
            </li>
          ))}
        </ul>
      </div>

      <div className={`beat ${styles.beatB}`}>
        <div className={styles.media} aria-hidden="true">
          <Still id="K03" crop="wide" phoneCrop="slab" alt="" sizes="100vw" className={styles.still} />
          <Still id="K03b-tubular" alt="" sizes="100vw" className={`${styles.still} ${styles.tubular}`} />
          <SealedCoreTrace className={styles.trace} />
        </div>
        <div className={styles.copy}>
          <p className="t-eyebrow">{section.eyebrow}</p>
          <h3 className={`t-h2 ${styles.title}`}>
            <Sentences text={section.headline} />
          </h3>
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

      <div className={`beat ${styles.beatS}`}>
        <div className={`${styles.copy} ${styles.sealedCopy}`}>
          <p className="t-eyebrow">{sealed.eyebrow}</p>
          <h3 className={`t-h2 ${styles.title}`}>
            <Sentences text={sealed.headline} />
          </h3>
          <p className="t-lead">{sealed.body}</p>
          <ul className={styles.sealedCallouts}>
            {sealed.callouts.map((c) => (
              <li key={c} className={`t-label ${styles.callout} ${styles.sealedCallout}`}>
                {c}
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className={`beat ${styles.beatC}`}>
        <ul className={`pool ${styles.proofs}`}>
          {section.proofs.map((p) => (
            <li key={p.title} className={styles.proof}>
              <p className={`t-h3 ${styles.proofTitle}`}>{p.title}</p>
              <p className="t-body">{p.body}</p>
            </li>
          ))}
        </ul>
      </div>
    </PinnedChapter>
  );
}
