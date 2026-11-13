"use client";

import { Still } from "@/components/media/Still";
import { feelChoice } from "@/content/copy";
import { v2 } from "@/content/v2";
import { gsap } from "@/lib/gsap";
import { V2Chapter } from "./V2Chapter";
import styles from "./FeelWipe.module.css";

const PORTRAIT = "(max-aspect-ratio: 4/5)";

/**
 * Effect 4, the feel switch: one racket, two feels. K05 in Command and in Pace (one rig, one camera, so the two stills
 * register to the pixel) lie one over the other, and a line of light sweeps across: behind it the racket is Pace. Pinned
 * from 900 px; below, the sweep runs as the frame crosses the screen. Each feel's name and purpose sit on its own
 * side and brighten as their half takes the frame. Reduced motion: the line rests at the middle, half and half.
 */
export function FeelWipe() {
  const [command, pace] = feelChoice.feels;
  const d = v2.feelWipe;
  return (
    <V2Chapter
      id={d.id}
      nextId="v2-feels"
      labelledBy={`${d.id}-title`}
      length={1.6}
      className={styles.chapter}
      flow={`.${styles.frame}`}
      flowStart="top 75%"
      flowEnd="bottom 40%"
      build={(tl, mode) => {
        const t0 = mode === "pin" ? 0.1 : 0;
        // The line moves by transform only: its x is the cut's distance from the frame's left edge.
        const width = () => document.querySelector<HTMLElement>(`.${styles.frame}`)?.offsetWidth ?? 0;
        const span = mode === "pin" ? 0.7 : 1;
        // The sweep: the Pace layer's clip and the line move together (the line sits on the clip's edge). At rest (reduced
        // motion, server render) the line stands at 50%, where the clip cuts.
        gsap.set(`.${styles.line}`, { left: 0 });
        tl.fromTo(`.${styles.pace}`, { "--cut": "100%" }, { "--cut": "0%", duration: span, ease: "power1.inOut", immediateRender: true }, t0)
          .fromTo(
            `.${styles.line}`,
            { x: () => width() },
            { x: 0, duration: span, ease: "power1.inOut", immediateRender: true },
            t0,
          )
          .fromTo(`.${styles.labelCommand}`, { opacity: 1 }, { opacity: 0.35, duration: span * 0.5, immediateRender: true }, t0 + span * 0.5)
          .fromTo(`.${styles.labelPace}`, { opacity: 0.35 }, { opacity: 1, duration: span * 0.5, immediateRender: true }, t0 + span * 0.25);
        if (mode === "pin") {
          gsap.set(`.${styles.head}`, { autoAlpha: 0, y: 20 });
          tl.to(`.${styles.head}`, { autoAlpha: 1, y: 0, duration: 0.08 }, 0.01).to({}, { duration: 0.2 });
        }
      }}
    >
      <div className={styles.stage}>
        <div className={styles.head}>
          <p className="t-eyebrow">{d.eyebrow}</p>
          <h2 id={`${d.id}-title`} className="t-h2">
            {d.headline}
          </h2>
          <p className="visually-hidden">{d.alt}</p>
        </div>
        <div className={styles.frame} aria-hidden="true">
          <Still id="K05" phoneId="K05-phone" phoneCrop="portrait" phoneMedia={PORTRAIT} feel="command" alt="" sizes="100vw" className={styles.still} />
          <div className={styles.pace}>
            <Still id="K05" phoneId="K05-phone" phoneCrop="portrait" phoneMedia={PORTRAIT} feel="pace" alt="" sizes="100vw" className={styles.still} />
          </div>
          <span className={styles.line} />
        </div>
        <div className={styles.labels}>
          <p className={styles.labelCommand}>
            <span className={styles.name}>{command.name}</span>
            <span className={styles.sub}>
              {feelChoice.builtFor} {command.sub.toLowerCase()}
            </span>
          </p>
          <p className={styles.labelPace}>
            <span className={styles.name}>{pace.name}</span>
            <span className={styles.sub}>
              {feelChoice.builtFor} {pace.sub.toLowerCase()}
            </span>
          </p>
        </div>
      </div>
    </V2Chapter>
  );
}
