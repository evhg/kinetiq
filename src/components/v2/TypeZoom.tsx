"use client";

import { useRef, type CSSProperties } from "react";
import { Still } from "@/components/media/Still";
import stills from "@/content/stills.generated.json";
import { v2 } from "@/content/v2";
import { gsap } from "@/lib/gsap";
import { useFeel } from "@/lib/feel-store";
import { V2Chapter } from "./V2Chapter";
import styles from "./TypeZoom.module.css";

type Size = { widths: number[]; hash?: string };
const sizes = stills as Record<string, Size>;

/** A still's file at about `want` px wide (WebP: every browser that clips a background to text decodes it). */
function stillUrl(key: string, want: number) {
  const s = sizes[key];
  if (!s) return null;
  const w = s.widths.find((x) => x >= want) ?? s.widths[s.widths.length - 1];
  return `/stills/${key}-${w}${s.hash ? `.${s.hash}` : ""}.webp`;
}

/**
 * Effect 6, the giant word: UNIBODY across the screen, its letters cut from the carbon face (K14's raking-light macro,
 * in the visitor's feel), over the dark. Pinned (from 900 px), the camera passes through the O: the word grows about
 * its O until the O's counter fills the screen, and through it the edge-on racket (K02, the image Unibody opens on) comes
 * up to full light, handing over to the Unibody chapter. Below 900 px the word sits whole and the carbon drifts inside
 * its letters as it scrolls by. Reduced motion: the word, the line under it and the racket, still.
 */
export function TypeZoom() {
  const word = useRef<HTMLHeadingElement>(null);
  const { feel } = useFeel();
  const fill = stillUrl(feel === "pace" && sizes["K14-pace-wide"] ? "K14-pace-wide" : "K14-wide", 1920);
  const letters = v2.typeZoom.word.split("");
  const oIndex = v2.typeZoom.word.indexOf("O");

  /** The O's centre in the word's own box (before any transform), as a transform origin. */
  const origin = () => {
    const h = word.current;
    const o = h?.querySelector<HTMLElement>("[data-o]");
    if (!h || !o) return "50% 50%";
    return `${o.offsetLeft + o.offsetWidth / 2}px ${o.offsetTop + o.offsetHeight * 0.52}px`;
  };

  return (
    <V2Chapter
      id="v2-unibody-word"
      nextId="unibody"
      labelledBy="v2-unibody-word-title"
      length={1.8}
      className={styles.chapter}
      flow={`.${styles.word}`}
      flowStart="top bottom"
      flowEnd="bottom top"
      build={(tl, mode) => {
        if (mode === "flow") {
          tl.fromTo(`.${styles.word}`, { backgroundPosition: "30% 40%" }, { backgroundPosition: "70% 60%", duration: 1, immediateRender: true }, 0);
          return;
        }
        gsap.set(`.${styles.backdrop}`, { autoAlpha: 0.12 });
        tl.fromTo(`.${styles.lead}`, { autoAlpha: 1 }, { autoAlpha: 0, duration: 0.08, immediateRender: true }, 0.08)
          // Through the O: slow at first, then rushing in (power3.in), the racket rising to full light behind.
          .fromTo(
            `.${styles.word}`,
            { scale: 1, transformOrigin: origin },
            { scale: 42, duration: 0.62, ease: "power3.in", transformOrigin: origin, immediateRender: true },
            0.12,
          )
          .to(`.${styles.backdrop}`, { autoAlpha: 1, duration: 0.42, ease: "power1.in" }, 0.3)
          .to(`.${styles.word}`, { autoAlpha: 0, duration: 0.06 }, 0.7)
          .fromTo(`.${styles.backdrop}`, { scale: 1.08 }, { scale: 1, duration: 0.5, immediateRender: true }, 0.3)
          .to({}, { duration: 0.22 });
      }}
    >
      <div className={styles.stage}>
        <div className={styles.backdrop} aria-hidden="true">
          <Still id="K02" phoneCrop="portrait" phoneMedia="(max-aspect-ratio: 4/5)" alt="" sizes="100vw" className={styles.backdropStill} />
        </div>
        <div className={styles.center}>
          <h2
            ref={word}
            id="v2-unibody-word-title"
            className={styles.word}
            aria-label={v2.typeZoom.spoken}
            style={fill ? ({ "--fill": `url("${fill}")` } as CSSProperties) : undefined}
          >
            {letters.map((l, i) => (
              <span key={i} aria-hidden="true" data-o={i === oIndex ? "" : undefined}>
                {l}
              </span>
            ))}
          </h2>
          <p className={`t-lead ${styles.lead}`}>{v2.typeZoom.lead}</p>
        </div>
      </div>
    </V2Chapter>
  );
}
