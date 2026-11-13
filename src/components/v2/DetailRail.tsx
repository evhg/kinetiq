"use client";

import { Still } from "@/components/media/Still";
import { bornWhole, surface, unibody } from "@/content/copy";
import { v2 } from "@/content/v2";
import { gsap } from "@/lib/gsap";
import { V2Chapter } from "./V2Chapter";
import styles from "./DetailRail.module.css";

/**
 * Effect 7, sideways: "Take a closer look", Apple's gallery of details. Five close-ups the page already shows, each with
 * a line the page already says (or, for the throat, what the image shows), so the rail adds no claim. From 900 px the
 * chapter is pinned and scrolling down moves the row sideways, one card after another across the screen; below 900 px
 * it is a row the visitor swipes (scroll snap), with the keyboard reaching it too. Reduced motion: the swipeable row.
 */
const CARDS = [
  { label: "The edge", text: unibody.edge.callouts[0].text, still: { id: "K14", crop: "card" } },
  { label: "The surface", text: surface.headline, still: { id: "K17-full", crop: "phone" } },
  { label: "The profile", text: "The face, the bridge, and the handle are one single integrated carbon unit.", still: { id: "K02", crop: "portrait" } },
  { label: "The throat", text: "Its own number, laser-marked on the throat.", still: { id: "K10", crop: "card" } },
  { label: "The mould", text: `${bornWhole.headline}`, still: { id: "K06-full", crop: "card" } },
];

export function DetailRail() {
  const d = v2.rail;
  return (
    <V2Chapter
      id={d.id}
      nextId="v2-identical"
      labelledBy={`${d.id}-title`}
      length={2.4}
      className={styles.chapter}
      build={(tl, mode) => {
        if (mode !== "pin") return;
        const track = document.querySelector<HTMLElement>(`.${styles.track}`);
        const viewport = document.querySelector<HTMLElement>(`.${styles.viewport}`);
        if (!track || !viewport) return;
        // The row travels by its overflow: from its first card at the left margin to its last at the right.
        const travel = () => -Math.max(0, track.scrollWidth - viewport.clientWidth);
        tl.fromTo(track, { x: 0 }, { x: travel, duration: 0.9, immediateRender: true }, 0.05).to({}, { duration: 0.08 });
        return () => gsap.set(track, { clearProps: "transform" });
      }}
    >
      <div className={styles.stage}>
        <div className={styles.head}>
          <p className="t-eyebrow">{d.eyebrow}</p>
          <h2 id={`${d.id}-title`} className="t-h2">
            {d.headline}
          </h2>
          <p className={`t-label ${styles.hint}`} aria-hidden="true">
            {d.hint}
          </p>
        </div>
        {/* Below the pin the viewport scrolls sideways (the keyboard reaches it: tabIndex and a label). */}
        <div className={styles.viewport} tabIndex={0} role="region" aria-label={d.headline}>
          <ul className={styles.track}>
            {CARDS.map((c) => (
              <li key={c.label} className={styles.card}>
                <div className={styles.media} aria-hidden="true">
                  <Still id={c.still.id} crop={c.still.crop} alt="" sizes="(min-width: 900px) 30vw, 78vw" className={styles.still} />
                </div>
                <p className={styles.label}>{c.label}</p>
                <p className={styles.text}>{c.text}</p>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </V2Chapter>
  );
}
