"use client";

import { Still } from "@/components/media/Still";
import { PinnedChapter } from "@/components/motion/PinnedChapter";
import { GluedSection, KinetiqSection, buildSectionTimeline } from "@/components/graphics/SectionComparison";
import { onePiece } from "@/content/copy";
import { gsap } from "@/lib/gsap";
import styles from "./OnePiece.module.css";

const { edge, section } = onePiece;

/**
 * One piece, pinned on wide screens: beat A is the edge-on racket (one unbroken wall), beat B the
 * cut-through head between a tubular section and the KINETIQ shell, beat C the three proofs over the shell.
 */
export function OnePiece() {
  return (
    <PinnedChapter
      id="one-piece"
      nextId="born-whole"
      labelledBy="one-piece-title"
      className={`pin-layered ${styles.chapter}`}
      length={2}
      build={(tl) => {
        // fromTo with explicit start values throughout: a scrubbed .from() can record its end state late
        // (after a refresh) and blink. A staggered fromTo only renders its first target immediately, so
        // the staggered groups are also set to their start state up front: nothing shows before its reveal.
        const show = { autoAlpha: 1, y: 0, immediateRender: true } as const;
        gsap.set(`.${styles.callout}`, { autoAlpha: 0, y: 12 });
        gsap.set(`.${styles.side}`, { autoAlpha: 0, y: 16 });
        gsap.set(`.${styles.proof}`, { autoAlpha: 0, y: 12 });
        tl.fromTo(`.${styles.edgeLight}`, { scaleX: 0 }, { scaleX: 1, duration: 0.35, immediateRender: true }, 0.1)
          .fromTo(`.${styles.callout}`, { autoAlpha: 0, y: 12 }, { ...show, stagger: 0.03, duration: 0.1 }, 0.3)
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
          // Beat C: the words and drawings leave the shell before the proofs arrive (no overlapping fades).
          .to(`.${styles.beatB} .${styles.copy}, .${styles.compare}`, { autoAlpha: 0, duration: 0.08 }, 1.12)
          .to(`.${styles.beatB} .${styles.media}`, { yPercent: 0, y: 0, scale: 1, duration: 0.12, ease: "power2.inOut" }, 1.12)
          .fromTo(`.${styles.beatC}`, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.02, immediateRender: true }, 1.2)
          .fromTo(`.${styles.proof}`, { autoAlpha: 0, y: 12 }, { ...show, stagger: 0.03, duration: 0.08 }, 1.22)
          .to({}, { duration: 0.12 });
      }}
    >
      <div className={`beat ${styles.beatA}`}>
        <div className={styles.media} aria-hidden="true">
          <Still id="K02" phoneCrop="portrait" alt="" sizes="100vw" className={styles.still} />
          <span className={styles.edgeLight} />
        </div>
        <div className={styles.copy}>
          <h2 id="one-piece-title" className="t-h2">
            {edge.headline}
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
        </div>
        <div className={styles.copy}>
          <p className="t-eyebrow">{section.eyebrow}</p>
          <h3 className="t-h2">{section.headline}</h3>
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
