// Swivel probe: for each device, which sequence and export width the swivels (hero K01, Unibody K02) pick, the
// canvas's backing size, how much the frame is scaled up to fill it, and how the drawn frame follows the scroll.
// Usage: node scripts/swivel-probe.mjs <base url> [--only=name,...] [--shots=<dir>] [--strip]
// Reads the page through an init script that tags each decoded frame with its URL (fetch -> blob -> bitmap/img) and
// records every drawImage onto a swivel canvas, then scrolls through each swivel in small steps.
import { mkdirSync, writeFileSync } from "node:fs";
import { chromium } from "@playwright/test";
import { ndaCookie } from "./nda-cookie.mjs";

const args = process.argv.slice(2);
const flags = Object.fromEntries(args.filter((a) => a.startsWith("--")).map((a) => a.slice(2).split("=")));
const [base = "http://127.0.0.1:3217/"] = args.filter((a) => !a.startsWith("--"));
const only = flags.only ? flags.only.split(",") : null;
const shotsDir = flags.shots;
if (shotsDir) mkdirSync(shotsDir, { recursive: true });

const DEVICES = [
  { name: "iphone15", width: 390, height: 844, dpr: 3, mobile: true },
  { name: "iphone-safari", width: 390, height: 664, dpr: 3, mobile: true },
  { name: "ipad-air-portrait", width: 820, height: 1180, dpr: 2, mobile: true },
  { name: "ipad-air-landscape", width: 1180, height: 820, dpr: 2, mobile: true },
  { name: "ipad-pro-portrait", width: 1024, height: 1366, dpr: 2, mobile: true },
  { name: "ipad-pro-landscape", width: 1366, height: 1024, dpr: 2, mobile: true },
  { name: "desktop-1440", width: 1440, height: 900, dpr: 1, mobile: false },
  { name: "desktop-1440-retina", width: 1440, height: 900, dpr: 2, mobile: false },
  { name: "wide-2560", width: 2560, height: 1440, dpr: 1, mobile: false },
];

const init = () => {
  const tag = new WeakMap();
  window.__swivel = { draws: [] };
  const blob = Response.prototype.blob;
  Response.prototype.blob = async function () {
    const b = await blob.call(this);
    tag.set(b, this.url);
    return b;
  };
  const cib = window.createImageBitmap;
  window.createImageBitmap = async function (src, ...rest) {
    const bm = await cib.call(window, src, ...rest);
    if (tag.has(src)) tag.set(bm, tag.get(src));
    return bm;
  };
  const draw = CanvasRenderingContext2D.prototype.drawImage;
  CanvasRenderingContext2D.prototype.drawImage = function (img, ...rest) {
    const url = tag.get(img) ?? img.currentSrc ?? img.src ?? "";
    const m = /seq\/([^/]+)\/(\d+)-(\d+)\./.exec(url);
    if (m) window.__swivel.draws.push({ seq: m[1], i: +m[2], w: +m[3], alpha: this.globalAlpha, y: scrollY, t: performance.now(), iw: img.width, ih: img.height });
    return draw.call(this, img, ...rest);
  };
};

const browser = await chromium.launch();
const report = {};
for (const d of DEVICES) {
  if (only && !only.includes(d.name)) continue;
  const ctx = await browser.newContext({ viewport: { width: d.width, height: d.height }, deviceScaleFactor: d.dpr, isMobile: d.mobile, hasTouch: d.mobile });
  await ctx.addCookies([ndaCookie(base)]);
  await ctx.addInitScript(init);
  const page = await ctx.newPage();
  const requests = [];
  page.on("request", (r) => {
    const m = /seq\/([^/]+)\/(\d+)-(\d+)\.\w+\.(\w+)/.exec(r.url());
    if (m) requests.push({ seq: m[1], i: +m[2], w: +m[3], fmt: m[4] });
  });
  const bytes = {};
  page.on("response", async (r) => {
    const m = /seq\/([^/]+)\//.exec(r.url());
    if (!m) return;
    const len = Number((await r.allHeaders())["content-length"] ?? 0) || (await r.body().catch(() => Buffer.alloc(0))).length;
    bytes[m[1]] = (bytes[m[1]] ?? 0) + len;
  });
  await page.goto(base, { waitUntil: "load" });
  await page.waitForTimeout(2500);
  const out = { device: `${d.width}x${d.height}@${d.dpr}` };
  for (const [label, sel] of [
    ["hero", "#hero-title"],
    ["unibody", "#unibody"],
  ]) {
    // Bring the swivel near, wait for frames, then scroll through it.
    const info = await page.evaluate((sel) => {
      const el = document.querySelector(sel);
      const sec = el.closest("section") ?? el;
      return { top: sec.getBoundingClientRect().top + scrollY, height: sec.getBoundingClientRect().height, vh: innerHeight };
    }, sel);
    const startY = label === "hero" ? 0 : Math.max(0, info.top - info.vh);
    const endY = label === "hero" ? info.height * 0.45 : info.top + info.height;
    await page.evaluate((y) => scrollTo(0, y), startY);
    await page.waitForTimeout(400);
    await page.evaluate((y) => scrollTo(0, y), startY + 2);
    await page.waitForTimeout(6000);
    await page.evaluate(() => (window.__swivel.draws = []));
    const step = 4;
    const samples = [];
    for (let y = startY; y <= endY; y += step) {
      await page.evaluate((y) => scrollTo(0, y), y);
      await page.waitForTimeout(40);
      samples.push(y);
    }
    await page.waitForTimeout(600);
    const res = await page.evaluate((label) => {
      const canvases = [...document.querySelectorAll("canvas[aria-hidden]")];
      const c = canvases.find((c) => (label === "hero" ? !c.closest("#unibody") && c.closest("section")?.querySelector("#hero-title") : c.closest("#unibody")));
      const draws = window.__swivel.draws;
      const cs = c ? getComputedStyle(c) : null;
      return {
        canvas: c ? { backing: [c.width, c.height], css: [parseFloat(cs.width), parseFloat(cs.height)], on: c.dataset.on } : null,
        draws,
      };
    }, label);
    const prefix = label === "hero" ? "K01-" : "K02-";
    const ds = res.draws.filter((x) => x.seq.startsWith(prefix));
    const seqs = [...new Set(ds.map((x) => x.seq))];
    const widths = [...new Set(ds.map((x) => x.w))];
    const frameW = ds.length ? Math.max(...ds.map((x) => x.iw)) : 0;
    // Distinct frames drawn and the scroll per frame change.
    const changes = [];
    for (let k = 1; k < ds.length; k++) if (ds[k].i !== ds[k - 1].i) changes.push(ds[k].y - ds[k - 1].y);
    const maxI = ds.length ? Math.max(...ds.map((x) => x.i)) : 0;
    const turnPx = ds.length ? ds.find((x) => x.i === maxI).y - ds[0].y : 0;
    out[label] = {
      seq: seqs,
      exportWidth: widths,
      frameBitmap: ds.length ? [ds[0].iw, ds[0].ih] : null,
      canvas: res.canvas,
      upscale: res.canvas && frameW ? +(res.canvas.backing[0] / frameW).toFixed(2) : null,
      deviceUpscale: res.canvas && frameW ? +((res.canvas.css[0] * d.dpr) / frameW).toFixed(2) : null,
      framesDrawn: new Set(ds.map((x) => x.i)).size,
      draws: ds.length,
      blended: ds.some((x) => x.alpha < 0.999),
      turnScrollPx: Math.round(turnPx),
      lastFrame: maxI,
      pxPerFrame: maxI ? +(turnPx / maxI).toFixed(1) : null,
    };
    if (shotsDir && ds.length) {
      // A strip: the swivel at about a quarter, half and three quarters of its turn (blended between frames), at 100%.
      for (const q of [0.25, 0.5, 0.75]) {
        const target = maxI * q;
        const hit = ds.reduce((a, b) => (Math.abs(b.i - target) < Math.abs(a.i - target) ? b : a));
        await page.evaluate((y) => scrollTo(0, y), hit.y + 2);
        await page.waitForTimeout(900);
        const rect = await page.evaluate((label) => {
          const c = [...document.querySelectorAll("canvas[aria-hidden]")].find((c) => (label === "hero" ? !c.closest("#unibody") : c.closest("#unibody")));
          const r = c.getBoundingClientRect();
          return { x: Math.max(0, r.x), y: Math.max(0, r.y), width: Math.min(innerWidth, r.right) - Math.max(0, r.x), height: Math.min(innerHeight, r.bottom) - Math.max(0, r.y) };
        }, label);
        if (rect.width > 4 && rect.height > 4) await page.screenshot({ path: `${shotsDir}/${d.name}-${label}-${Math.round(q * 100)}.png`, clip: rect });
      }
      await page.screenshot({ path: `${shotsDir}/${d.name}-${label}-view.png` });
    }
  }
  out.requests = Object.fromEntries([...new Set(requests.map((r) => r.seq))].map((s) => [s, { n: requests.filter((r) => r.seq === s).length, widths: [...new Set(requests.filter((r) => r.seq === s).map((r) => r.w))], fmt: [...new Set(requests.filter((r) => r.seq === s).map((r) => r.fmt))], kb: Math.round((bytes[s] ?? 0) / 1024) }]));
  report[d.name] = out;
  console.log(d.name, JSON.stringify(out, null, 1));
  await ctx.close();
}
await browser.close();
if (flags.json) writeFileSync(flags.json, JSON.stringify(report, null, 1));
