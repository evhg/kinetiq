"use client";

import { useId } from "react";
import type { GripId } from "@/content/prefs";
import { useGrip } from "@/lib/grip-store";
import styles from "./FeelToggle.module.css";

type Props = {
  /** The group's accessible name and the two option labels, from src/content/site.ts (this module carries no copy). */
  label: string;
  labels: Record<GripId, string>;
  /** "hero" beside Reserve Now; "compact" in the header (wide screens); "panel" in the header's view panel. */
  size?: "hero" | "compact" | "panel";
  className?: string;
  /** Out of the tab order and the accessibility tree while hidden (the header's, over the hero). */
  inert?: boolean;
  /** Mirrored on data-visible, for a caller that fades the toggle in and out (the header). */
  visible?: boolean;
};

const ORDER: GripId[] = ["on", "off"];

/**
 * Grip and Naked (owner, 2026-11-02: "could we have another minimal toggle to show a remove the grip?"): the racket
 * with its overgrip, or without it, so the bare carbon handle shows running straight out of the head. The feel toggle's
 * visual language (FeelToggle.module.css): a small handle glyph with its name, the chosen one ringed and its name in
 * --text. The bare handle's glyph is the face's carbon in the feel on show (html[data-feel]), the grip's the black wrap.
 * A native radio group: arrow keys move the choice, Tab enters on the checked one, every option at least 44 px square
 * to the touch. The state is read from html[data-grip] (set before the first paint), so a stored choice never flashes,
 * and every grip toggle on the page (the hero's, the header's, the view panel's) shows the same one (lib/grip-store.ts).
 */
export function GripToggle({ label, labels, size = "hero", className, inert, visible }: Props) {
  const { grip, setGrip } = useGrip();
  const name = useId();
  return (
    <div
      role="radiogroup"
      aria-label={label}
      className={`${styles.toggle} ${className ?? ""}`}
      data-size={size}
      data-kind="grip"
      inert={inert}
      data-visible={visible}
    >
      {ORDER.map((id) => (
        <label key={id} className={styles.option} data-grip-option={id}>
          <input type="radio" name={name} value={id} checked={grip === id} onChange={() => setGrip(id)} className={styles.input} />
          <span className={`${styles.swatch} ${styles.handle}`} aria-hidden="true" />
          <span className={styles.text}>{labels[id]}</span>
        </label>
      ))}
    </div>
  );
}
