"use client";

import { useId } from "react";
import type { GripId } from "@/content/site";
import { useGrip } from "@/lib/grip-store";
import styles from "./FeelToggle.module.css";

type Props = {
  /** The group's accessible name and the two option labels, from src/content/site.ts (this module carries no copy). */
  label: string;
  labels: Record<GripId, string>;
  className?: string;
};

const ORDER: GripId[] = ["on", "off"];

/**
 * Grip and Bare (owner, 2026-11-02: "could we have another minimal toggle to show a remove the grip?"): the hero racket
 * with its overgrip, or without it, so the bare carbon handle shows running straight out of the head. The feel toggle's
 * visual language (FeelToggle.module.css): a small handle glyph with its name, the chosen one ringed and its name in
 * --text. The bare handle's glyph is the face's carbon in the feel on show (html[data-feel]), the grip's the black wrap.
 * A native radio group: arrow keys move the choice, Tab enters on the checked one, every option at least 44 px square
 * to the touch. The state is read from html[data-grip] (set before the first paint), so a stored choice never flashes.
 * Only in the hero: the header's toggle stays the feel alone (the grip changes nothing on screen once the hero is gone).
 */
export function GripToggle({ label, labels, className }: Props) {
  const { grip, setGrip } = useGrip();
  const name = useId();
  return (
    <div role="radiogroup" aria-label={label} className={`${styles.toggle} ${className ?? ""}`} data-size="hero" data-kind="grip">
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
