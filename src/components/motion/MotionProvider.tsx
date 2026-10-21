"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import { MOTION_STORAGE_KEY, type MotionSetting } from "@/lib/motion-preference";

type MotionContextValue = {
  /** True when animation is allowed: the user's switch, else the OS setting. */
  motionOn: boolean;
  /** False until the client has read the saved setting. */
  ready: boolean;
  setMotion: (setting: MotionSetting) => void;
};

const MotionContext = createContext<MotionContextValue>({
  motionOn: false,
  ready: false,
  setMotion: () => {},
});

function readInitial(): MotionSetting {
  const fromHtml = document.documentElement.dataset.motion;
  return fromHtml === "on" ? "on" : "off";
}

export function MotionProvider({ children }: { children: ReactNode }) {
  const [motion, setMotionState] = useState<MotionSetting>("off");
  const [ready, setReady] = useState(false);

  useEffect(() => {
    // The inline head script already resolved saved choice vs OS setting.
    // eslint-disable-next-line react-hooks/set-state-in-effect -- sync from the pre-hydration DOM once
    setMotionState(readInitial());
    setReady(true);

    // Follow OS changes only while the user hasn't chosen explicitly.
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    const onChange = () => {
      let saved: string | null = null;
      try {
        saved = localStorage.getItem(MOTION_STORAGE_KEY);
      } catch {}
      if (saved !== "on" && saved !== "off") {
        const next: MotionSetting = mq.matches ? "off" : "on";
        document.documentElement.dataset.motion = next;
        setMotionState(next);
      }
    };
    mq.addEventListener("change", onChange);
    return () => mq.removeEventListener("change", onChange);
  }, []);

  const setMotion = useCallback((setting: MotionSetting) => {
    document.documentElement.dataset.motion = setting;
    try {
      localStorage.setItem(MOTION_STORAGE_KEY, setting);
    } catch {}
    setMotionState(setting);
  }, []);

  return (
    <MotionContext.Provider value={{ motionOn: motion === "on", ready, setMotion }}>
      {children}
    </MotionContext.Provider>
  );
}

export function useMotion() {
  return useContext(MotionContext);
}
