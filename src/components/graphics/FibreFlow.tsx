"use client";

import { useEffect, useRef } from "react";
import { useMotion } from "@/components/motion/MotionProvider";
import {
  FRAMES,
  buildFlowField,
  createFlowBuilder,
  linesToPath,
  prng,
  type FlowField,
  type FlowLine,
  type FrameName,
  type Rect,
} from "@/lib/graphics-fibreflow";
import styles from "./FibreFlow.module.css";

/** Strings this graphic adds (none of them are claims beyond holes.* in copy.ts). */
export const LABELS = {
  summary:
    "Fibre flow around the 42 moulded holes: thousands of carbon filaments part around every hole and rejoin behind it, so not one is cut.",
};

type Mode = "full" | "strip";

type Props = {
  className?: string;
  /** "full" fills its parent (the Holes band); "strip" is the 390 x 260 phone strip. */
  mode?: Mode;
  /** Flow direction in degrees: 0 runs along +x (the K04 weave), positive turns up the face. */
  angle?: number;
  /** Which part of the hole field to frame: a named framing or a world rect [x0, y0, x1, y1]. */
  frame?: FrameName | Rect;
  /** Fade the field away under a text block on this side. */
  fadeSide?: "left" | "right" | "none";
  /** Where the framed holes sit in the box, as fractions (defaults follow fadeSide). */
  focus?: [number, number];
  /** Line density: 1 is about 900 lines on a 2560 x 1440 band; 0.5 halves it. */
  density?: number;
  /** Draw one static frame even when motion is allowed. */
  still?: boolean;
  /** Hide from assistive tech (when the parent already describes the picture). */
  decorative?: boolean;
};

type Rgb = [number, number, number];
type Comet = { line: FlowLine; s: number; len: number; v: number; group: number; peak: number };
type Engine = { field: FlowField; comets: Comet[] };

const FPS_GAP = 1000 / 30 - 2;
/** About 0.2 px per frame at 30 fps, scaled by the local flow speed. */
const BASE_SPEED = 0.2 / (1000 / 30);
const PULSE_STEPS = 9;

function hexToRgb(v: string, fallback: Rgb): Rgb {
  const m = /^#?([0-9a-f]{6})$/i.exec(v.trim());
  if (!m) return fallback;
  const n = parseInt(m[1], 16);
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
}
const rgba = ([r, g, b]: Rgb, a: number) => `rgba(${r},${g},${b},${a.toFixed(3)})`;

/** Layout for each mode: framing, fit and line spacing (CSS px). */
function layout(mode: Mode, w: number, h: number, frame: Props["frame"], fadeSide: Props["fadeSide"], focus: Props["focus"], density: number, angle: number) {
  const rect: Rect = Array.isArray(frame) ? frame : FRAMES[frame ?? (mode === "strip" ? "strip" : "field")];
  const defFocus: [number, number] =
    mode === "strip" ? [0.5, 0.5] : fadeSide === "left" ? [0.72, 0.5] : fadeSide === "right" ? [0.28, 0.5] : [0.5, 0.5];
  // About 900 lines across a 2560 x 1440 band; never denser than 1.4 px.
  const base = mode === "strip" ? 2.2 : Math.max(1.5, Math.min(2.4, h / 900 + 0.5));
  return {
    width: w,
    height: h,
    angle,
    frame: rect,
    fit: mode === "strip" ? ("cover" as const) : ("contain" as const),
    fitW: mode === "strip" ? 1 : fadeSide === "none" ? 0.9 : 0.5,
    fitH: mode === "strip" ? 1 : 0.88,
    focus: focus ?? defFocus,
    spacing: base / Math.max(0.2, density),
    tow: mode === "strip" ? 6 : 7,
    maxLines: Math.round(1000 * Math.max(0.2, density)),
    maxStep: mode === "strip" ? 4 : 6,
  };
}

/**
 * G05, the fibre flow field. Streamlines of potential flow around the real 42-hole pattern
 * (racket-shape.ts): every filament parts around each hole and rejoins, as the moulded carbon
 * does. Drawn on two canvases (static lines and rings, then slow comets that advect along the
 * lines), capped at 30 fps, paused off-screen and when the tab is hidden, DPR capped at 2.
 * Reduced motion draws one static frame. Without JavaScript a light SVG of the same field shows.
 */
export function FibreFlow({
  className,
  mode = "full",
  angle = 0,
  frame,
  fadeSide = "none",
  focus,
  density = 1,
  still = false,
  decorative = false,
}: Props) {
  const root = useRef<HTMLDivElement>(null);
  const baseRef = useRef<HTMLCanvasElement>(null);
  const liveRef = useRef<HTMLCanvasElement>(null);
  const { motionOn } = useMotion();
  const animate = motionOn && !still;
  const animateRef = useRef(animate);
  const syncRef = useRef<() => void>(() => {});

  const frameKey = Array.isArray(frame) ? frame.join(",") : (frame ?? "");
  const focusKey = focus ? focus.join(",") : "";

  useEffect(() => {
    const el = root.current;
    const baseCv = baseRef.current;
    const liveCv = liveRef.current;
    if (!el || !baseCv || !liveCv) return;
    const bctx = baseCv.getContext("2d");
    const lctx = liveCv.getContext("2d");
    if (!bctx || !lctx) return;

    const css = getComputedStyle(el);
    const amber = hexToRgb(css.getPropertyValue("--amber"), [227, 164, 103]);
    const hot = hexToRgb(css.getPropertyValue("--amber-hot"), [255, 226, 191]);
    const steel = hexToRgb(css.getPropertyValue("--steel"), [201, 204, 209]);
    const dark = hexToRgb(css.getPropertyValue("--void"), [6, 6, 7]);

    let engine: Engine | null = null;
    let dpr = 1;
    let size = { w: 0, h: 0 };
    /** Within reach (build ahead of time) and actually on screen (run the loop). */
    let near = false;
    let visible = false;
    let raf = 0;
    let last = 0;
    let building: { cancel: () => void } | null = null;
    let resizeTimer = 0;
    const frameRect: Rect | FrameName | undefined = frame;

    // ---------- drawing ----------
    // Hairlines thicken a little on wide screens so the field keeps its weight at 2560.
    const lineW = mode === "strip" ? 0.7 : Math.max(0.6, Math.min(0.9, 0.6 + ((el.clientWidth - 1440) / 1120) * 0.3));

    // Light: brightest over the framed holes, falling away to a floor (radial, elliptical).
    const LIGHT: [number, number][] =
      mode === "strip"
        ? [
            [0, 1],
            [0.7, 0.85],
            [1, 0.6],
          ]
        : [
            [0, 1],
            [0.45, 0.9],
            [0.8, 0.55],
            [1.15, 0.3],
            [1.6, 0.2],
          ];
    const lightGeo = (f: FlowField) => {
      const [x0, y0, x1, y1] = f.frameBox;
      return { cx: (x0 + x1) / 2, cy: (y0 + y1) / 2, rx: ((x1 - x0) / 2) * 1.15, ry: ((y1 - y0) / 2) * 1.12 };
    };
    const lightAt = (t: number) => {
      if (t <= 0) return LIGHT[0][1];
      for (let k = 1; k < LIGHT.length; k++) {
        if (t <= LIGHT[k][0]) {
          const [t0, v0] = LIGHT[k - 1];
          const [t1, v1] = LIGHT[k];
          return v0 + ((v1 - v0) * (t - t0)) / (t1 - t0);
        }
      }
      return LIGHT[LIGHT.length - 1][1];
    };

    // Fades are baked into the drawing (a CSS mask would re-composite the whole band every frame):
    // the edges of the band, and the side under a text block.
    const EDGE = mode === "strip" ? 0.1 : 0.09;
    const SIDE: [number, number][] = [
      [0, 0.04],
      [0.2, 0.1],
      [0.38, 0.42],
      [0.58, 1],
    ];
    const ramp = (stops: [number, number][], t: number) => {
      if (t <= stops[0][0]) return stops[0][1];
      for (let k = 1; k < stops.length; k++) {
        if (t <= stops[k][0]) {
          const [t0, v0] = stops[k - 1];
          const [t1, v1] = stops[k];
          return v0 + ((v1 - v0) * (t - t0)) / (t1 - t0);
        }
      }
      return stops[stops.length - 1][1];
    };
    const fadeAt = (x: number, y: number, w: number, h: number) => {
      const ty = y / h;
      const edge = Math.min(1, Math.max(0, Math.min(ty, 1 - ty) / EDGE));
      if (fadeSide === "none") return edge;
      const tx = fadeSide === "left" ? x / w : 1 - x / w;
      return edge * ramp(SIDE, tx);
    };
    // destination-out is a bounded operation (unlike destination-in, which clears everything outside
    // the shape), so each fade only touches its own strip: alpha is cut by (1 - fade).
    function applyFades(ctx: CanvasRenderingContext2D, w: number, h: number) {
      ctx.save();
      ctx.globalCompositeOperation = "destination-out";
      const eh = h * EDGE;
      const top = ctx.createLinearGradient(0, 0, 0, eh);
      top.addColorStop(0, "#000");
      top.addColorStop(1, "rgba(0,0,0,0)");
      ctx.fillStyle = top;
      ctx.fillRect(0, 0, w, eh);
      const bottom = ctx.createLinearGradient(0, h, 0, h - eh);
      bottom.addColorStop(0, "#000");
      bottom.addColorStop(1, "rgba(0,0,0,0)");
      ctx.fillStyle = bottom;
      ctx.fillRect(0, h - eh, w, eh);
      if (fadeSide !== "none") {
        const sw = w * SIDE[SIDE.length - 1][0];
        const left = fadeSide === "left";
        const gs = left ? ctx.createLinearGradient(0, 0, sw, 0) : ctx.createLinearGradient(w, 0, w - sw, 0);
        for (const [t, v] of SIDE) gs.addColorStop(t / SIDE[SIDE.length - 1][0], `rgba(0,0,0,${1 - v})`);
        ctx.fillStyle = gs;
        ctx.fillRect(left ? 0 : w - sw, 0, sw, h);
      }
      ctx.restore();
    }

    /**
     * Draws the static field into `ctx` (an offscreen canvas), yielding between stages so each
     * frame only rasterises part of it; the result is blitted to the visible canvas in one go.
     */
    const glowK = Math.max(1, Math.min(1.6, el.clientWidth / 1440));
    const GLOW: [number, number][] = [
      [9 * glowK, 0.035],
      [5.5 * glowK, 0.06],
      [3 * glowK, 0.1],
    ];

    function* drawBase(f: FlowField, ctx: CanvasRenderingContext2D) {
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.lineJoin = "round";
      ctx.lineCap = "round";

      // Filaments, batched by opacity so the whole field is a dozen strokes.
      const buckets = 12;
      const groups: FlowLine[][] = Array.from({ length: buckets }, () => []);
      const hotLines: FlowLine[] = [];
      for (const l of f.lines) {
        if (l.hot) hotLines.push(l);
        else groups[Math.min(buckets - 1, Math.floor(l.alpha * buckets))].push(l);
      }
      const trace = (ls: FlowLine[]) => {
        ctx.beginPath();
        for (const l of ls) {
          const p = l.pts;
          ctx.moveTo(p[0], p[1]);
          for (let k = 2; k < p.length; k += 2) ctx.lineTo(p[k], p[k + 1]);
        }
      };
      ctx.lineWidth = lineW;
      const [aLo, aHi] = mode === "strip" ? [0.12, 0.8] : [0.08, 0.78];
      for (let b = 0; b < buckets; b++) {
        if (!groups[b].length) continue;
        trace(groups[b]);
        ctx.strokeStyle = rgba(amber, aLo + (aHi - aLo) * ((b + 0.5) / buckets));
        ctx.stroke();
        if (b % 3 === 2) yield;
      }
      // Hot filaments: a pre-blurred glow underneath, built from stacked wide, faint strokes
      // (a canvas shadow or filter blur over the whole band costs ~100 ms to rasterise), then the core.
      if (hotLines.length) {
        trace(hotLines);
        for (const [wd, a] of GLOW) {
          ctx.strokeStyle = rgba(amber, a);
          ctx.lineWidth = wd;
          ctx.stroke();
        }
        ctx.strokeStyle = rgba(hot, 0.8);
        ctx.lineWidth = lineW + 0.2;
        ctx.stroke();
      }

      yield;
      // Light falloff, applied to the lines only (the rings stay crisp everywhere).
      const L = lightGeo(f);
      ctx.save();
      ctx.globalCompositeOperation = "destination-out";
      ctx.translate(L.cx, L.cy);
      ctx.scale(L.rx, L.ry);
      const reach = LIGHT[LIGHT.length - 1][0];
      const g = ctx.createRadialGradient(0, 0, 0, 0, 0, reach);
      for (const [t, v] of LIGHT) g.addColorStop(t / reach, `rgba(0,0,0,${1 - v})`);
      ctx.fillStyle = g;
      const big = (Math.max(f.width, f.height) * 4) / Math.min(L.rx, L.ry);
      ctx.fillRect(-big, -big, big * 2, big * 2);
      ctx.restore();

      yield;
      // Bores, drawn as G06 draws a moulded hole: cleared, a throat that darkens with depth, an
      // amber rim light outside, a crisp rim and wall lines that tighten down the bore.
      const r = f.holeR;
      const h = f.holes;
      const circles = (rr: number) => {
        ctx.beginPath();
        for (let k = 0; k < h.length; k += 2) {
          ctx.moveTo(h[k] + rr, h[k + 1]);
          ctx.arc(h[k], h[k + 1], rr, 0, Math.PI * 2);
        }
      };
      ctx.save();
      ctx.globalCompositeOperation = "destination-out";
      circles(r * 1.02);
      ctx.fill();
      ctx.restore();
      for (let k = 0; k < h.length; k += 2) {
        const rg = ctx.createRadialGradient(h[k], h[k + 1], 0, h[k], h[k + 1], r);
        rg.addColorStop(0, rgba(dark, 0.62));
        rg.addColorStop(0.7, rgba(dark, 0.5));
        rg.addColorStop(1, rgba(dark, 0.22));
        ctx.fillStyle = rg;
        ctx.beginPath();
        ctx.arc(h[k], h[k + 1], r, 0, Math.PI * 2);
        ctx.fill();
      }
      // Amber rim light: the same stacked-stroke glow, hugging the outside of each bore.
      for (const [wd, a] of GLOW) {
        circles(r * 1.02 + wd / 2);
        ctx.strokeStyle = rgba(amber, a * 0.8);
        ctx.lineWidth = wd;
        ctx.stroke();
      }
      // Wall lines: spacing and brightness fall away with depth (the G06 moulded wall in miniature).
      const wallW = Math.max(0.6, lineW);
      for (const [k, a] of [
        [0.9, 0.42],
        [0.82, 0.26],
        [0.765, 0.15],
      ] as const) {
        circles(r * k);
        ctx.strokeStyle = rgba(amber, a);
        ctx.lineWidth = wallW;
        ctx.stroke();
      }
      circles(r);
      ctx.strokeStyle = rgba(steel, 0.72);
      ctx.lineWidth = Math.max(1, lineW + 0.25);
      ctx.stroke();
      applyFades(ctx, f.width, f.height);
    }

    // Light pulses ride the lines: a soft rise and fall in PULSE_STEPS pieces, batched by level.
    const LEVELS = 6;

    function seg(ctx: CanvasRenderingContext2D, l: FlowLine, s0: number, s1: number) {
      const L = l.len;
      const n = L.length;
      if (s1 <= 0 || s0 >= L[n - 1]) return;
      s0 = Math.max(0, s0);
      s1 = Math.min(L[n - 1], s1);
      let lo = 0;
      let hi = n - 1;
      while (lo < hi) {
        const mid = (lo + hi) >> 1;
        if (L[mid] < s0) lo = mid + 1;
        else hi = mid;
      }
      const p = l.pts;
      const at = (sv: number, i: number): [number, number] => {
        const i0 = Math.max(0, i - 1);
        const span = L[i] - L[i0] || 1;
        const t = Math.min(1, Math.max(0, (sv - L[i0]) / span));
        return [p[2 * i0] + (p[2 * i] - p[2 * i0]) * t, p[2 * i0 + 1] + (p[2 * i + 1] - p[2 * i0 + 1]) * t];
      };
      const [x0, y0] = at(s0, lo);
      ctx.moveTo(x0, y0);
      let i = lo;
      while (i < n && L[i] < s1) {
        ctx.lineTo(p[2 * i], p[2 * i + 1]);
        i++;
      }
      const [x1, y1] = at(s1, Math.min(n - 1, i));
      ctx.lineTo(x1, y1);
    }

    /** The point at arc length sv, interpolated (straight runs keep only their end points). */
    function pointAt(l: FlowLine, sv: number): [number, number] {
      const L = l.len;
      const n = L.length;
      let lo = 0;
      let hi = n - 1;
      while (lo < hi) {
        const mid = (lo + hi) >> 1;
        if (L[mid] < sv) lo = mid + 1;
        else hi = mid;
      }
      const i0 = Math.max(0, lo - 1);
      const span = L[lo] - L[i0] || 1;
      const t = Math.min(1, Math.max(0, (sv - L[i0]) / span));
      const p = l.pts;
      return [p[2 * i0] + (p[2 * lo] - p[2 * i0]) * t, p[2 * i0 + 1] + (p[2 * lo + 1] - p[2 * i0 + 1]) * t];
    }

    // Reused per frame: pieces bucketed by [colour][level].
    const buckets: Comet[][][] = [0, 1].map(() => Array.from({ length: LEVELS + 1 }, () => []));
    const pieceOf: number[][][] = [0, 1].map(() => Array.from({ length: LEVELS + 1 }, () => []));

    function drawLive() {
      const ctx = lctx!;
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.clearRect(0, 0, liveCv!.width, liveCv!.height);
      if (!engine) return;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.lineCap = "round";
      ctx.lineJoin = "round";
      const Lg = lightGeo(engine.field);
      for (const col of [0, 1]) for (let v = 0; v <= LEVELS; v++) {
        buckets[col][v].length = 0;
        pieceOf[col][v].length = 0;
      }
      for (const c of engine.comets) {
        const [hx, hy] = pointAt(c.line, c.s - c.len / 2);
        const t = Math.hypot((hx - Lg.cx) / Lg.rx, (hy - Lg.cy) / Lg.ry);
        // Pulses fade much faster than the lines away from the light and towards the edges, so the
        // dim fringe never shows a lone bright dash (it read as a scratch at 2560).
        const lt = lightAt(t);
        const fd = fadeAt(hx, hy, engine.field.width, engine.field.height);
        const peak = c.peak * lt * lt * lt * fd * fd;
        const col = c.group === 3 ? 1 : 0;
        for (let k = 0; k < PULSE_STEPS; k++) {
          const w = Math.pow(Math.sin((Math.PI * (k + 0.5)) / PULSE_STEPS), 1.6);
          const lv = Math.min(LEVELS, Math.round(peak * w * LEVELS));
          if (lv <= 0) continue;
          buckets[col][lv].push(c);
          pieceOf[col][lv].push(k);
        }
      }
      for (const col of [0, 1]) {
        ctx.lineWidth = col ? lineW + 0.35 : lineW + 0.2;
        for (let v = 1; v <= LEVELS; v++) {
          const list = buckets[col][v];
          if (!list.length) continue;
          ctx.beginPath();
          const ks = pieceOf[col][v];
          for (let j = 0; j < list.length; j++) {
            const c = list[j];
            const a = c.s - c.len + (c.len * ks[j]) / PULSE_STEPS;
            seg(ctx, c.line, a, a + c.len / PULSE_STEPS + 0.4);
          }
          ctx.strokeStyle = rgba(col ? hot : amber, v / LEVELS);
          ctx.stroke();
        }
      }
    }

    function advance(dt: number) {
      if (!engine) return;
      for (const c of engine.comets) {
        const L = c.line.len;
        const n = L.length;
        let lo = 0;
        let hi = n - 1;
        const mid0 = c.s - c.len / 2;
        while (lo < hi) {
          const mid = (lo + hi) >> 1;
          if (L[mid] < mid0) lo = mid + 1;
          else hi = mid;
        }
        const sp = c.line.speed[Math.min(n - 1, lo)] || 1;
        c.s += dt * BASE_SPEED * c.v * Math.min(2.2, Math.max(0.35, sp));
        if (c.s - c.len > L[n - 1]) c.s = 0;
      }
    }

    function makeComets(f: FlowField): Comet[] {
      const rnd = prng(7);
      const comets: Comet[] = [];
      const k = Math.max(0.6, Math.min(1.7, f.width / 1440));
      for (const line of f.lines) {
        const total = line.len[line.len.length - 1];
        if (total < 60) continue;
        const count = rnd() < 0.36 ? 1 : rnd() < 0.08 ? 2 : 0;
        for (let i = 0; i < count; i++) {
          const g = line.hot || rnd() < 0.06 ? 3 : 0;
          comets.push({
            line,
            s: rnd() * (total + 200),
            len: (90 + rnd() * 220) * k * (mode === "strip" ? 0.55 : 1),
            v: 0.75 + rnd() * 0.5,
            group: g,
            peak: g === 3 ? 0.85 + rnd() * 0.15 : 0.32 + rnd() * 0.36,
          });
        }
      }
      return comets;
    }

    // ---------- loop ----------
    const tick = (now: number) => {
      raf = requestAnimationFrame(tick);
      if (now - last < FPS_GAP) return;
      const dt = Math.min(100, now - last);
      last = now;
      advance(dt);
      drawLive();
    };
    const stop = () => {
      if (raf) cancelAnimationFrame(raf);
      raf = 0;
    };
    const sync = () => {
      const run = animateRef.current && visible && !document.hidden && !!engine;
      if (run && !raf) {
        last = performance.now();
        raf = requestAnimationFrame(tick);
      } else if (!run && raf) {
        stop();
      }
      if (!animateRef.current && engine) drawLive();
    };
    syncRef.current = sync;

    // ---------- building (in idle slices, never one long task) ----------
    function build() {
      building?.cancel();
      const w = Math.round(el!.clientWidth);
      const h = Math.round(el!.clientHeight);
      if (w < 8 || h < 8) return;
      size = { w, h };
      dpr = Math.min(2, window.devicePixelRatio || 1);
      const b = createFlowBuilder(layout(mode, w, h, frameRect, fadeSide, focus, density, angle));
      let cancelled = false;
      let handle = 0;
      let frame = 0;
      // Safari has no requestIdleCallback: fall back to short timeouts.
      const idle = typeof window.requestIdleCallback === "function";
      const schedule = (fn: () => void) =>
        (handle = idle ? window.requestIdleCallback(fn, { timeout: 120 }) : window.setTimeout(fn, 16));
      const slice = () => {
        if (cancelled) return;
        const t0 = performance.now();
        let more = true;
        while (more && performance.now() - t0 < 9) more = b.step();
        if (more) {
          schedule(slice);
          return;
        }
        // Draw the static field over a few frames, so no single frame rasterises all of it. The
        // first time, straight into the (still hidden) canvas; on a rebuild, offscreen and then one
        // blit, so the old field stays up until the new one is complete.
        const first = !engine;
        const pw = Math.round(w * dpr);
        const ph = Math.round(h * dpr);
        let off: HTMLCanvasElement | null = null;
        if (first) {
          for (const cv of [baseCv!, liveCv!]) {
            cv.width = pw;
            cv.height = ph;
          }
        } else {
          off = document.createElement("canvas");
          off.width = pw;
          off.height = ph;
        }
        const tctx = off ? off.getContext("2d") : bctx;
        if (!tctx) return;
        const stages = drawBase(b.field, tctx);
        const stage = () => {
          if (cancelled) return;
          if (!stages.next().done) {
            frame = requestAnimationFrame(stage);
            return;
          }
          building = null;
          if (off) {
            for (const cv of [baseCv!, liveCv!]) {
              cv.width = pw;
              cv.height = ph;
            }
            bctx!.drawImage(off, 0, 0);
          }
          engine = { field: b.field, comets: makeComets(b.field) };
          drawLive();
          el!.dataset.ready = "true";
          sync();
        };
        frame = requestAnimationFrame(stage);
      };
      schedule(slice);
      building = {
        cancel: () => {
          cancelled = true;
          cancelAnimationFrame(frame);
          if (idle) window.cancelIdleCallback(handle);
          else window.clearTimeout(handle);
        },
      };
    }

    const ro = new ResizeObserver(() => {
      const w = Math.round(el.clientWidth);
      const h = Math.round(el.clientHeight);
      if (Math.abs(w - size.w) < 2 && Math.abs(h - size.h) < 2) return;
      window.clearTimeout(resizeTimer);
      resizeTimer = window.setTimeout(() => {
        if (near || engine) build();
      }, engine ? 180 : 0);
    });
    // Two observers: one builds the field a little before the band arrives, the other runs the
    // loop only while some of the band is actually on screen (paused off-screen).
    const pre = new IntersectionObserver(
      ([e]) => {
        near = e.isIntersecting;
        if (near && !engine && !building) build();
      },
      { rootMargin: "35% 0px" },
    );
    const io = new IntersectionObserver(([e]) => {
      visible = e.isIntersecting;
      sync();
    });
    const onVis = () => sync();
    ro.observe(el);
    pre.observe(el);
    io.observe(el);
    document.addEventListener("visibilitychange", onVis);

    return () => {
      stop();
      building?.cancel();
      window.clearTimeout(resizeTimer);
      ro.disconnect();
      pre.disconnect();
      io.disconnect();
      document.removeEventListener("visibilitychange", onVis);
      syncRef.current = () => {};
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps -- frame and focus are tracked by their keys
  }, [mode, angle, frameKey, fadeSide, focusKey, density]);

  useEffect(() => {
    animateRef.current = animate;
    syncRef.current();
  }, [animate]);

  return (
    <div
      ref={root}
      className={`${styles.root} ${mode === "strip" ? styles.strip : styles.full}${className ? ` ${className}` : ""}`}
      data-fade={fadeSide}
      role={decorative ? undefined : "img"}
      aria-label={decorative ? undefined : LABELS.summary}
      aria-hidden={decorative ? true : undefined}
    >
      <canvas ref={baseRef} className={styles.canvas} aria-hidden="true" />
      <canvas ref={liveRef} className={styles.canvas} aria-hidden="true" />
      <noscript>{typeof window === "undefined" ? <Fallback mode={mode} angle={angle} frame={frame} fadeSide={fadeSide} focus={focus} /> : null}</noscript>
    </div>
  );
}

/** Server-only SVG of the same field (fewer lines), shown when JavaScript is off. */
function Fallback({ mode, angle, frame, fadeSide, focus }: Pick<Props, "angle" | "frame" | "fadeSide" | "focus"> & { mode: Mode }) {
  const [w, h] = mode === "strip" ? [390, 260] : [1600, 900];
  const f = buildFlowField({ ...layout(mode, w, h, frame, fadeSide, focus, 1, angle ?? 0), spacing: mode === "strip" ? 9 : 13, tow: 1, maxStep: 10 });
  const d = linesToPath(f.lines, 1);
  const r = f.holeR.toFixed(1);
  return (
    <svg className={styles.fallback} viewBox={`0 0 ${w} ${h}`} preserveAspectRatio="xMidYMid slice" aria-hidden="true">
      <path d={d} className={styles.fbLines} />
      {Array.from({ length: f.holes.length / 2 }, (_, k) => (
        <circle key={k} cx={f.holes[2 * k].toFixed(1)} cy={f.holes[2 * k + 1].toFixed(1)} r={r} className={styles.fbHole} />
      ))}
    </svg>
  );
}
