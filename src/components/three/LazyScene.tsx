"use client";

import dynamic from "next/dynamic";
import { useEffect, useState } from "react";
import { useMotion } from "@/components/motion/MotionProvider";

const SmokeScene = dynamic(() => import("./SmokeScene"), { ssr: false });

function hasWebGL() {
  try {
    const canvas = document.createElement("canvas");
    return Boolean(canvas.getContext("webgl2") || canvas.getContext("webgl"));
  } catch {
    return false;
  }
}

/**
 * Shows the static fallback first (it is the LCP-safe image), then swaps in
 * the R3F scene after the page is idle, only when WebGL works and motion is on.
 */
export function LazyScene({ fallbackSrc, fallbackAlt }: { fallbackSrc: string; fallbackAlt: string }) {
  const { motionOn } = useMotion();
  const [canRender, setCanRender] = useState(false);

  useEffect(() => {
    if (!motionOn) {
      // eslint-disable-next-line react-hooks/set-state-in-effect -- reflect the switch immediately
      setCanRender(false);
      return;
    }
    if (!hasWebGL()) return;
    const ric = window.requestIdleCallback ?? ((cb: () => void) => window.setTimeout(cb, 200));
    const cancel = window.cancelIdleCallback ?? window.clearTimeout;
    const id = ric(() => setCanRender(true));
    return () => cancel(id);
  }, [motionOn]);

  return (
    <div className="scene" data-scene={canRender ? "webgl" : "fallback"}>
      {/* eslint-disable-next-line @next/next/no-img-element -- static SVG fallback, no optimisation needed */}
      <img className="scene-fallback" src={fallbackSrc} alt={fallbackAlt} width={800} height={800} />
      {canRender ? <SmokeScene /> : null}
    </div>
  );
}
