// Screenshots of one section at a list of viewports, for review (owner feedback, 2026-11-03). Scrolls to the section,
// optionally to a fraction of its pinned length, and saves the viewport.
//   node scripts/section-shots.mjs --url=http://127.0.0.1:3311/ --id=sweet-spot --at=0,0.3,0.6,1 --feel=pace --grip=off
//     --sizes=375x667,390x844,768x1024,1440x900,2560x1440@2 --mode=motion|reduced --out=.checks/shots
import { chromium } from "@playwright/test";
import { mkdirSync } from "node:fs";
import { join } from "node:path";
import { ndaCookie } from "./nda-cookie.mjs";

const args = Object.fromEntries(process.argv.slice(2).map((a) => { const [k, ...v] = a.replace(/^--/, "").split("="); return [k, v.join("=") || true]; }));
const url = args.url ?? "http://127.0.0.1:3311/";
const id = args.id;
const at = String(args.at ?? "0").split(",").map(Number);
const sizes = String(args.sizes ?? "390x844,768x1024,1440x900,2560x1440").split(",");
const out = args.out ?? ".checks/shots";
mkdirSync(out, { recursive: true });
const browser = await chromium.launch({ args: ["--disable-gpu-compositing"] });
for (const size of sizes) {
  const [wh, dpr = "1"] = size.split("@");
  const [width, height] = wh.split("x").map(Number);
  const ctx = await browser.newContext({ viewport: { width, height }, deviceScaleFactor: Number(dpr), reducedMotion: args.mode === "reduced" ? "reduce" : "no-preference", isMobile: width < 900, hasTouch: width < 900 });
  const cookies = [ndaCookie(url)];
  const base = new URL(url);
  if (args.feel) cookies.push({ name: "kq-feel", value: args.feel, domain: base.hostname, path: "/" });
  if (args.grip) cookies.push({ name: "kq-grip", value: args.grip, domain: base.hostname, path: "/" });
  await ctx.addCookies(cookies);
  if (args.feel || args.grip) await ctx.addInitScript(([f, g]) => { try { if (f) localStorage.setItem("kq-feel", f); if (g) localStorage.setItem("kq-grip", g); } catch {} }, [args.feel, args.grip]);
  const page = await ctx.newPage();
  await page.goto(url, { waitUntil: "load" });
  await page.waitForTimeout(800);
  // walk down so lazy stills load and once-only reveals fire
  const total = await page.evaluate(() => document.documentElement.scrollHeight);
  for (let y = 0; y < total; y += height * 0.8) { await page.evaluate((v) => window.scrollTo(0, v), y); await page.waitForTimeout(60); }
  for (const f of at) {
    const y = await page.evaluate(([sel, f]) => {
      const el = document.getElementById(sel);
      const r = el.getBoundingClientRect();
      const top = r.top + window.scrollY;
      const pinLen = Math.max(0, el.offsetHeight - window.innerHeight);
      return Math.round(top + (pinLen ? pinLen * f : f * el.offsetHeight));
    }, [id, f]);
    await page.evaluate((v) => { if (window.__lenis) window.__lenis.scrollTo(v, { immediate: true, force: true }); else window.scrollTo(0, v); }, y);
    await page.waitForTimeout(1600);
    const name = `${id}-${size.replace("@", "-dpr")}-${args.mode ?? "motion"}${args.feel ? `-${args.feel}` : ""}${args.grip ? `-grip-${args.grip}` : ""}-${f}.png`;
    await page.screenshot({ path: join(out, name) });
    console.log(join(out, name));
  }
  await ctx.close();
}
await browser.close();
