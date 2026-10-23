"use client";

import { useId, useRef } from "react";
import type { FeelId } from "@/content/site";
import { useFeel } from "@/lib/feel-store";
import styles from "./FeelToggle.module.css";

type Props = {
  /** The group's accessible name and the two option labels, from src/content/site.ts (this module carries no copy). */
  label: string;
  labels: Record<FeelId, string>;
  /** "hero": as tall as the hero's Reserve Now; "compact": as tall as the header's. */
  size?: "hero" | "compact";
  className?: string;
  /** Out of the tab order and the accessibility tree while hidden (the header's, when its Reserve Now is hidden). */
  inert?: boolean;
  /** Mirrored on data-visible, for a caller that fades the toggle in and out (the header). */
  visible?: boolean;
};

const ORDER: FeelId[] = ["command", "pace"];

/**
 * Command | Pace: a two-option radio group (native radios, so the arrow keys move the choice and Tab enters on the
 * checked one). Every toggle on the page shows the same state: the thumb and the labels follow html[data-feel], which
 * the head script sets before the first paint, so a stored Pace never flashes Command. The thumb slides on a pointer
 * (transform, 220 ms ease-out) and jumps at once from the keyboard (Emil Kowalski's rule).
 */
export function FeelToggle({ label, labels, size = "hero", className, inert, visible }: Props) {
  const { feel, setFeel } = useFeel();
  const name = useId();
  const root = useRef<HTMLDivElement>(null);
  const instant = (on: boolean) => {
    const el = root.current;
    if (!el) return;
    if (on) el.dataset.instant = "";
    else delete el.dataset.instant;
  };
  return (
    <div
      ref={root}
      role="radiogroup"
      aria-label={label}
      className={`${styles.toggle} ${className ?? ""}`}
      data-size={size}
      inert={inert}
      data-visible={visible}
      onKeyDown={() => instant(true)}
      onPointerDown={() => instant(false)}
    >
      <span className={styles.thumb} aria-hidden="true" />
      {ORDER.map((id) => (
        <label key={id} className={styles.option} data-option={id}>
          <input
            type="radio"
            name={name}
            value={id}
            checked={feel === id}
            onChange={() => setFeel(id)}
            className={styles.input}
          />
          <span className={styles.swatch} aria-hidden="true" />
          <span className={styles.text}>{labels[id]}</span>
        </label>
      ))}
    </div>
  );
}
