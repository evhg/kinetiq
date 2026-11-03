// Registration probe for the drawings laid over stills (owner, 2026-11-03: the sealed core's "yellow outline doesn't
// follow the graphic"): SealedCoreTrace over K03 and SweetSpotEdge over K14. For each visible overlay <svg>, it maps
// image-space points through two independent routes and reports the largest gap in CSS px:
//   1. the <img>: its currentSrc's crop, laid out by object-fit (cover) and object-position, from getBoundingClientRect;
//   2. the <svg>: getScreenCTM() of its viewBox (preserveAspectRatio slice).
// Then it saves a crop of the screen around the overlay, so the line can be checked on the render by eye.
//   node scripts/probe-overlay.mjs --url=http://127.0.0.1:3311/ --sizes=390x844,768x1024,1440x900,2560x1440 --feel=pace
import { chromium } from "@playwright/test";
import { mkdirSync } from "node:fs";
import { join } from "node:path";
import { ndaCookie } from "./nda-cookie.mjs";

const args = Object.fromEntries(process.argv.slice(2).map((a) => { const [k, ...v] = a.replace(/^--/, "").split("="); return [k, v.join("=") || true]; }));
const url = args.url ?? "http://127.0.0.1:3311/";
const sizes = String(args.sizes ?? "390x844,768x1024,1440x900,2560x1440").split(",");
const out = args.out ?? ".checks/overlay";
mkdirSync(out, { recursive: true });
// Each overlay: its section, the selector of its svgs, the image crops' boxes in the master's 1280 x 720 space.
const TARGETS = [
  { id: "sealed-core", svg: "svg[data-seal-trace]", at: 0.8, points: [[450, 343], [691.5, 525], [451, 530], [547.8, 249.3]] },
  { id: "sweet-spot", svg: "svg[data-sweet-edge]", at: 1, points: [[640, 215.7], [960, 121.4], [1180, 82], [700, 194]] },
];
const browser = await chromium.launch({ args: ["--disable-gpu-compositing"] });
let worst = 0;
for (const size of sizes) {
  const [wh, dpr = "1"] = size.split("@");
  const [width, height] = wh.split("x").map(Number);
  const ctx = await browser.newContext({ viewport: { width, height }, deviceScaleFactor: Number(dpr), isMobile: width < 900, hasTouch: width < 900, reducedMotion: args.mode === "reduced" ? "reduce" : "no-preference" });
  const host = new URL(url).hostname;
  const cookies = [ndaCookie(url)];
  if (args.feel) cookies.push({ name: "kq-feel", value: args.feel, domain: host, path: "/" });
  await ctx.addCookies(cookies);
  if (args.feel) await ctx.addInitScript((f) => { try { localStorage.setItem("kq-feel", f); } catch {} }, args.feel);
  const page = await ctx.newPage();
  await page.goto(url, { waitUntil: "load" });
  const total = await page.evaluate(() => document.documentElement.scrollHeight);
  for (let y = 0; y < total; y += height * 0.8) { await page.evaluate((v) => window.scrollTo(0, v), y); await page.waitForTimeout(40); }
  for (const t of TARGETS) {
    await page.evaluate(([id, f]) => {
      const el = document.getElementById(id);
      const top = el.getBoundingClientRect().top + window.scrollY;
      const len = Math.max(0, el.offsetHeight - window.innerHeight);
      const y = Math.round(top + (len ? len * f : 0) - (len ? 0 : window.innerHeight * 0.15));
      if (window.__lenis) window.__lenis.scrollTo(y, { immediate: true, force: true }); else window.scrollTo(0, y);
    }, [t.id, t.at]);
    await page.waitForTimeout(1800);
    const r = await page.evaluate(([sel, pts]) => {
      const svg = [...document.querySelectorAll(sel)].find((s) => s.getBoundingClientRect().width > 0 && getComputedStyle(s).display !== "none");
      if (!svg) return { missing: true };
      let frame = svg.parentElement;
      while (frame && !frame.querySelector("img")) frame = frame.parentElement;
      const img = frame.querySelector("img");
      const vb = svg.viewBox.baseVal;
      // The crop the img shows, in the master's 1280 x 720 space, read from its file name (e.g. "K03-card-1080").
      const src = img.currentSrc;
      const crop = /-card-|-portrait-/.test(src) ? (/K03/.test(src) ? { x: 352, w: 576 } : { x: 492.8, w: 576 }) : { x: 0, w: 1280 };
      const ib = img.getBoundingClientRect();
      const s = Math.max(ib.width / crop.w, ib.height / 720);
      const [px, py] = getComputedStyle(img).objectPosition.split(" ").map((v) => parseFloat(v) / 100);
      const ox = ib.left + (ib.width - crop.w * s) * px;
      const oy = ib.top + (ib.height - 720 * s) * py;
      const m = svg.getScreenCTM();
      const gaps = pts.map(([x, y]) => {
        const a = { x: ox + (x - crop.x) * s, y: oy + y * s };
        const p = svg.createSVGPoint(); p.x = x; p.y = y; const b = p.matrixTransform(m);
        return Math.hypot(a.x - b.x, a.y - b.y);
      });
      const sb = svg.getBoundingClientRect();
      return { src: src.split("/").pop(), viewBox: `${vb.x} ${vb.y} ${vb.width} ${vb.height}`, gap: Math.max(...gaps), box: [sb.left, sb.top, sb.width, sb.height], shown: getComputedStyle(svg).visibility };
    }, [t.svg, t.points]);
    if (r.missing) { console.log(`${size} ${t.id}: no visible overlay`); continue; }
    worst = Math.max(worst, r.gap);
    const name = `${t.id}-${size.replace("@", "-dpr")}${args.feel ? `-${args.feel}` : ""}${args.mode ? `-${args.mode}` : ""}.png`;
    const vw = width, vh = height;
    const clip = { x: Math.max(0, r.box[0]), y: Math.max(0, r.box[1]), width: Math.min(vw, r.box[0] + r.box[2]) - Math.max(0, r.box[0]), height: Math.min(vh, r.box[1] + r.box[3]) - Math.max(0, r.box[1]) };
    if (clip.width > 0 && clip.height > 0) await page.screenshot({ path: join(out, name), clip });
    console.log(`${size} ${t.id}: ${r.src} viewBox ${r.viewBox} ${r.shown}, max gap ${r.gap.toFixed(3)} px -> ${join(out, name)}`);
  }
  await ctx.close();
}
await browser.close();
console.log(`worst gap ${worst.toFixed(3)} px`);
process.exit(worst <= 1 ? 0 : 1);
