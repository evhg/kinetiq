"use client";

import dynamic from "next/dynamic";
import { useEffect, useState, type ReactNode } from "react";
import { useMotion } from "@/components/motion/MotionProvider";

const HeroScene = dynamic(() => import("./HeroScene"), { ssr: false });

function hasWebGL() {
  try {
    const canvas = document.createElement("canvas");
    return Boolean(canvas.getContext("webgl2") || canvas.getContext("webgl"));
  } catch {
    return false;
  }
}

/**
 * The server-rendered still (children) paints first and is the LCP-safe image.
 * The R3F scene mounts after the page is idle, only with WebGL and motion on,
 * and the still fades out once the first 3D frame has rendered.
 */
export function LazyHeroScene({ children }: { children: ReactNode }) {
  const { motionOn } = useMotion();
  const [mount, setMount] = useState(false);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    if (!motionOn) {
      // eslint-disable-next-line react-hooks/set-state-in-effect -- reflect the switch immediately
      setMount(false);
      setReady(false);
      return;
    }
    if (!hasWebGL()) return;
    const ric = window.requestIdleCallback ?? ((cb: () => void) => window.setTimeout(cb, 200));
    const cancel = window.cancelIdleCallback ?? window.clearTimeout;
    const id = ric(() => setMount(true), { timeout: 1500 });
    return () => cancel(id);
  }, [motionOn]);

  return (
    <div className="hero-visual" data-scene={ready ? "webgl" : "fallback"}>
      <div className="hero-still">{children}</div>
      {mount ? <HeroScene onReady={() => setReady(true)} /> : null}
    </div>
  );
}
