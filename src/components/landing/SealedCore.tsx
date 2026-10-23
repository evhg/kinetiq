"use client";

import { SealedCoreTrace } from "@/components/graphics/SealedCoreTrace";
import { Still } from "@/components/media/Still";
import { PinnedChapter } from "@/components/motion/PinnedChapter";
import { sealedCore } from "@/content/copy";
import { gsap } from "@/lib/gsap";
import styles from "./SealedCore.module.css";

/**
 * The sealed core, its own pinned chapter right after Holes (owner, 2026-10-23: the core never touching the air
 * follows from the 42 moulded, lined holes). Pinned, the words take the left columns and the K03 cut-through stands on
 * the right, where Unibody's beat B left it; the scrub settles the frame, lists the three callouts and draws the
 * shell's amber line around the core once, then holds. The heading and the image are on screen from the first frame,
 * so the chapter never enters blank. Stacked (phones, reduced motion, below 900 px): the words, the callouts, then
 * K03, with the trace drawn from 700 px, where the frame is the 16:9 crop the trace is drawn on.
 */
export function SealedCore() {
  return (
    <PinnedChapter
      id="sealed-core"
      nextId="durability"
      labelledBy="sealed-core-title"
      className={`pin-layered ${styles.chapter}`}
      length={1}
      build={(tl) => {
        const show = { autoAlpha: 1, y: 0, immediateRender: true } as const;
        gsap.set(`.${styles.callout}`, { autoAlpha: 0, y: 12 });
        gsap.set(`.${styles.trace}`, { autoAlpha: 0 });
        gsap.set(`.${styles.trace} [data-seal-line]`, { strokeDasharray: 1, strokeDashoffset: 1 });
        tl.fromTo(`.${styles.frame}`, { scale: 1.06 }, { scale: 1, duration: 0.5, ease: "power2.out", immediateRender: true }, 0)
          .fromTo(`.${styles.callout}`, { autoAlpha: 0, y: 12 }, { ...show, stagger: 0.05, duration: 0.1 }, 0.12)
          // The proof on the still: the shell's line draws once around the core, and the bores light up lined.
          .fromTo(`.${styles.trace}`, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.05, immediateRender: true }, 0.24)
          .fromTo(
            `.${styles.trace} [data-seal-line]`,
            { strokeDashoffset: 1 },
            { strokeDashoffset: 0, duration: 0.3, immediateRender: true },
            0.24,
          )
          // It holds while the stage is still pinned, then scrolls away into Durability.
          .to({}, { duration: 0.36 });
      }}
    >
      <div className={`beat ${styles.beat}`}>
        <div className={styles.copy}>
          <p className="t-eyebrow">{sealedCore.eyebrow}</p>
          <h2 id="sealed-core-title" className={`t-h2 ${styles.title}`}>
            {sealedCore.headline}
          </h2>
          <p className="t-lead">{sealedCore.body}</p>
          <ul className={styles.callouts}>
            {sealedCore.callouts.map((c) => (
              <li key={c} className={`t-label ${styles.callout}`}>
                {c}
              </li>
            ))}
          </ul>
        </div>
        <div className={styles.media} aria-hidden="true">
          <div className={styles.frame}>
            <Still id="K03" crop="wide" phoneCrop="card" alt="" sizes="100vw" className={styles.still} />
            <SealedCoreTrace className={styles.trace} />
          </div>
        </div>
      </div>
    </PinnedChapter>
  );
}
