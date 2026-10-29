"use client";

import { useEffect, useImperativeHandle, useRef, type Ref } from "react";
import { useMotion } from "@/components/motion/MotionProvider";
import generated from "@/content/sequences.generated.json";
import { useFeel } from "@/lib/feel-store";

/**
 * A scroll-scrubbed swivel (owner, 2026-10-23; generalised 2026-10-28 for Unibody's K02): a racket turning, drawn from a
 * frame sequence (scripts/sequence.mjs) onto a canvas over the still it starts from. The sequence for each feel and
 * layout is `<sequence>-<feel>-desktop|phone` (sequences.generated.json). Frame 0 is the still's own composition, so
 * the canvas only shows from frame 1 and the handover is invisible. Each frame holds only the rectangle that ever
 * changes; the canvas covers exactly that rectangle of the still, placed with the still's own object-fit (cover) and
 * object-position inside the canvas's parent (the box the still fills), and the still shows around it. The owner
 * drives it through the ref: progress(0..1).
 * Frames load in the background, coarse first (every 32nd, then every 16th ... every one), from the page's load event,
 * the visitor's first scroll or touch, or 1.5 s after mount, whichever comes first (iPhone, 2026-10-28: a visitor who
 * scrolls at once must not outrun a late load event, which in-app browsers can hold back for seconds); the swivel
 * starts once no gap between downloaded frames is wider than 4, and draws the nearest frame meanwhile.
 * Fluid and sharp (owner, 2026-10-29: "blurry and not fluid" on iPad, "low res" on iPhone): between two frames the
 * later one fades over the earlier at the fraction between them, so the turn never steps; the canvas draws at the
 * screen's density (up to 3, never more pixels than the frame has); the export is the narrowest whose crop is as
 * wide as the canvas in device pixels. Frames stay compressed once downloaded and decode around the one on screen,
 * within a shared memory budget (`decoded`), so high-resolution sequences fit in an iPhone's memory.
 * Safari: no requestIdleCallback (a timeout stands in), and each frame decodes through createImageBitmap where it
 * works, else through an <img> (older WebKit cannot make a bitmap from a WebP blob); a frame that fails to download
 * is retried once, and the nearest frame stands in for a lost one. Missing sequence (the feel's or the layout's not exported
 * yet), a layout the swivel does not play in (`media`), Save-Data, a quarter of the frames failing, or reduced motion
 * (on an iPhone, Settings > Accessibility > Motion > Reduce Motion): the canvas stays hidden and the still shows,
 * exactly as before.
 */

type Entry = {
  frames: number;
  w: number;
  h: number;
  crop: { x: number; y: number; w: number; h: number };
  widths: number[];
  hash: string;
  /** The frames' file type (default webp). */
  format?: string;
};
const manifest = generated as Record<string, Entry>;

type Frame = ImageBitmap | HTMLImageElement;
type Seq = {
  key: string;
  name: string;
  entry: Entry;
  width: number;
  /** The downloaded (still compressed) frames: decoded only around the frame on screen (`decoded`, below). */
  blobs: (Blob | null)[];
  /** Frames being decoded now. */
  decoding: Set<number>;
  /** Load order, coarse to fine, and how far through it the loader has started. */
  order: number[];
  next: number;
  inFlight: number;
  /** Frames that failed twice; past a quarter of the sequence the swivel gives up (the still stays). */
  lost: Set<number>;
  failed: boolean;
  ready: boolean;
  onChange: Set<() => void>;
  /** Cancels the downloads in flight when the visitor scrolls past (`lead`); their frames go back in the queue. */
  ctrl: AbortController;
  requeue: number[];
};

export type SwivelHandle = { progress: (p: number) => void };

/** Sequences downloaded on this page, kept across a visit to /reserve so Back finds them loaded. */
const cache = new Map<string, Seq>();
const CONCURRENCY = 3;
/** The swivel starts once no two downloaded frames are more than this many frames apart. */
const READY_GAP = 4;
/**
 * Decoded frames, shared by every swivel on the page, least recently drawn first out (2026-10-29). A decoded frame
 * is width x height x 4 bytes: a whole high-resolution sequence would take hundreds of MB, more than iOS Safari
 * allows a page, so only the frames around the one on screen stay decoded (on a phone, about 30 high-resolution frames).
 */
type Decoded = { frame: Frame; bytes: number; used: number; url?: string };
const decoded = new Map<string, Decoded>();
let decodedBytes = 0;
let budget = 0;
const decodedKey = (s: Seq, i: number) => `${s.key}#${i}`;
function decodeBudget() {
  if (!budget) budget = (window.matchMedia("(pointer: coarse)").matches ? 200 : 480) * 2 ** 20;
  return budget;
}
function dropDecoded(k: string) {
  const d = decoded.get(k);
  if (!d) return;
  if ("close" in d.frame) d.frame.close();
  if (d.url) URL.revokeObjectURL(d.url);
  decodedBytes -= d.bytes;
  decoded.delete(k);
}
function evict(keep: Set<string>) {
  if (decodedBytes <= decodeBudget()) return;
  const order = [...decoded.entries()].filter(([k]) => !keep.has(k)).sort((a, b) => a[1].used - b[1].used);
  for (const [k] of order) {
    if (decodedBytes <= decodeBudget()) break;
    dropDecoded(k);
  }
}

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

const frameUrl = (s: Seq, i: number) =>
  `/stills/seq/${s.name}/${String(i).padStart(3, "0")}-${s.width}.${s.entry.hash}.${s.entry.format ?? "webp"}`;

/** Whether createImageBitmap has decoded a WebP blob on this browser (null until the first frame tries). */
let bitmaps: boolean | null = null;

async function viaImage(url: string): Promise<HTMLImageElement> {
  const img = new Image();
  img.decoding = "async";
  img.src = url;
  // Safari can reject decode() for an image that loads fine (and older WebKit has no decode()): wait for load instead.
  if (typeof img.decode === "function") await img.decode().catch(() => (img.complete && img.naturalWidth ? undefined : loaded(img)));
  else await loaded(img);
  if (!img.naturalWidth) throw new Error("empty frame");
  return img;
}

function loaded(img: HTMLImageElement) {
  return new Promise<void>((resolve, reject) => {
    if (img.complete && img.naturalWidth) return resolve();
    img.addEventListener("load", () => resolve(), { once: true });
    img.addEventListener("error", () => reject(new Error("frame failed")), { once: true });
  });
}

async function download(url: string, signal: AbortSignal): Promise<Blob> {
  // Low priority: the frames are an enhancement and never come before the page's own images.
  const res = await fetch(url, { credentials: "same-origin", priority: "low", signal } as RequestInit);
  if (!res.ok) throw new Error(String(res.status));
  return res.blob();
}

/** A downloaded frame decoded: through createImageBitmap where it works, else through an <img> (older WebKit cannot
 * make a bitmap from a WebP blob; from then on every frame goes that way). */
async function decodeBlob(blob: Blob): Promise<{ frame: Frame; url?: string }> {
  if (bitmaps !== false && typeof createImageBitmap === "function") {
    try {
      const frame = await createImageBitmap(blob);
      bitmaps = true;
      return { frame };
    } catch (e) {
      // A bitmap that has worked before means this frame is broken; otherwise this browser cannot make one.
      if (bitmaps) throw e;
      bitmaps = false;
    }
  }
  const url = URL.createObjectURL(blob);
  try {
    return { frame: await viaImage(url), url };
  } catch (e) {
    URL.revokeObjectURL(url);
    throw e;
  }
}

function maxGap(s: Seq) {
  let gap = 0;
  let last = -1;
  s.blobs.forEach((f, i) => {
    // a lost frame counts as covered: its neighbours stand in for it
    if (!f && !s.lost.has(i)) return;
    if (last >= 0) gap = Math.max(gap, i - last);
    last = i;
  });
  return last === s.blobs.length - 1 && s.blobs[0] ? gap : Infinity;
}

/** Starts (or resumes) loading while the sequence is wanted; `active` says whether it still is. */
function pump(s: Seq, active: () => boolean) {
  while (!s.failed && active() && s.inFlight < CONCURRENCY && (s.requeue.length || s.next < s.order.length)) {
    const i = s.requeue.length ? s.requeue.shift()! : s.order[s.next++];
    s.inFlight++;
    const url = frameUrl(s, i);
    const { signal } = s.ctrl;
    // One retry, a moment later, for a frame lost to the network (a phone between cells); none for a cancelled one.
    download(url, signal)
      .catch((e) =>
        signal.aborted
          ? Promise.reject(e)
          : new Promise<Blob>((resolve, reject) => window.setTimeout(() => download(url, signal).then(resolve, reject), 800)),
      )
      .then(
        (blob) => {
          s.inFlight--;
          // Released (the other feel was picked) or failed meanwhile: drop it.
          if (s.failed) return;
          s.blobs[i] = blob;
          if (!s.ready && maxGap(s) <= READY_GAP) s.ready = true;
          s.onChange.forEach((f) => f());
          pump(s, active);
        },
        () => {
          s.inFlight--;
          if (s.failed) return;
          // Cancelled because the visitor scrolled past: not lost, it loads again when the still comes back near.
          if (signal.aborted) {
            s.requeue.push(i);
            return;
          }
          lose(s, i);
          pump(s, active);
        },
      );
  }
}

/** A lost frame: its neighbours stand in (maxGap skips it). Too many lost, or an end frame, and the still stays. */
function lose(s: Seq, i: number) {
  s.blobs[i] = null;
  s.lost.add(i);
  if (s.lost.size > s.blobs.length / 4 || i === 0 || i === s.blobs.length - 1) s.failed = true;
  else if (!s.ready && maxGap(s) <= READY_GAP) s.ready = true;
  s.onChange.forEach((f) => f());
}

/** Frame i decoded, or null while it decodes (it starts decoding now if it has downloaded). */
function decodedFrame(s: Seq, i: number, now: number): Frame | null {
  const k = decodedKey(s, i);
  const d = decoded.get(k);
  if (d) {
    d.used = now;
    return d.frame;
  }
  const blob = s.blobs[i];
  if (!blob || s.decoding.has(i) || s.failed) return null;
  s.decoding.add(i);
  decodeBlob(blob).then(
    ({ frame, url }) => {
      s.decoding.delete(i);
      if (s.failed || cache.get(s.key) !== s) {
        if ("close" in frame) frame.close();
        if (url) URL.revokeObjectURL(url);
        return;
      }
      const w = "naturalWidth" in frame ? frame.naturalWidth : frame.width;
      const h = "naturalHeight" in frame ? frame.naturalHeight : frame.height;
      decoded.set(k, { frame, bytes: w * h * 4, used: performance.now(), url });
      decodedBytes += w * h * 4;
      s.onChange.forEach((f) => f());
    },
    () => {
      s.decoding.delete(i);
      if (!s.failed) lose(s, i);
    },
  );
  return null;
}

/** The downloaded frame nearest to i (a lost or late frame's neighbour stands in), or -1. */
function nearestLoaded(s: Seq, i: number) {
  for (let d = 0; d < s.blobs.length; d++) {
    if (s.blobs[i - d]) return i - d;
    if (s.blobs[i + d]) return i + d;
  }
  return -1;
}

/** The decoded frame nearest to f, or -1. */
function nearestDecoded(s: Seq, f: number) {
  const n = s.blobs.length;
  const c = Math.round(f);
  for (let d = 0; d < n; d++) {
    if (c - d >= 0 && decoded.has(decodedKey(s, c - d))) return c - d;
    if (c + d < n && decoded.has(decodedKey(s, c + d))) return c + d;
  }
  return -1;
}

function release(s: Seq) {
  s.failed = true;
  for (let i = 0; i < s.blobs.length; i++) dropDecoded(decodedKey(s, i));
  s.blobs.fill(null);
  cache.delete(s.key);
}

/** Percentages of object-position ("50% 100%"); anything else counts as centred. */
function objectPosition(img: HTMLImageElement | null) {
  const parts = (img ? getComputedStyle(img).objectPosition : "").split(/\s+/);
  const pct = (v: string | undefined) => (v && v.endsWith("%") ? parseFloat(v) / 100 : 0.5);
  return [pct(parts[0]), pct(parts[1])] as const;
}

type Props = {
  ref?: Ref<SwivelHandle>;
  /** The sequences' common name: `<sequence>-<feel>-desktop|phone`, e.g. "K01-swivel". */
  sequence: string;
  /** Where the phone sequence (the still's phone master) applies: the same query as the still's phoneMedia. */
  portraitQuery: string;
  /** Where the swivel plays at all (omitted: everywhere); elsewhere the still shows alone and nothing loads. */
  media?: string;
  /**
   * Load only while the still is within this many screens of the viewport (and after the load triggers), so a swivel
   * further down the page never takes a slow phone's bandwidth from the images around the visitor. Omitted: at once,
   * whatever the scroll position (the hero's).
   */
  lead?: number;
  className?: string;
};

export function Swivel({ ref, sequence, portraitQuery, media, lead, className }: Props) {
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
    const playing = media ? window.matchMedia(media) : null;
    const ctx = canvas.getContext("2d", { alpha: false });
    if (!ctx) return;

    let seq: Seq | null = null;
    let started = false;
    let alive = true;
    /** What the canvas holds now ("i:j:alpha"), so an unchanged scroll position draws nothing. */
    let drawn = "";
    let on = false;
    let raf = 0;
    /** The canvas's place over the still, in CSS px, and its backing size. */
    let laidOut = false;

    const show = (v: boolean) => {
      if (v === on) return;
      on = v;
      canvas.dataset.on = String(v);
    };

    /** The device pixel ratio the swivel draws at: the screen's, up to 3 (an iPhone). */
    const density = () => Math.min(window.devicePixelRatio || 1, 3);
    /** The width the canvas's crop is drawn at on screen, in device px, for this sequence (cover, as the still). */
    const drawnCropWidth = (entry: Entry) =>
      Math.max(box.clientWidth / entry.w, box.clientHeight / entry.h) * entry.crop.w * density();
    /** The narrowest export whose crop is at least as wide as it is drawn (within 8%), else the widest. */
    const widthFor = (entry: Entry) => {
      const need = drawnCropWidth(entry);
      return entry.widths.find((w) => (entry.crop.w * w) / entry.w * 1.08 >= need) ?? entry.widths[entry.widths.length - 1];
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
      const dpr = density();
      const snap = (v: number) => Math.round(v * dpr) / dpr;
      const left = snap(ox + entry.crop.x * scale);
      const top = snap(oy + entry.crop.y * scale);
      const right = snap(ox + (entry.crop.x + entry.crop.w) * scale);
      const bottom = snap(oy + (entry.crop.y + entry.crop.h) * scale);
      Object.assign(canvas.style, { left: `${left}px`, top: `${top}px`, width: `${right - left}px`, height: `${bottom - top}px` });
      // The backing store at the screen's density, but never more pixels than the frame has (a frame drawn larger than
      // it was exported gains nothing from a bigger canvas, and a 2000 px canvas at 2x is 32 MB on an iPad).
      const frameW = (entry.crop.w * seq.width) / entry.w;
      const k = Math.max(1, Math.min(dpr, frameW / (right - left)));
      const cw = Math.round((right - left) * k);
      const ch = Math.round((bottom - top) * k);
      if (canvas.width !== cw || canvas.height !== ch) {
        canvas.width = cw;
        canvas.height = ch;
        drawn = "";
      }
      laidOut = true;
    };

    const draw = () => {
      raf = 0;
      if (!alive) return;
      const s = seq;
      const n = s ? s.entry.frames : 0;
      const f = s ? Math.min(1, Math.max(0, progress.current)) * (n - 1) : 0;
      // Frame 0 is the still: the canvas shows only once the racket has begun to turn.
      if (!s || !s.ready || s.failed || f < 0.01) return show(false);
      if (!laidOut) layout();
      if (!canvas.width) return show(false);
      // Between two frames, the later one fades over the earlier one at the fraction between them (2026-10-29), so
      // the turn never steps, however few frames there are. A frame still downloading: its nearest neighbour stands in.
      const i0 = Math.min(n - 2, Math.floor(f));
      const a = nearestLoaded(s, i0);
      const b = nearestLoaded(s, i0 + 1);
      if (a < 0) return show(false);
      const t = a === b ? 0 : Math.round((f - i0) * 64) / 64;
      const now = performance.now();
      const fa = decodedFrame(s, a, now);
      const fb = t > 0 ? decodedFrame(s, b, now) : null;
      // Decode ahead and behind, so the frames on either side are ready before the scroll reaches them.
      for (let d = -2; d <= 3; d++) if (i0 + d >= 0 && i0 + d < n && s.blobs[i0 + d]) decodedFrame(s, i0 + d, now - 1);
      let key: string;
      if (fa && (t === 0 || fb)) {
        key = `${a}:${b}:${t}`;
        if (key !== drawn) {
          ctx.imageSmoothingEnabled = true;
          ctx.imageSmoothingQuality = "high";
          ctx.globalAlpha = 1;
          ctx.drawImage(fa, 0, 0, canvas.width, canvas.height);
          if (fb && t > 0) {
            ctx.globalAlpha = t;
            ctx.drawImage(fb, 0, 0, canvas.width, canvas.height);
            ctx.globalAlpha = 1;
          }
        }
      } else {
        // Still decoding: the nearest decoded frame meanwhile (the decode's onChange redraws).
        const j = nearestDecoded(s, f);
        if (j < 0) return show(!!drawn && on);
        key = `${j}:${j}:0`;
        if (key !== drawn) {
          ctx.globalAlpha = 1;
          ctx.drawImage(decoded.get(decodedKey(s, j))!.frame, 0, 0, canvas.width, canvas.height);
        }
      }
      drawn = key;
      evict(new Set([decodedKey(s, a), decodedKey(s, b)]));
      show(true);
    };
    // Scroll updates arrive on GSAP's ticker; loads arrive any time: either way, at most one draw a frame.
    const schedule = () => {
      if (!raf) raf = requestAnimationFrame(draw);
    };
    redraw.current = schedule;

    const pick = () => {
      // Outside `media` no sequence plays (and none loads): the still shows alone.
      const name = playing && !playing.matches ? "" : `${sequence}-${feel}-${portrait.matches ? "phone" : "desktop"}`;
      const entry = name ? manifest[name] : undefined;
      // The export by the canvas's real size on screen (2026-10-29): a tablet's portrait canvas at 2x, an iPhone's at 3x.
      const width = entry && box.clientWidth ? widthFor(entry) : 0;
      if (seq && seq.name === name && (seq.width === width || !width)) return;
      // The other layout (a turned tablet): hide, then load this one; the other's frames go once this one exists.
      seq?.onChange.delete(schedule);
      seq = null;
      drawn = "";
      laidOut = false;
      show(false);
      if (!entry) return;
      const key = `${name}@${width || entry.widths[0]}`;
      // Only this swivel's other sequences (another feel, layout or width): another swivel on the page keeps its own.
      for (const s of cache.values()) if (s.key !== key && s.name.startsWith(`${sequence}-`)) release(s);
      let s = cache.get(key);
      if (!s) {
        s = { key, name, entry, width: width || entry.widths[0], blobs: Array(entry.frames).fill(null), decoding: new Set(), order: loadOrder(entry.frames), next: 0, inFlight: 0, lost: new Set(), failed: false, ready: false, onChange: new Set(), ctrl: new AbortController(), requeue: [] };
        cache.set(key, s);
      }
      seq = s;
      s.onChange.add(schedule);
      if (started) pump(s, () => alive && seq === s && near);
      schedule();
    };

    // `lead`: the load triggers below only arm the start; the still coming near fires it (and vice versa).
    let armed = false;
    let near = lead === undefined;
    const start = () => {
      armed = true;
      if (!alive || started || !near) return;
      started = true;
      const s = seq;
      if (s) pump(s, () => alive && seq === s && near);
    };
    pick();
    // After the load event (the hero's stills are in), when the main thread is idle: never ahead of the LCP. But never
    // later than the visitor's first scroll or touch, or 1.5 s after mount: Safari's load event waits for every eager
    // resource, in-app browsers (Telegram, Instagram, Claude) can hold it back for seconds, and a visitor who scrolls at
    // once would otherwise pass the whole turn before a frame exists. Safari has no requestIdleCallback.
    let idle = 0;
    const later = () => {
      idle = window.requestIdleCallback ? window.requestIdleCallback(start, { timeout: 1000 }) : window.setTimeout(start, 200);
    };
    if (document.readyState === "complete") later();
    else window.addEventListener("load", later, { once: true });
    const intent = { once: true, passive: true } as const;
    window.addEventListener("scroll", start, intent);
    window.addEventListener("touchstart", start, intent);
    const fallback = window.setTimeout(start, 1500);
    const nearby =
      lead === undefined
        ? null
        : new IntersectionObserver(
            (entries) => {
              // Loads only while the still is near: a visitor who has scrolled on past it pauses its frames (the
              // ones in flight finish), so the images where they are now come first; coming back resumes them.
              near = entries[entries.length - 1].isIntersecting;
              if (!near) {
                // Cancel the frames in flight too, so the images the visitor is scrolling towards get the bandwidth.
                if (seq && seq.inFlight) {
                  seq.ctrl.abort();
                  seq.ctrl = new AbortController();
                }
                return;
              }
              if (!started) {
                if (armed) start();
              } else if (seq) {
                const s = seq;
                pump(s, () => alive && seq === s && near);
              }
            },
            { rootMargin: `${Math.round(lead * 100)}% 0px` },
          );
    nearby?.observe(box);

    const resize = new ResizeObserver(() => {
      // A size that needs another export (a turned iPad, a window made larger) loads that one; a smaller one keeps
      // the frames it has.
      if (seq && box.clientWidth && widthFor(seq.entry) > seq.width) pick();
      laidOut = false;
      layout();
      schedule();
    });
    resize.observe(box);
    portrait.addEventListener("change", pick);
    playing?.addEventListener("change", pick);

    return () => {
      alive = false;
      cancelAnimationFrame(raf);
      if (window.cancelIdleCallback) window.cancelIdleCallback(idle);
      window.clearTimeout(idle);
      window.removeEventListener("load", later);
      window.removeEventListener("scroll", start);
      window.removeEventListener("touchstart", start);
      window.clearTimeout(fallback);
      nearby?.disconnect();
      resize.disconnect();
      portrait.removeEventListener("change", pick);
      playing?.removeEventListener("change", pick);
      redraw.current = () => {};
      // The frames stay decoded for Back (a half-loaded sequence resumes where it stopped); a change of feel releases
      // them once the other feel's sequence is picked.
      seq?.onChange.delete(schedule);
      show(false);
    };
  }, [motionOn, feel, sequence, portraitQuery, media, lead]);

  return <canvas ref={canvasRef} className={className} aria-hidden="true" data-on="false" />;
}

/** Whether any sequence of this swivel is exported (`<sequence>-<feel>-<layout>`). */
export function hasSequence(sequence: string) {
  return Object.keys(manifest).some((k) => k.startsWith(`${sequence}-`));
}
