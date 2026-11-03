// 5K delivery probe (owner, 2026-11-03, on a 5K screen: "the image doesn't look hi-res"). Loads a page at 2560 x 1440
// CSS px and DPR 2 (a 5K display), scrolls through it so every lazy still loads, and reports for each <img> and each
// swivel <canvas>: the physical pixels it covers on screen (object-fit: cover), the width of the file the browser
// chose, the widest one its srcset offers, and the shortfall. "upscaled" means the screen shows the file larger than
// its pixels; "capped by export" means the srcset has nothing wider (the render owner's exports), "chose narrower"
// means the markup (sizes) let the browser pick a narrower file than one available.
//   node scripts/probe-5k.mjs --url=http://127.0.0.1:3311/ [--path=/reserve] [--feel=pace] [--grip=off] [--dpr=2]
import { chromium } from "@playwright/test";
import { ndaCookie } from "./nda-cookie.mjs";

const args = Object.fromEntries(process.argv.slice(2).map((a) => { const [k, ...v] = a.replace(/^--/, "").split("="); return [k, v.join("=") || true]; }));
const base = args.url ?? "http://127.0.0.1:3311/";
const url = new URL(args.path ?? "/", base).toString();
const dpr = Number(args.dpr ?? 2);
const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 2560, height: 1440 }, deviceScaleFactor: dpr });
const host = new URL(base).hostname;
const cookies = [ndaCookie(base)];
if (args.feel) cookies.push({ name: "kq-feel", value: args.feel, domain: host, path: "/" });
if (args.grip) cookies.push({ name: "kq-grip", value: args.grip, domain: host, path: "/" });
await ctx.addCookies(cookies);
const page = await ctx.newPage();
await page.goto(url, { waitUntil: "load" });
const rows = new Map();
const total = await page.evaluate(() => document.documentElement.scrollHeight);
for (let y = 0; y < total; y += 600) {
  await page.evaluate((v) => window.scrollTo(0, v), y);
  await page.waitForTimeout(250);
  const seen = await page.evaluate(() => {
    const out = [];
    for (const img of document.querySelectorAll("img")) {
      const r = img.getBoundingClientRect();
      if (r.width < 200 || r.bottom < 0 || r.top > innerHeight || !img.currentSrc || !img.naturalWidth) continue;
      if (getComputedStyle(img).visibility === "hidden") continue;
      const fit = getComputedStyle(img).objectFit;
      const s = fit === "cover" ? Math.max(r.width / img.naturalWidth, r.height / img.naturalHeight) : fit === "contain" ? Math.min(r.width / img.naturalWidth, r.height / img.naturalHeight) : r.width / img.naturalWidth;
      const pic = img.closest("picture");
      const source = pic && [...pic.querySelectorAll("source")].find((so) => (!so.media || matchMedia(so.media).matches) && so.type === "image/avif");
      const set = (source?.srcset || img.srcset || "").split(",").map((x) => Number(x.trim().split(" ")[1]?.replace("w", ""))).filter(Boolean);
      const name = img.currentSrc.split("/").pop();
      const fileW = Number(name.match(/-(\d+)\.[0-9a-f]+\.(avif|webp)$/)?.[1] ?? img.naturalWidth);
      const key = name.replace(/-\d+\.[0-9a-f]+\.(avif|webp)$/, "");
      out.push({ key, file: name, shownPx: Math.round(img.naturalWidth * s * devicePixelRatio), fileW, maxW: Math.max(...set, fileW) });
    }
    for (const c of document.querySelectorAll("canvas")) {
      const r = c.getBoundingClientRect();
      if (r.width < 200 || r.bottom < 0 || r.top > innerHeight || c.dataset.on === "false" || !c.width) continue;
      out.push({ key: `canvas:${c.closest("section")?.id ?? "?"}`, file: `${c.width}x${c.height}`, shownPx: Math.round(r.width * devicePixelRatio), fileW: c.width, maxW: c.width });
    }
    return out;
  });
  for (const s of seen) {
    const prev = rows.get(s.key);
    if (!prev || s.shownPx > prev.shownPx) rows.set(s.key, s);
  }
}
await browser.close();
let bad = 0;
console.log(`${url} at 2560 x 1440, DPR ${dpr}`);
console.log("still | shown (device px wide) | file | widest in srcset | verdict");
for (const r of [...rows.values()].sort((a, b) => b.shownPx / b.fileW - a.shownPx / a.fileW)) {
  const k = r.shownPx / r.fileW;
  const verdict = k <= 1.05 ? "ok" : r.fileW < r.maxW ? `chose narrower (x${k.toFixed(2)})` : `upscaled x${k.toFixed(2)}, capped by export`;
  if (k > 1.05) bad++;
  console.log(`${r.key} | ${r.shownPx} | ${r.file} | ${r.maxW} | ${verdict}`);
}
console.log(`${bad} of ${rows.size} upscaled`);
