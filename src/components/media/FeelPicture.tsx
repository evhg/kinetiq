"use client";

import { useEffect, useRef, useState } from "react";
import { useMotion } from "@/components/motion/MotionProvider";
import type { FeelId } from "@/content/site";
import { useFeel } from "@/lib/feel-store";

export type PictureSet = {
  sources: { media?: string; type: string; srcSet: string; sizes: string; width?: number; height?: number }[];
  src: string;
  width: number;
  height: number;
};

type Props = {
  command: PictureSet;
  pace: PictureSet;
  /** A fixed feel (the /reserve gallery's); omitted, the picture follows the site-wide feel. */
  feel?: FeelId;
  className?: string;
  alt: string;
  loading: "eager" | "lazy";
  fetchPriority: "high" | "low" | "auto";
  decoding: "sync" | "async";
};

/** The exit, shorter than the entry (globals.css "Feel stills" has the same two durations). */
const EXIT_MS = 150;

/**
 * A still with a Command and a Pace version, one <picture> that only ever holds one of them, so the two never both
 * download. The server and the hydrating render paint Command; after hydration a stored or chosen Pace swaps in.
 * The <picture> element (its class, and any tween on it) stays; only its sources and image are replaced, and the box
 * keeps its size (both versions share their crops), so nothing shifts.
 * The swap: the shown image fades out (150 ms; under html[data-feel] at once, for a picture that follows the toggle,
 * so a stored Pace never flashes Command before hydration), the other version's image is mounted hidden, and it fades
 * in once it has loaded (240 ms ease-out). Reduced motion: the same steps with no fade (globals.css).
 */
export function FeelPicture({ command, pace, feel: fixed, className, alt, loading, fetchPriority, decoding }: Props) {
  const site = useFeel();
  const target = fixed ?? site.feel;
  const { motionOn } = useMotion();
  const [shown, setShown] = useState<FeelId>(target);
  const [ready, setReady] = useState(true);
  // After the first swap the image is created by the client: it gets no src of its own (a detached image with a src
  // starts loading it at once), so it loads only the source its <picture> selects.
  const [swapped, setSwapped] = useState(false);
  const imgRef = useRef<HTMLImageElement>(null);

  // A new target: hide what is shown (150 ms), then mount the other version, hidden until it loads.
  useEffect(() => {
    if (target === shown) return;
    const img = imgRef.current;
    // Already invisible (html[data-feel] hid it before the first paint, or reduced motion): swap at once.
    const hidden = !img || !motionOn || getComputedStyle(img).opacity === "0";
    const out = window.setTimeout(() => setReady(false), 0);
    const swap = window.setTimeout(() => {
      // An image taken out of its <picture> falls back to its own src and fetches it: drop it first (the picture's
      // selected source, already loaded, stays on show until the swap).
      imgRef.current?.removeAttribute("src");
      setSwapped(true);
      setShown(target);
    }, hidden ? 0 : EXIT_MS);
    return () => {
      window.clearTimeout(out);
      window.clearTimeout(swap);
    };
  }, [target, shown, motionOn]);

  // The target's image is mounted: show it once it has loaded (a cached one may be complete already).
  useEffect(() => {
    if (ready || shown !== target) return;
    const img = imgRef.current;
    if (!img) return;
    let raf = 0;
    const show = () => {
      cancelAnimationFrame(raf);
      raf = requestAnimationFrame(() => setReady(true));
    };
    if (img.complete) show();
    img.addEventListener("load", show);
    img.addEventListener("error", show);
    return () => {
      cancelAnimationFrame(raf);
      img.removeEventListener("load", show);
      img.removeEventListener("error", show);
    };
  }, [ready, shown, target]);

  const set = shown === "pace" ? pace : command;
  return (
    <picture
      className={className}
      data-feel-swap=""
      data-feel-follow={fixed === undefined ? "" : undefined}
      data-feel-shown={shown}
      data-feel-ready={ready}
    >
      {/* The sources are updated in place; the image is keyed by the feel, so the old one is removed before the sources
          change (it never reselects and fetches) and a fresh one, whose load is its own, takes the new version. */}
      {set.sources.map((s) => (
        <source key={`${s.media ?? ""}${s.type}`} {...s} />
      ))}
      <img
        key={shown}
        ref={imgRef}
        src={swapped ? undefined : set.src}
        width={set.width}
        height={set.height}
        alt={alt}
        loading={loading}
        fetchPriority={fetchPriority}
        decoding={decoding}
      />
    </picture>
  );
}

