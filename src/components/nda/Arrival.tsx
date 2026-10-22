"use client";

import { useEffect } from "react";
import { NDA_TRIED_KEY } from "@/lib/nda";

const VEIL_ANIMATION = "kq-arrive";

/**
 * The arrival from the NDA gate (html[data-arrive], set before first paint by the head script in
 * src/lib/motion-preference.ts; the veil itself is CSS in globals.css). On the real page it clears the gate's
 * "tried" flag, so a reload a few seconds later does not replay the veil; on the gate the flag means the cookie did
 * not stick, and NdaGate reads it. The attribute goes once the veil has lifted (or after 4 s at the latest, so a
 * stream that never finishes cannot keep the page veiled).
 */
export function Arrival() {
  useEffect(() => {
    const html = document.documentElement;
    if (!("arrive" in html.dataset)) return;
    if (!document.querySelector("[data-nda-gate]")) {
      try {
        sessionStorage.removeItem(NDA_TRIED_KEY);
      } catch {}
    }
    const done = () => {
      delete html.dataset.arrive;
    };
    const onEnd = (e: AnimationEvent) => {
      if (e.animationName === VEIL_ANIMATION) done();
    };
    html.addEventListener("animationend", onEnd);
    // Hydration can come after the veil has already lifted: then the attribute goes now. While /reserve's shell
    // holds the veil, no animation runs yet and animationend ends it.
    if (typeof CSSAnimation === "function" && typeof html.getAnimations === "function") {
      const running = html
        .getAnimations({ subtree: true })
        .find((a): a is CSSAnimation => a instanceof CSSAnimation && a.animationName === VEIL_ANIMATION);
      if (running) running.finished.then(done, done);
      else if (!document.querySelector("[data-reserve-shell]")) done();
    }
    const timer = window.setTimeout(done, 4000);
    return () => {
      html.removeEventListener("animationend", onEnd);
      window.clearTimeout(timer);
    };
  }, []);
  return null;
}
