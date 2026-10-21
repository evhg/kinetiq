"use client";

import { useMotion } from "./MotionProvider";

/** Visible Motion on/off switch. The choice is saved between visits. */
export function MotionToggle() {
  const { motionOn, ready, setMotion } = useMotion();
  return (
    <button
      type="button"
      className="motion-toggle"
      aria-pressed={motionOn}
      disabled={!ready}
      onClick={() => setMotion(motionOn ? "off" : "on")}
    >
      <span className="motion-toggle__dot" aria-hidden="true" />
      Motion {motionOn ? "on" : "off"}
    </button>
  );
}
