"use client";

import { useId } from "react";
import type { FeelId } from "@/content/site";
import { useFeel } from "@/lib/feel-store";
import styles from "./FeelToggle.module.css";

type Props = {
  /** The group's accessible name and the two option labels, from src/content/site.ts (this module carries no copy). */
  label: string;
  labels: Record<FeelId, string>;
  /**
   * "hero": two face swatches with their names, quiet beside or above Reserve Now; "compact": the header's, the
   * swatches alone below 700 px (the names stay as the radios' labels for assistive tech), with their names from 700 px.
   */
  size?: "hero" | "compact";
  className?: string;
  /** Out of the tab order and the accessibility tree while hidden (the header's, when its Reserve Now is hidden). */
  inert?: boolean;
  /** Mirrored on data-visible, for a caller that fades the toggle in and out (the header). */
  visible?: boolean;
};

const ORDER: FeelId[] = ["command", "pace"];

/**
 * Command and Pace (owner, 2026-10-28: "make the toggle more minimal"): two small face swatches, white 3K and black
 * 12K, the chosen one ringed and its name in --text, the other's name --muted. No pill and no thumb, so it never
 * competes with Reserve Now. A native radio group: the arrow keys move the choice and Tab enters on the checked one;
 * every option is at least 44 px square to the touch, however small it looks. Every toggle on the page shows the same
 * state: the rings and the names follow html[data-feel], which the head script sets before the first paint, so a stored
 * Pace never flashes Command.
 */
export function FeelToggle({ label, labels, size = "hero", className, inert, visible }: Props) {
  const { feel, setFeel } = useFeel();
  const name = useId();
  return (
    <div
      role="radiogroup"
      aria-label={label}
      className={`${styles.toggle} ${className ?? ""}`}
      data-size={size}
      inert={inert}
      data-visible={visible}
    >
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
