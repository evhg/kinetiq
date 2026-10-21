"use client";

import { useEffect } from "react";
import Lenis from "lenis";
import { gsap, ScrollTrigger } from "@/lib/gsap";
import { useMotion } from "./MotionProvider";

declare global {
  interface Window {
    __lenis?: Lenis;
  }
}

const DESKTOP = "(min-width: 1024px) and (hover: hover) and (pointer: fine)";

/**
 * Lenis smooth scrolling on desktop only, driven by GSAP's ticker so
 * ScrollTrigger and Lenis share one clock. Off when motion is off.
 */
export function SmoothScroll() {
  const { motionOn } = useMotion();

  useEffect(() => {
    if (!motionOn) return;
    const mq = window.matchMedia(DESKTOP);
    let lenis: Lenis | null = null;
    let tick: ((time: number) => void) | null = null;

    const start = () => {
      lenis = new Lenis({ autoRaf: false });
      lenis.on("scroll", ScrollTrigger.update);
      tick = (time: number) => lenis?.raf(time * 1000);
      gsap.ticker.add(tick);
      gsap.ticker.lagSmoothing(0);
      window.__lenis = lenis;
      ScrollTrigger.refresh();
    };
    const stop = () => {
      if (tick) gsap.ticker.remove(tick);
      lenis?.destroy();
      lenis = null;
      tick = null;
      delete window.__lenis;
      gsap.ticker.lagSmoothing(500, 33);
    };
    const sync = () => {
      stop();
      if (mq.matches) start();
    };

    sync();
    mq.addEventListener("change", sync);
    return () => {
      mq.removeEventListener("change", sync);
      stop();
    };
  }, [motionOn]);

  return null;
}
