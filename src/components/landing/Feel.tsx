"use client";

import { VibrationGraph } from "@/components/graphics/VibrationGraph";
import { PinnedChapter } from "@/components/motion/PinnedChapter";
import { feel } from "@/content/copy";
import { gsap } from "@/lib/gsap";
import { Reveal } from "./Reveal";
import styles from "./Feel.module.css";

/** Below the pin (phones, tablets) the three points rise on entry; pinned, the chapter's scrub lists them. */
const POINTS_REVEAL = "(max-width: 899px) and (prefers-reduced-motion: no-preference)";

/**
 * Feel, the payoff's second beat (owner, 2026-10-28: a climactic rise), after the sweet spot and before the five
 * years. Pinned from 900 px like the chapters above it (owner, 2026-10-23), with its own eyebrow and Skip link (it
 * lands on Durability): the headline, the vibration graph and the three points share one screen, the graph draws once
 * as the chapter arrives, the points follow in the scrub, and the screen holds. Phones and reduced motion stack it, every part visible.
 */
export function Feel() {
  return (
    <PinnedChapter
      id="feel"
      nextId="durability"
      labelledBy="feel-title"
      className={styles.chapter}
      length={0.8}
      build={(tl) => {
        const show = { autoAlpha: 1, y: 0, immediateRender: true } as const;
        gsap.set(`.${styles.point}`, { autoAlpha: 0, y: 16 });
        tl.fromTo(`.${styles.point}`, { autoAlpha: 0, y: 16 }, { ...show, stagger: 0.08, duration: 0.16 }, 0.04).to({}, { duration: 0.6 });
      }}
    >
      <div className={`lift ${styles.section}`}>
        <Reveal className={styles.head}>
          <div className={styles.title}>
            <p className="t-eyebrow">{feel.eyebrow}</p>
            <h2 id="feel-title" className="t-h2">
              {feel.headline}
            </h2>
          </div>
          <p className="t-lead">{feel.body}</p>
        </Reveal>
        <div className={styles.graph}>
          <VibrationGraph className={styles.figure} fill />
        </div>
        <Reveal as="ul" className={`pool ${styles.points}`} media={POINTS_REVEAL}>
          {feel.points.map((p) => (
            <li key={p.title} className={styles.point}>
              <h3 className="t-h3">{p.title}</h3>
              <p className="t-body">{p.body}</p>
            </li>
          ))}
        </Reveal>
      </div>
    </PinnedChapter>
  );
}
