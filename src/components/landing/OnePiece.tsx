"use client";

import { Still } from "@/components/media/Still";
import { PinnedChapter } from "@/components/motion/PinnedChapter";
import { GluedSection, KinetiqSection, buildSectionTimeline } from "@/components/graphics/SectionComparison";
import { onePiece } from "@/content/copy";
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
      length={1.9}
      build={(tl) => {
        tl.from(`.${styles.edgeLight}`, { scaleX: 0, duration: 0.35 }, 0.1)
          .from(`.${styles.callout}`, { opacity: 0, y: 12, stagger: 0.03, duration: 0.1 }, 0.4)
          .to(`.${styles.beatA} .${styles.copy}`, { autoAlpha: 0, duration: 0.08 }, 0.5)
          .to(`.${styles.beatA}`, { autoAlpha: 0, duration: 0.12 }, 0.55)
          .fromTo(`.${styles.beatB}`, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.12 }, 0.55)
          .from(`.${styles.beatB} .${styles.copy}`, { autoAlpha: 0, y: 16, duration: 0.08 }, 0.62)
          .from(`.${styles.side}`, { autoAlpha: 0, y: 16, stagger: 0.04, duration: 0.08 }, 0.62);
        // G07: the tubular parts drift apart at their bond lines while the KINETIQ shell draws in one stroke.
        buildSectionTimeline(tl, `.${styles.compare}`, { at: 0.66, duration: 0.2 });
        tl
          // The conventional tubular cut dissolves into the KINETIQ shell (both stills share one camera).
          .fromTo(`.${styles.tubular}`, { autoAlpha: 1 }, { autoAlpha: 0, duration: 0.1 }, 0.78)
          // Beat C: the words and drawings leave the shell before the proofs arrive (no overlapping fades).
          .to(`.${styles.beatB} .${styles.copy}, .${styles.compare}`, { autoAlpha: 0, duration: 0.08 }, 1.0)
          .to(`.${styles.beatB} .${styles.media}`, { yPercent: 0, y: 0, scale: 1, duration: 0.12, ease: "power2.inOut" }, 1.0)
          .fromTo(`.${styles.beatC}`, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.02 }, 1.08)
          .from(`.${styles.proof}`, { autoAlpha: 0, y: 12, stagger: 0.03, duration: 0.08 }, 1.1)
          .to({}, { duration: 0.1 });
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
          <Still id="K03" crop="wide" phoneCrop="card" alt="" sizes="100vw" className={styles.still} />
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
        <ul className={styles.proofs}>
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
