"use client";

import { useCallback, useEffect, useId, useRef, useState, type FocusEvent, type MouseEvent } from "react";
import type { FeelId, GripId } from "@/content/prefs";
import { useFeel } from "@/lib/feel-store";
import { useGrip } from "@/lib/grip-store";
import { FeelToggle } from "./FeelToggle";
import { GripToggle } from "./GripToggle";
import styles from "./ViewControl.module.css";

/** The view control's words, passed in from the server (Chrome.tsx, src/content/site.ts): this module carries no copy. */
export type ViewCopy = {
  /** The panel's name, and the button's before the current choice ("Feel and handle: Command, Grip"). */
  label: string;
  feel: { label: string; labels: Record<FeelId, string> };
  grip: { label: string; labels: Record<GripId, string> };
};

/**
 * The Feel (Command, Pace) and Handle (Grip, Naked) choices in the header, so they are one tap away anywhere on /,
 * /reserve and /reserved (owner, 2026-11-03: "when on iphone, I have to scroll all the way back up to change the
 * toggle?"). From 1024 px both radio groups sit in the header with their names. Below it, one 44 px button shows the
 * current face and handle (white or black swatch, the overgrip or the bare carbon, from html[data-feel] and
 * html[data-grip], so the server paint is already right) and opens a small panel under the header holding the same two
 * named groups. A disclosure, not a modal: the panel follows the button in the tab order; it closes on Escape (focus
 * back on the button), on a tap or a click outside, when focus leaves it, and when the header hides it (over the hero,
 * whose own toggles show). It stays open while a choice is made, so Grip and Naked can be compared on the still beneath.
 * Opened from the keyboard it appears at once and focus moves to the checked option (no animation on keyboard actions);
 * from a tap it fades and settles in 200 ms ease-out from scale 0.97, and leaves in 150 ms (DESIGN.md "Feel toggle").
 * Every toggle on the page shares one store per axis (lib/feel-store.ts, lib/grip-store.ts), so all of them agree. The
 * button's name carries the choice on show ("Feel and handle: Command, Naked"), so a screen reader hears it before opening.
 * `flush`: the compact Reserve Now after it is hidden, so the button (and the wide screens' groups) slide right by
 * --view-shift to the row's end instead of leaving a hole (`translate`, a transform: nothing reflows).
 */
export function ViewControl({ copy, visible, flush = false }: { copy: ViewCopy; visible: boolean; flush?: boolean }) {
  const { feel } = useFeel();
  const { grip } = useGrip();
  const name = `${copy.label}: ${copy.feel.labels[feel]}, ${copy.grip.labels[grip]}`;
  const [open, setOpen] = useState(false);
  // Opened or closed from the keyboard: no transition (CLAUDE.md "Interface micro-animations").
  const [instant, setInstant] = useState(false);
  const focusOnOpen = useRef(false);
  const wrap = useRef<HTMLDivElement>(null);
  const button = useRef<HTMLButtonElement>(null);
  const panel = useRef<HTMLDivElement>(null);
  const panelId = useId();

  const close = useCallback((opts: { instant?: boolean; refocus?: boolean } = {}) => {
    setInstant(Boolean(opts.instant));
    setOpen(false);
    if (opts.refocus) button.current?.focus();
  }, []);

  const onButton = (e: MouseEvent<HTMLButtonElement>) => {
    // A click with no pointer behind it (detail 0) is Enter or Space.
    const keyboard = e.detail === 0;
    setInstant(keyboard);
    focusOnOpen.current = keyboard && !open;
    setOpen(!open);
  };

  // Keyboard open: focus the checked option of the first group, so the arrow keys work at once.
  useEffect(() => {
    if (!open || !focusOnOpen.current) return;
    focusOnOpen.current = false;
    panel.current?.querySelector<HTMLInputElement>("input:checked")?.focus();
  }, [open]);

  // Light dismiss: a press anywhere outside the button and the panel, or Escape wherever focus is.
  useEffect(() => {
    if (!open) return;
    const onDown = (e: PointerEvent) => {
      if (e.target instanceof Node && wrap.current?.contains(e.target)) return;
      close();
    };
    const onKey = (e: globalThis.KeyboardEvent) => {
      if (e.key === "Escape") close({ instant: true, refocus: true });
    };
    document.addEventListener("pointerdown", onDown, true);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("pointerdown", onDown, true);
      document.removeEventListener("keydown", onKey);
    };
  }, [open, close]);

  // The header hides the control over the hero: the panel goes with it (and stays closed when the control returns).
  const [wasVisible, setWasVisible] = useState(visible);
  if (visible !== wasVisible) {
    setWasVisible(visible);
    if (!visible) setOpen(false);
  }

  // Tab past the panel's last option (or Shift+Tab before the button): focus has left, so the panel closes.
  const onBlur = (e: FocusEvent<HTMLDivElement>) => {
    if (!open) return;
    const next = e.relatedTarget;
    if (next instanceof Node && wrap.current?.contains(next)) return;
    if (next === null) return; // focus went nowhere (a tap on the page): the pointer handler decides
    close({ instant: true });
  };

  return (
    <>
      {/* Wide screens: both groups in the header, with their names. */}
      <div className={styles.inline} data-visible={visible} data-flush={flush} inert={!visible}>
        <FeelToggle label={copy.feel.label} labels={copy.feel.labels} size="compact" />
        <span className={styles.rule} aria-hidden="true" />
        <GripToggle label={copy.grip.label} labels={copy.grip.labels} size="compact" />
      </div>
      {/* Below 1024 px: one button and its panel. */}
      <div ref={wrap} className={styles.view} data-visible={visible} data-flush={flush} inert={!visible} onBlur={onBlur}>
        <button
          ref={button}
          type="button"
          className={styles.button}
          aria-label={name}
          aria-expanded={open}
          aria-controls={panelId}
          data-instant={instant}
          onClick={onButton}
        >
          <span className={styles.face} aria-hidden="true" />
          <span className={styles.handle} aria-hidden="true" />
          <span className={styles.chevron} aria-hidden="true" />
        </button>
        <div
          ref={panel}
          id={panelId}
          className={styles.panel}
          data-open={open}
          data-instant={instant}
          inert={!open}
          role="group"
          aria-label={copy.label}
        >
          <div className={styles.line}>
            <span className={styles.name} aria-hidden="true">
              {copy.feel.label}
            </span>
            <FeelToggle label={copy.feel.label} labels={copy.feel.labels} size="panel" className={styles.group} />
          </div>
          <div className={styles.line}>
            <span className={styles.name} aria-hidden="true">
              {copy.grip.label}
            </span>
            <GripToggle label={copy.grip.label} labels={copy.grip.labels} size="panel" className={styles.group} />
          </div>
        </div>
      </div>
    </>
  );
}
