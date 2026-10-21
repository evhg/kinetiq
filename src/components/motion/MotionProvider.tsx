"use client";

import { createContext, useContext, useEffect, useState, type ReactNode } from "react";

type MotionContextValue = {
  /** False when the OS asks for reduced motion. */
  motionOn: boolean;
  /** False until the client has read the media query. */
  ready: boolean;
};

const MotionContext = createContext<MotionContextValue>({ motionOn: false, ready: false });

export function MotionProvider({ children }: { children: ReactNode }) {
  const [motionOn, setMotionOn] = useState(false);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    const sync = () => {
      const on = !mq.matches;
      document.documentElement.dataset.motion = on ? "on" : "off";
      setMotionOn(on);
    };
    sync();
    // eslint-disable-next-line react-hooks/set-state-in-effect -- one-time client read
    setReady(true);
    mq.addEventListener("change", sync);
    return () => mq.removeEventListener("change", sync);
  }, []);

  return <MotionContext.Provider value={{ motionOn, ready }}>{children}</MotionContext.Provider>;
}

export function useMotion() {
  return useContext(MotionContext);
}
