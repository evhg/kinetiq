#!/usr/bin/env node
// Check harness: builds and serves the production site (or targets --url),
// then screenshots every 10% of the page at phone, desktop and wide (2560) sizes,
// with motion on and with reduced motion. Records console errors, LCP, CLS,
// horizontal overflow, long frames while scrolling, blank frames and the fill
// rule (no mostly-black viewport, no dead black strip).
//
// Usage:
//   node scripts/check.mjs                      build + start locally
//   node scripts/check.mjs --skip-build         reuse the last .next build
//   node scripts/check.mjs --url=https://x.app  test a deployed URL
//   node scripts/check.mjs --path=/reserve      test another page
//   node scripts/check.mjs --only=wide          one viewport (phone|desktop|wide)
//   node scripts/check.mjs --url=... --study    reference mode: also detect
//                                               animation libraries and pins
// Output: .checks/<label>/ (git-ignored): PNGs, report.json, report.md.
// Exit code 1 when a budget or check fails (not in --study mode).

import { spawn, spawnSync } from "node:child_process";
import { createServer } from "node:net";
import { mkdirSync, rmSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { chromium } from "@playwright/test";

const args = Object.fromEntries(
  process.argv.slice(2).map((a) => {
    const [k, v] = a.replace(/^--/, "").split("=");
    return [k, v ?? true];
  }),
);

// A free port per run, so a stale server from an earlier build can never be tested by mistake.
const PORT = Number(args.port ?? (await freePort()));
const remote = typeof args.url === "string";
const baseUrl = remote ? args.url : `http://127.0.0.1:${PORT}/`;

function freePort() {
  return new Promise((resolve, reject) => {
    const srv = createServer();
    srv.once("error", reject);
    srv.listen(0, "127.0.0.1", () => {
      const { port } = srv.address();
      srv.close(() => resolve(port));
    });
  });
}
const study = Boolean(args.study);
// --path=/reserve tests another page on the same site.
const pagePath = typeof args.path === "string" ? args.path : "/";
const targetUrl = new URL(pagePath, baseUrl).toString();
const label = args.label ?? `${remote ? new URL(baseUrl).hostname : "local"}${pagePath === "/" ? "" : pagePath.replace(/\//g, "-")}`;
const outDir = join(process.cwd(), ".checks", label);

const BUDGET = { lcpMs: 2500, cls: 0.1 };
const VIEWPORTS = [
  { name: "phone", width: 390, height: 844, isMobile: true, hasTouch: true, deviceScaleFactor: 2 },
  { name: "desktop", width: 1440, height: 900, isMobile: false, hasTouch: false, deviceScaleFactor: 1 },
  { name: "wide", width: 2560, height: 1440, isMobile: false, hasTouch: false, deviceScaleFactor: 1 },
];
// Fill rule (DESIGN.md): no viewport may read as mostly black, at any width.
// - at most 40% of pixels at luma <= 12 (flat black)
// - at least 8% of pixels at luma >= 40 (something lit)
// - no vertical strip of flat black as wide as a quarter of the viewport (640 px at 2560, 360 px at 1440)
const FILL = { darkLuma: 12, maxDark: 0.4, litLuma: 40, minLit: 0.08, deadStrip: 0.25 };
const MODES = [
  { name: "motion", reducedMotion: "no-preference" },
  { name: "reduced", reducedMotion: "reduce" },
];
// Lighthouse-style mobile profile, applied to the phone runs.
const PHONE_THROTTLE = { cpuRate: 4, latency: 150, down: (1.6 * 1024 * 1024) / 8, up: (750 * 1024) / 8 };

const ANIMATION_LIB_SIGNATURES = {
  GSAP: /GreenSock|gsap\.registerPlugin|_gsap\b/,
  ScrollTrigger: /ScrollTrigger/,
  ScrollSmoother: /ScrollSmoother/,
  SplitText: /SplitText/,
  Lenis: /\blenis\b|Lenis/,
  "Locomotive Scroll": /locomotive-scroll|LocomotiveScroll/,
  "three.js": /three\.module|WebGLRenderer|__THREE__/,
  "React Three Fiber": /@react-three\/fiber|useFrame/,
  "Motion / Framer Motion": /framer-motion|motion\/react|MotionValue/,
  "Anime.js": /animejs|anime\.timeline/,
  Lottie: /lottie|bodymovin/,
  Rive: /@rive-app|rive\.wasm/,
  Spline: /@splinetool|splinecode/,
  Barba: /@barba|barba\.init/,
  Swiper: /swiper/i,
  "Theatre.js": /@theatre\/core/,
  OGL: /\bogl\b.*Renderer/,
};

function log(...m) {
  console.log("[check]", ...m);
}

async function waitForServer(url, timeoutMs = 60_000) {
  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    try {
      const res = await fetch(url);
      if (res.ok) return;
    } catch {}
    await new Promise((r) => setTimeout(r, 500));
  }
  throw new Error(`Server at ${url} did not start within ${timeoutMs} ms`);
}

async function launchBrowser() {
  const base = [
    "--enable-unsafe-swiftshader",
    "--use-angle=swiftshader",
    "--ignore-gpu-blocklist",
    "--enable-webgl",
    "--disable-gpu-compositing",
  ];
  const proxy = remote && process.env.HTTPS_PROXY ? { server: process.env.HTTPS_PROXY } : undefined;
  const executablePath = process.env.PLAYWRIGHT_CHROMIUM_PATH || undefined;
  try {
    return await chromium.launch({ args: base, proxy, executablePath });
  } catch (err) {
    log("launch failed, retrying with --no-sandbox:", String(err).split("\n")[0]);
    return chromium.launch({ args: [...base, "--no-sandbox"], proxy, executablePath });
  }
}

// Injected before any page script: LCP, CLS and long-frame counters.
function metricsInit() {
  window.__check = { lcp: 0, lcpEl: "", cls: 0, frames: 0, longFrames: 0, worstFrame: 0, watching: false };
  try {
    new PerformanceObserver((list) => {
      for (const e of list.getEntries()) {
        window.__check.lcp = e.startTime;
        const el = e.element;
        window.__check.lcpEl = el ? `${el.tagName.toLowerCase()}${el.id ? "#" + el.id : ""}${el.className && typeof el.className === "string" ? "." + el.className.split(" ")[0] : ""}` : "";
      }
    }).observe({ type: "largest-contentful-paint", buffered: true });
    new PerformanceObserver((list) => {
      for (const e of list.getEntries()) if (!e.hadRecentInput) window.__check.cls += e.value;
    }).observe({ type: "layout-shift", buffered: true });
  } catch {}
  let last = 0;
  const loop = (t) => {
    if (window.__check.watching && last) {
      const gap = t - last;
      window.__check.frames++;
      if (gap > 50) window.__check.longFrames++;
      window.__check.worstFrame = Math.max(window.__check.worstFrame, gap);
    }
    last = t;
    requestAnimationFrame(loop);
  };
  requestAnimationFrame(loop);
}

// Luminance statistics of a PNG, computed in a scratch page: contrast (std), the share of flat-black
// and lit pixels, and the widest run of columns that are flat black top to bottom (as a share of width).
async function imageStats(statsPage, png) {
  return statsPage.evaluate(
    async ({ b64, fill }) => {
      const blob = await (await fetch(`data:image/png;base64,${b64}`)).blob();
      const bmp = await createImageBitmap(blob);
      const w = 192;
      const h = Math.max(1, Math.round((bmp.height / bmp.width) * w));
      const c = new OffscreenCanvas(w, h);
      const ctx = c.getContext("2d");
      ctx.drawImage(bmp, 0, 0, w, h);
      const d = ctx.getImageData(0, 0, w, h).data;
      let sum = 0;
      let sq = 0;
      let dark = 0;
      let lit = 0;
      const colLit = new Uint8Array(w);
      const n = d.length / 4;
      for (let i = 0; i < d.length; i += 4) {
        const l = 0.2126 * d[i] + 0.7152 * d[i + 1] + 0.0722 * d[i + 2];
        sum += l;
        sq += l * l;
        if (l <= fill.darkLuma) dark++;
        else colLit[(i / 4) % w] = 1;
        if (l >= fill.litLuma) lit++;
      }
      let run = 0;
      let widest = 0;
      for (let x = 0; x < w; x++) {
        run = colLit[x] ? 0 : run + 1;
        widest = Math.max(widest, run);
      }
      const mean = sum / n;
      return { mean, std: Math.sqrt(Math.max(0, sq / n - mean * mean)), dark: dark / n, lit: lit / n, deadStrip: widest / w };
    },
    { b64: png.toString("base64"), fill: FILL },
  );
}

// Viewport screenshot straight from the DevTools Protocol, with a hard timeout.
// Software WebGL can take seconds per frame; a slow frame is not a failure.
async function capture(page, path) {
  const cdp = await page.context().newCDPSession(page);
  try {
    const shot = cdp.send("Page.captureScreenshot", { format: "png", captureBeyondViewport: false });
    const timeout = new Promise((_, reject) => setTimeout(() => reject(new Error("capture timed out after 90 s")), 90_000));
    const { data } = await Promise.race([shot, timeout]);
    const buf = Buffer.from(data, "base64");
    writeFileSync(path, buf);
    return buf;
  } finally {
    await cdp.detach().catch(() => {});
  }
}

async function scrollTo(page, y) {
  // Native scroll, like a scrollbar drag or keyboard: Lenis follows native scroll
  // events. (Instant lenis.scrollTo jumps into a pin can stall headless capture.)
  await page.evaluate((target) => window.scrollTo({ top: target, behavior: "instant" }), y);
}

async function studySnapshot(page) {
  return page.evaluate(() => {
    const describe = (el) => {
      if (!el) return "";
      const cls = typeof el.className === "string" ? el.className.trim().split(/\s+/).slice(0, 3).join(".") : "";
      return `${el.tagName.toLowerCase()}${el.id ? "#" + el.id : ""}${cls ? "." + cls : ""}`;
    };
    const pinSpacers = [...document.querySelectorAll(".pin-spacer")].map((s) => {
      const child = s.firstElementChild;
      const cs = child ? getComputedStyle(child) : null;
      return {
        pinned: describe(child),
        spacerHeight: Math.round(s.getBoundingClientRect().height),
        active: cs ? cs.position === "fixed" : false,
      };
    });
    const sticky = [...document.querySelectorAll("body *")]
      .filter((el) => getComputedStyle(el).position === "sticky")
      .slice(0, 10)
      .map(describe);
    const st = window.ScrollTrigger?.getAll?.().map((t) => ({
      trigger: describe(t.trigger),
      pin: Boolean(t.pin),
      scrub: t.vars?.scrub ?? null,
      start: t.start,
      end: t.end,
    }));
    return {
      pinSpacers,
      sticky,
      scrollTriggers: st ?? null,
      canvases: document.querySelectorAll("canvas").length,
      htmlClass: document.documentElement.className,
    };
  });
}

async function detectLibraries(page, scriptBodies) {
  const globals = await page.evaluate(() => ({
    gsap: Boolean(window.gsap),
    ScrollTrigger: Boolean(window.ScrollTrigger),
    Lenis: Boolean(window.Lenis || window.lenis),
    THREE: Boolean(window.THREE || window.__THREE__),
    lenisHtmlClass: document.documentElement.classList.contains("lenis"),
    locomotive: document.documentElement.classList.contains("has-scroll-smooth"),
    webglCanvas: [...document.querySelectorAll("canvas")].some((c) => {
      try {
        return Boolean(c.getContext("webgl2") || c.getContext("webgl"));
      } catch {
        return false;
      }
    }),
  }));
  const found = {};
  for (const [lib, re] of Object.entries(ANIMATION_LIB_SIGNATURES)) {
    const hits = scriptBodies.filter((s) => re.test(s.body)).map((s) => s.url.split("?")[0].split("/").pop());
    if (hits.length) found[lib] = [...new Set(hits)].slice(0, 5);
  }
  return { globals, signatures: found, scripts: scriptBodies.map((s) => ({ url: s.url, bytes: s.body.length })) };
}

async function runCase(browser, statsPage, vp, mode) {
  const context = await browser.newContext({
    viewport: { width: vp.width, height: vp.height },
    deviceScaleFactor: vp.deviceScaleFactor,
    isMobile: vp.isMobile,
    hasTouch: vp.hasTouch,
    reducedMotion: mode.reducedMotion,
    ignoreHTTPSErrors: false,
  });
  await context.addInitScript(metricsInit);
  const page = await context.newPage();
  const consoleErrors = [];
  const failedRequests = [];
  const scriptBodies = [];
  page.on("console", (m) => m.type() === "error" && consoleErrors.push(m.text()));
  page.on("pageerror", (e) => consoleErrors.push(`pageerror: ${e.message}`));
  page.on("requestfailed", (r) => failedRequests.push(`${r.failure()?.errorText} ${r.url()}`));
  if (study) {
    page.on("response", async (res) => {
      const type = res.request().resourceType();
      if (type !== "script") return;
      try {
        scriptBodies.push({ url: res.url(), body: await res.text() });
      } catch {}
    });
  }

  if (vp.name === "phone") {
    const cdp = await context.newCDPSession(page);
    await cdp.send("Emulation.setCPUThrottlingRate", { rate: PHONE_THROTTLE.cpuRate });
    await cdp.send("Network.enable");
    await cdp.send("Network.emulateNetworkConditions", {
      offline: false,
      latency: PHONE_THROTTLE.latency,
      downloadThroughput: PHONE_THROTTLE.down,
      uploadThroughput: PHONE_THROTTLE.up,
    });
  }

  const id = `${vp.name}-${mode.name}`;
  log(`${id}: loading ${targetUrl}`);
  await page.goto(targetUrl, { waitUntil: "load", timeout: 120_000 });
  await page.waitForLoadState("networkidle", { timeout: 30_000 }).catch(() => {});
  await page.waitForTimeout(2500); // idle-loaded 3D and late layout

  const load = await page.evaluate(() => ({ ...window.__check }));
  const sceneState = await page.evaluate(() => document.querySelector("[data-scene]")?.getAttribute("data-scene") ?? null);
  const overflowX = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 1);

  // 3D blank check: the scene region must not be a flat colour.
  let sceneStd = null;
  const scene = page.locator("[data-scene]").first();
  if ((await scene.count()) > 0) {
    const box = await scene.boundingBox();
    if (box && box.width > 10 && box.height > 10) {
      const png = await page.screenshot({ clip: box, timeout: 120_000 });
      sceneStd = (await imageStats(statsPage, png)).std;
    }
  }

  const steps = [];
  await page.evaluate(() => (window.__check.watching = true));
  for (let i = 0; i <= 10; i++) {
    const max = await page.evaluate(() => document.documentElement.scrollHeight - window.innerHeight);
    await scrollTo(page, Math.round((max * i) / 10));
    await page.waitForTimeout(vp.name === "phone" ? 1200 : 800);
    const file = `${id}-${String(i * 10).padStart(3, "0")}.png`;
    const shotStart = Date.now();
    const png = await capture(page, join(outDir, file));
    if (args.verbose) log(`${id} ${i * 10}%: screenshot ${Date.now() - shotStart} ms`);
    const stats = await imageStats(statsPage, png);
    const step = {
      pct: i * 10,
      file,
      std: Number(stats.std.toFixed(1)),
      blank: stats.std < 2,
      dark: Number(stats.dark.toFixed(2)),
      lit: Number(stats.lit.toFixed(2)),
      deadStrip: Number(stats.deadStrip.toFixed(2)),
    };
    step.fillFail = [
      step.dark > FILL.maxDark ? `${Math.round(step.dark * 100)}% flat black` : null,
      step.lit < FILL.minLit ? `only ${Math.round(step.lit * 100)}% lit` : null,
      step.deadStrip >= FILL.deadStrip ? `dead strip ${Math.round(step.deadStrip * 100)}% wide` : null,
    ].filter(Boolean);
    if (study) step.study = await studySnapshot(page);
    steps.push(step);
  }
  const after = await page.evaluate(() => ({ ...window.__check }));
  const interactions = study ? null : await interactionChecks(page);
  const libs = study ? await detectLibraries(page, scriptBodies) : null;
  await context.close();

  return {
    id,
    viewport: vp.name,
    mode: mode.name,
    lcpMs: Math.round(load.lcp),
    lcpElement: load.lcpEl,
    clsAtLoad: Number(load.cls.toFixed(3)),
    clsAfterScroll: Number(after.cls.toFixed(3)),
    longFrames: after.longFrames,
    frames: after.frames,
    worstFrameMs: Math.round(after.worstFrame),
    sceneState,
    sceneStd: sceneStd === null ? null : Number(sceneStd.toFixed(1)),
    overflowX,
    interactions,
    consoleErrors,
    failedRequests,
    blankSteps: steps.filter((s) => s.blank).map((s) => s.pct),
    fillSteps: steps.filter((s) => s.fillFail.length).map((s) => `${s.pct}% (${s.fillFail.join(", ")})`),
    steps,
    libs,
  };
}

// Functional checks for the shared UI: the Skip link of the first pinned chapter. Below 900 px the
// chapters don't pin and the link is hidden by design, so there is nothing to check there.
async function interactionChecks(page) {
  const out = {};
  const skipLink = page.locator(".skip-link").first();
  if ((await skipLink.count()) > 0 && (await skipLink.isVisible())) {
    const href = await skipLink.getAttribute("href");
    const pinTop = await page.evaluate(() => {
      const el = document.querySelector(".pin");
      return el ? el.getBoundingClientRect().top + window.scrollY : 0;
    });
    await scrollTo(page, Math.round(pinTop + 50));
    await page.waitForTimeout(800);
    await skipLink.focus();
    await page.keyboard.press("Enter");
    await page.waitForTimeout(800);
    // The target lands just below the fixed header: html's scroll-padding-top (header height + 16 px).
    out.skip = await page.evaluate((id) => {
      const t = document.getElementById(id);
      const top = t ? t.getBoundingClientRect().top : null;
      const pad = parseFloat(getComputedStyle(document.documentElement).scrollPaddingTop) || 0;
      return { targetTop: top === null ? null : Math.round(top), expectedTop: Math.round(pad), focused: document.activeElement?.id === id };
    }, href.slice(1));
    out.skip.ok = out.skip.focused && out.skip.targetTop !== null && Math.abs(out.skip.targetTop - out.skip.expectedTop) < 40;
  }
  return out;
}

function evaluate(results) {
  const failures = [];
  for (const r of results) {
    if (r.consoleErrors.length) failures.push(`${r.id}: ${r.consoleErrors.length} console error(s)`);
    if (r.blankSteps.length) failures.push(`${r.id}: blank frames at ${r.blankSteps.join(", ")}%`);
    if (r.overflowX) failures.push(`${r.id}: horizontal overflow`);
    if (r.clsAfterScroll > BUDGET.cls) failures.push(`${r.id}: CLS ${r.clsAfterScroll} > ${BUDGET.cls}`);
    if (r.viewport === "phone" && r.lcpMs > BUDGET.lcpMs) failures.push(`${r.id}: LCP ${r.lcpMs} ms > ${BUDGET.lcpMs} ms`);
    if (r.sceneState === "webgl" && r.sceneStd !== null && r.sceneStd < 2) failures.push(`${r.id}: 3D scene looks blank`);
    if (r.interactions?.skip && !r.interactions.skip.ok) failures.push(`${r.id}: Skip link did not land on its target with focus`);
    if (r.fillSteps.length) failures.push(`${r.id}: fill rule broken at ${r.fillSteps.join("; ")}`);
  }
  return failures;
}

function markdown(results, failures) {
  const rows = results.map(
    (r) =>
      `| ${r.id} | ${r.lcpMs} (${r.lcpElement || "?"}) | ${r.clsAfterScroll} | ${r.longFrames}/${r.frames} (worst ${r.worstFrameMs} ms) | ${r.sceneState ?? "-"} (${r.sceneStd ?? "-"}) | ${r.interactions?.skip ? (r.interactions.skip.ok ? "ok" : "FAIL") : "-"} | ${r.consoleErrors.length} | ${r.blankSteps.length ? r.blankSteps.join(",") : "none"} | ${r.fillSteps.length ? r.fillSteps.length : "ok"} |`,
  );
  return [
    `# Check report: ${targetUrl}`,
    "",
    `Run at ${new Date().toISOString()}. Phone runs use 4x CPU slowdown, 150 ms RTT, 1.6 Mbps.`,
    "Long frames are measured in headless Chromium with software WebGL, so treat them as a smoke signal, not a device measurement.",
    "",
    "| Case | LCP ms (element) | CLS | Long frames >50 ms | Scene (contrast) | Skip link | Console errors | Blank steps | Fill rule |",
    "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ...rows,
    "",
    failures.length ? `## Failures\n\n${failures.map((f) => `- ${f}`).join("\n")}` : "## Result: all checks passed",
    "",
    ...results.flatMap((r) => (r.consoleErrors.length ? [`### ${r.id} console errors`, ...r.consoleErrors.map((e) => `- ${e}`), ""] : [])),
  ].join("\n");
}

async function main() {
  rmSync(outDir, { recursive: true, force: true });
  mkdirSync(outDir, { recursive: true });

  let server = null;
  if (!remote) {
    if (!args["skip-build"]) {
      log("building…");
      const b = spawnSync("npm", ["run", "build"], { stdio: "inherit" });
      if (b.status !== 0) process.exit(b.status ?? 1);
    }
    server = spawn("npx", ["next", "start", "-p", String(PORT)], { stdio: "ignore", detached: true });
    await waitForServer(baseUrl);
    log("server ready on", baseUrl);
  }

  // A fresh browser per case: software WebGL state from one case must not slow the next.
  const results = [];
  try {
    for (const vp of VIEWPORTS.filter((v) => !args.only || v.name === args.only)) {
      for (const mode of MODES.filter((m) => !args.mode || m.name === args.mode)) {
        const browser = await launchBrowser();
        try {
          const statsPage = await (await browser.newContext()).newPage();
          results.push(await runCase(browser, statsPage, vp, mode));
        } finally {
          await browser.close();
        }
      }
    }
  } finally {
    if (server) {
      try {
        process.kill(-server.pid);
      } catch {}
    }
  }

  const failures = study ? [] : evaluate(results);
  writeFileSync(join(outDir, "report.json"), JSON.stringify({ baseUrl, results, failures }, null, 2));
  writeFileSync(join(outDir, "report.md"), markdown(results, failures));
  console.log(markdown(results, failures));
  log(`screenshots and report in ${outDir}`);
  if (failures.length) process.exit(1);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
