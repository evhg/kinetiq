"use client";

import { useEffect, useImperativeHandle, useRef, type Ref } from "react";
import { useMotion } from "@/components/motion/MotionProvider";
import generated from "@/content/sequences.generated.json";
import { useFeel } from "@/lib/feel-store";

/**
 * The hero's swivel (owner, 2026-10-23): as the hero scrolls away, the lit racket turns about its handle (yaw 0° to
 * about 35°), drawn from a frame sequence (scripts/sequence.mjs) onto a canvas over the lit still. Frame 0 is the lit
 * still's own composition, so the canvas only shows from frame 1 and the handover is invisible. Each frame holds only
 * the rectangle that ever changes (the racket, its shadow and its light on the floor); the canvas covers exactly that
 * rectangle of the still, placed with the still's own object-fit and object-position, and the still shows around it.
 * Frames load after the page's load event, in the background, coarse first (every 32nd, then every 16th ... every
 * one); the swivel starts once no gap between decoded frames is wider than 4, and draws the nearest decoded frame
 * meanwhile. Missing sequence (the feel's or the layout's not exported yet), Save-Data, a failed frame or reduced
 * motion: the canvas stays hidden and the hero is the still, exactly as before.
 */

type Entry = {
  frames: number;
  w: number;
  h: number;
  crop: { x: number; y: number; w: number; h: number };
  widths: number[];
  hash: string;
};
const manifest = generated as Record<string, Entry>;

type Frame = ImageBitmap | HTMLImageElement;
type Seq = {
  key: string;
  name: string;
  entry: Entry;
  width: number;
  frames: (Frame | null)[];
  /** Load order, coarse to fine, and how far through it the loader has started. */
  order: number[];
  next: number;
  inFlight: number;
  failed: boolean;
  ready: boolean;
  onChange: Set<() => void>;
};

export type SwivelHandle = { progress: (p: number) => void };

/** Sequences decoded on this page, kept across a visit to /reserve so Back finds them decoded. */
const cache = new Map<string, Seq>();
const CONCURRENCY = 3;
/** The swivel starts once no two decoded frames are more than this many frames apart. */
const READY_GAP = 4;

function loadOrder(n: number) {
  const order: number[] = [0, n - 1];
  const seen = new Set(order);
  for (let stride = 32; stride >= 1; stride /= 2)
    for (let i = 0; i < n; i += stride)
      if (!seen.has(i)) {
        seen.add(i);
        order.push(i);
      }
  return order;
}

const frameUrl = (s: Seq, i: number) => `/stills/seq/${s.name}/${String(i).padStart(3, "0")}-${s.width}.${s.entry.hash}.webp`;

async function decode(url: string): Promise<Frame> {
  if (typeof createImageBitmap === "function") {
    const res = await fetch(url, { credentials: "same-origin" });
    if (!res.ok) throw new Error(String(res.status));
    return createImageBitmap(await res.blob());
  }
  const img = new Image();
  img.src = url;
  await img.decode();
  return img;
}

function maxGap(s: Seq) {
  let gap = 0;
  let last = -1;
  s.frames.forEach((f, i) => {
    if (!f) return;
    if (last >= 0) gap = Math.max(gap, i - last);
    last = i;
  });
  return last === s.frames.length - 1 && s.frames[0] ? gap : Infinity;
}

/** Starts (or resumes) loading while the sequence is wanted; `active` says whether it still is. */
function pump(s: Seq, active: () => boolean) {
  while (!s.failed && active() && s.inFlight < CONCURRENCY && s.next < s.order.length) {
    const i = s.order[s.next++];
    s.inFlight++;
    decode(frameUrl(s, i)).then(
      (frame) => {
        s.inFlight--;
        // Released (the other feel was picked) or failed meanwhile: drop it.
        if (s.failed) {
          if ("close" in frame) frame.close();
          return;
        }
        s.frames[i] = frame;
        if (!s.ready && maxGap(s) <= READY_GAP) s.ready = true;
        s.onChange.forEach((f) => f());
        pump(s, active);
      },
      () => {
        s.inFlight--;
        s.failed = true;
        s.onChange.forEach((f) => f());
      },
    );
  }
}

function release(s: Seq) {
  s.failed = true;
  for (const f of s.frames) if (f && "close" in f) f.close();
  s.frames.fill(null);
  cache.delete(s.key);
}

/** The nearest decoded frame to i. */
function nearest(s: Seq, i: number) {
  for (let d = 0; d < s.frames.length; d++) {
    const f = s.frames[i - d] ?? s.frames[i + d];
    if (f) return f;
  }
  return null;
}

/** Percentages of object-position ("50% 100%"); anything else counts as centred. */
function objectPosition(img: HTMLImageElement | null) {
  const parts = (img ? getComputedStyle(img).objectPosition : "").split(/\s+/);
  const pct = (v: string | undefined) => (v && v.endsWith("%") ? parseFloat(v) / 100 : 0.5);
  return [pct(parts[0]), pct(parts[1])] as const;
}

type Props = {
  ref?: Ref<SwivelHandle>;
  /** The hero's portrait layout (phones and portrait tablets), the same query as the still's phoneMedia. */
  portraitQuery: string;
  className?: string;
};

export function HeroSwivel({ ref, portraitQuery, className }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const { motionOn } = useMotion();
  const { feel } = useFeel();
  const progress = useRef(0);
  const redraw = useRef<() => void>(() => {});

  useImperativeHandle(
    ref,
    () => ({
      progress: (p: number) => {
        progress.current = p;
        redraw.current();
      },
    }),
    [],
  );

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!motionOn || !canvas) return;
    const conn = (navigator as Navigator & { connection?: { saveData?: boolean } }).connection;
    if (conn?.saveData) return;
    const box = canvas.parentElement!;
    const portrait = window.matchMedia(portraitQuery);
    const ctx = canvas.getContext("2d", { alpha: false });
    if (!ctx) return;

    let seq: Seq | null = null;
    let started = false;
    let alive = true;
    let drawn: Frame | null = null;
    let on = false;
    let raf = 0;
    /** The canvas's place over the still, in CSS px, and its backing size. */
    let laidOut = false;

    const show = (v: boolean) => {
      if (v === on) return;
      on = v;
      canvas.dataset.on = String(v);
    };

    const layout = () => {
      if (!seq) return;
      const { entry } = seq;
      const img = box.querySelector("img");
      const bw = box.clientWidth;
      const bh = box.clientHeight;
      if (!bw || !bh) return;
      // object-fit: cover, at the still's object-position.
      const scale = Math.max(bw / entry.w, bh / entry.h);
      const [px, py] = objectPosition(img);
      const ox = (bw - entry.w * scale) * px;
      const oy = (bh - entry.h * scale) * py;
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      const snap = (v: number) => Math.round(v * dpr) / dpr;
      const left = snap(ox + entry.crop.x * scale);
      const top = snap(oy + entry.crop.y * scale);
      const right = snap(ox + (entry.crop.x + entry.crop.w) * scale);
      const bottom = snap(oy + (entry.crop.y + entry.crop.h) * scale);
      Object.assign(canvas.style, { left: `${left}px`, top: `${top}px`, width: `${right - left}px`, height: `${bottom - top}px` });
      const cw = Math.round((right - left) * dpr);
      const ch = Math.round((bottom - top) * dpr);
      if (canvas.width !== cw || canvas.height !== ch) {
        canvas.width = cw;
        canvas.height = ch;
        drawn = null;
      }
      laidOut = true;
    };

    const draw = () => {
      raf = 0;
      if (!alive) return;
      const s = seq;
      const i = s ? Math.round(Math.min(1, Math.max(0, progress.current)) * (s.entry.frames - 1)) : 0;
      // Frame 0 is the still: the canvas shows only once the racket has turned.
      if (!s || !s.ready || s.failed || i === 0) return show(false);
      if (!laidOut) layout();
      const frame = nearest(s, i);
      if (!frame || !canvas.width) return show(false);
      if (frame !== drawn) {
        ctx.imageSmoothingEnabled = true;
        ctx.imageSmoothingQuality = "medium";
        ctx.drawImage(frame, 0, 0, canvas.width, canvas.height);
        drawn = frame;
      }
      show(true);
    };
    // Scroll updates arrive on GSAP's ticker; loads arrive any time: either way, at most one draw a frame.
    const schedule = () => {
      if (!raf) raf = requestAnimationFrame(draw);
    };
    redraw.current = schedule;

    const pick = () => {
      const name = `K01-swivel-${feel}-${portrait.matches ? "phone" : "desktop"}`;
      const entry = manifest[name];
      if (seq && seq.name === name) return;
      // The other layout (a turned tablet): hide, then load this one; the other's frames go once this one exists.
      seq?.onChange.delete(schedule);
      seq = null;
      drawn = null;
      laidOut = false;
      show(false);
      if (!entry) return;
      for (const s of cache.values()) if (s.name !== name) release(s);
      // The narrowest export that covers the drawn frame (within 15%) at the screen's density, capped at 2.
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      const drawnW = Math.max(box.clientWidth / entry.w, box.clientHeight / entry.h) * entry.w * dpr;
      const width = entry.widths.find((w) => w * 1.15 >= drawnW) ?? entry.widths[entry.widths.length - 1];
      const key = `${name}@${width}`;
      let s = cache.get(key);
      if (!s) {
        s = { key, name, entry, width, frames: Array(entry.frames).fill(null), order: loadOrder(entry.frames), next: 0, inFlight: 0, failed: false, ready: false, onChange: new Set() };
        cache.set(key, s);
      }
      seq = s;
      s.onChange.add(schedule);
      if (started) pump(s, () => alive && seq === s);
      schedule();
    };

    const start = () => {
      if (!alive || started) return;
      started = true;
      const s = seq;
      if (s) pump(s, () => alive && seq === s);
    };
    pick();
    // After the load event (the hero's stills are in), when the main thread is idle: never ahead of the LCP.
    let idle = 0;
    const later = () => {
      idle = window.requestIdleCallback ? window.requestIdleCallback(start, { timeout: 2000 }) : window.setTimeout(start, 300);
    };
    if (document.readyState === "complete") later();
    else window.addEventListener("load", later, { once: true });

    const resize = new ResizeObserver(() => {
      laidOut = false;
      layout();
      schedule();
    });
    resize.observe(box);
    portrait.addEventListener("change", pick);

    return () => {
      alive = false;
      cancelAnimationFrame(raf);
      if (window.cancelIdleCallback) window.cancelIdleCallback(idle);
      window.clearTimeout(idle);
      window.removeEventListener("load", later);
      resize.disconnect();
      portrait.removeEventListener("change", pick);
      redraw.current = () => {};
      // The frames stay decoded for Back (a half-loaded sequence resumes where it stopped); a change of feel releases
      // them once the other feel's sequence is picked.
      seq?.onChange.delete(schedule);
      show(false);
    };
  }, [motionOn, feel, portraitQuery]);

  return <canvas ref={canvasRef} className={className} aria-hidden="true" data-on="false" />;
}
