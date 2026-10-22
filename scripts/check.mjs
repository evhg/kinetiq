#!/usr/bin/env node
// Check harness: builds and serves the production site (or targets --url),
// then screenshots every 10% of the page at phone, desktop and wide (2560) sizes,
// with motion on and with reduced motion. Records console errors, LCP, CLS,
// horizontal overflow, long frames while scrolling, blank frames and the fill
// rule (no mostly-black viewport, no dead black strip). By keyboard: every Skip
// link, and the sweet-spot ‡ marks reached by Tab and shown the moment they have focus.
//
// Usage:
//   node scripts/check.mjs                      build + start locally
//   node scripts/check.mjs --skip-build         reuse the last .next build
//   node scripts/check.mjs --url=https://x.app  test a deployed URL
//   node scripts/check.mjs --path=/reserve      test another page
//   node scripts/check.mjs --only=wide          one viewport (phone|desktop|wide)
//   node scripts/check.mjs --url=... --study    reference mode: also detect
//                                               animation libraries and pins
//   node scripts/check.mjs --gate               the NDA gate: loads the page WITHOUT the
//                                               cookie, checks the gate screen, walks it by
//                                               keyboard to the real page, and checks that
//                                               assets and APIs answer 403 without the cookie
// Every other case carries the NDA cookie (scripts/nda-cookie.mjs), so it sees the real site.
// Output: .checks/<label>/ (git-ignored): PNGs, report.json, report.md.
// Exit code 1 when a budget or check fails (not in --study mode).

import { spawn, spawnSync } from "node:child_process";
import { createServer } from "node:net";
import { existsSync, mkdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { chromium, request as apiRequest } from "@playwright/test";
import { NDA_COOKIE, ndaCookie, ndaHeader } from "./nda-cookie.mjs";

const args = Object.fromEntries(
  process.argv.slice(2).map((a) => {
    // Split at the first "=" only, so --path=/reserve?tier=limited keeps its query.
    const [k, ...v] = a.replace(/^--/, "").split("=");
    return [k, v.length ? v.join("=") : true];
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
const gateMode = Boolean(args.gate);
// --path=/reserve tests another page on the same site.
const pagePath = typeof args.path === "string" ? args.path : "/";
const targetUrl = new URL(pagePath, baseUrl).toString();
const label =
  args.label ??
  `${remote ? new URL(baseUrl).hostname : "local"}${pagePath === "/" ? "" : pagePath.replace(/[/?=&]/g, "-")}${gateMode ? "-gate" : ""}`;
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

// Remote sites go through the sandbox's HTTPS proxy; a local server (--url=http://localhost:…) never does.
function proxyConfig() {
  const local = ["localhost", "127.0.0.1", "[::1]"].includes(new URL(baseUrl).hostname);
  return remote && !local && process.env.HTTPS_PROXY ? { server: process.env.HTTPS_PROXY, bypass: "localhost,127.0.0.1" } : undefined;
}

async function launchBrowser() {
  const base = [
    "--enable-unsafe-swiftshader",
    "--use-angle=swiftshader",
    "--ignore-gpu-blocklist",
    "--enable-webgl",
    "--disable-gpu-compositing",
  ];
  const proxy = proxyConfig();
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
  // Native scroll, like a scrollbar drag or keyboard: Lenis follows native scroll events. The page is
  // scrolled in 120 px steps, one per frame, as a person would: an instant 1,500 px jump lands in the
  // middle of a pinned chapter, and the pin engaging one frame later reads as a layout shift no visitor
  // ever sees. (Instant lenis.scrollTo jumps into a pin can also stall headless capture.)
  await page.evaluate(async (target) => {
    const frame = () => new Promise((r) => requestAnimationFrame(() => r()));
    let y = window.scrollY;
    while (Math.abs(target - y) > 120) {
      y += Math.sign(target - y) * 120;
      window.scrollTo({ top: y, behavior: "instant" });
      await frame();
    }
    window.scrollTo({ top: target, behavior: "instant" });
    await frame();
  }, y);
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

async function throttle(context, page) {
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

function fillStep(stats, pct, file) {
  const step = {
    pct,
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
  return step;
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
  // Past the NDA gate (src/proxy.ts): the cookie is set before the first navigation.
  await context.addCookies([ndaCookie(baseUrl)]);
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

  if (vp.name === "phone") await throttle(context, page);

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
    const step = fillStep(await imageStats(statsPage, png), i * 10, file);
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

// Functional checks for the shared UI: the Skip link of every pinned chapter, reached by keyboard as a visitor would.
// Each link is visually hidden until it takes focus (globals.css `.skip-link`). From the top of the page, Tab must reach
// the first link (and, after each skip, Tab from its target must reach the next one, in page order); the moment it has
// focus it must show, with no transition, at the top of its stage with the stage at the top of the window (just below
// the header), at least 44 px tall and not under anything; Enter must land on its target with focus, just below the
// header; once focus moves on, the link hides again.
// Below 900 px the chapters don't pin and the links are not rendered (display: none), so there is nothing to check.
const MAX_TABS = 80; // Tab presses allowed to reach each Skip link (header, hero and section controls come first)

async function skipLinkState(page, href) {
  return page.evaluate((href) => {
    const a = [...document.querySelectorAll(".skip-link")].find((el) => el.getAttribute("href") === href);
    if (!a) return null;
    const r = a.getBoundingClientRect();
    const stage = a.closest(".pin-stage")?.getBoundingClientRect() ?? null;
    const cs = getComputedStyle(a);
    const hit = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2);
    const pad = parseFloat(getComputedStyle(document.documentElement).scrollPaddingTop) || 0;
    const zero = (list) => list.split(",").every((d) => parseFloat(d) === 0);
    return {
      focused: document.activeElement === a,
      width: Math.round(r.width),
      height: Math.round(r.height),
      top: Math.round(r.top),
      // Distance from the top of the pinned stage; the CSS puts it just below the header (= html's scroll padding).
      fromStageTop: stage ? Math.round(r.top - stage.top) : null,
      expectedFromStageTop: Math.round(pad),
      inView: r.top >= 0 && r.left >= 0 && r.bottom <= window.innerHeight && r.right <= window.innerWidth,
      onTop: Boolean(hit && (hit === a || a.contains(hit))),
      clipped: cs.clipPath !== "none",
      instant: zero(cs.transitionDuration) && cs.animationName === "none",
    };
  }, href);
}

// The sweet-spot claim and its ‡ marks stay in the tab order and the accessibility tree before the section is scrolled
// to (its words rise on opacity only, never visibility). From the top of the page, with nothing focused, Tab must reach
// every ‡ mark in #sweet-spot before anything after the section (a Skip link included), at every width, and each mark
// must be fully shown the moment it has focus (a focus inside the section finishes the rise at once).
const MAX_TABS_TO_SWEET = 20;

async function sweetSpotKeyboard(page) {
  const marks = await page.evaluate(() => document.querySelectorAll("#sweet-spot .footmark").length);
  if (!marks) return null;
  await scrollTo(page, 0);
  await page.waitForTimeout(300);
  await page.evaluate(() => document.activeElement instanceof HTMLElement && document.activeElement.blur());
  const problems = [];
  const seen = [];
  let tabs = 0;
  while (seen.length < marks && tabs < MAX_TABS_TO_SWEET) {
    await page.keyboard.press("Tab");
    tabs++;
    const at = await page.evaluate(() => {
      const a = document.activeElement;
      const section = document.getElementById("sweet-spot");
      if (!a || a === document.body || !section) return { kind: "none" };
      const name = (a.getAttribute("aria-label") || a.textContent || "").trim().replace(/\s+/g, " ").slice(0, 40);
      if (!section.contains(a)) {
        const after = Boolean(section.compareDocumentPosition(a) & Node.DOCUMENT_POSITION_FOLLOWING);
        return { kind: after ? "after" : "before", name, where: a.closest("section")?.id ?? a.closest("header,footer")?.tagName ?? "-" };
      }
      if (!a.classList.contains("footmark")) return { kind: "inside", name };
      // Effective opacity: the mark's own and every ancestor's up to the section (the rise moves its block).
      let opacity = 1;
      for (let e = a; e && e !== section; e = e.parentElement) opacity *= parseFloat(getComputedStyle(e).opacity);
      const r = a.getBoundingClientRect();
      return {
        kind: "mark",
        opacity: Number(opacity.toFixed(2)),
        visible: getComputedStyle(a).visibility === "visible",
        inView: r.width > 1 && r.bottom > 0 && r.top < window.innerHeight,
      };
    });
    if (at.kind === "after") {
      problems.push(`Tab reached "${at.name}" (${at.where}) after ${seen.length} of ${marks} sweet-spot ‡ mark(s)`);
      break;
    }
    if (at.kind !== "mark") continue;
    seen.push(at);
    if (!at.visible || at.opacity < 0.99) problems.push(`‡ mark ${seen.length} focused but not shown (visibility ${at.visible ? "visible" : "hidden"}, opacity ${at.opacity})`);
    if (!at.inView) problems.push(`‡ mark ${seen.length} focused out of view`);
  }
  if (seen.length < marks && !problems.length) problems.push(`only ${seen.length} of ${marks} sweet-spot ‡ mark(s) reached in ${MAX_TABS_TO_SWEET} Tab presses`);
  await page.evaluate(() => document.activeElement instanceof HTMLElement && document.activeElement.blur());
  return { ok: problems.length === 0, marks, reached: seen.length, tabs, problems };
}

async function interactionChecks(page) {
  const out = {};
  const sweet = await sweetSpotKeyboard(page);
  if (sweet) out.sweet = sweet;
  const { links, pins, wide } = await page.evaluate(() => ({
    links: [...document.querySelectorAll(".skip-link")]
      .filter((a) => getComputedStyle(a).display !== "none")
      .map((a) => ({ href: a.getAttribute("href"), chapter: a.closest(".pin")?.id ?? null })),
    pins: document.querySelectorAll(".pin").length,
    wide: window.innerWidth >= 900,
  }));
  if (!links.length) {
    // A page with pinned chapters must offer their Skip links wherever the chapters can pin.
    if (pins && wide) out.skip = { ok: false, links: [], problems: [`${pins} pinned chapter(s) but no Skip link rendered`] };
    return out;
  }

  // Start from the top of the page with nothing focused, so the first Tab goes to the first control.
  await scrollTo(page, 0);
  await page.waitForTimeout(500);
  await page.evaluate(() => document.activeElement instanceof HTMLElement && document.activeElement.blur());

  const problems = [];
  const results = [];
  for (const link of links) {
    const name = `${link.chapter ? `#${link.chapter}` : "?"} → ${link.href}`;
    const res = { ...link, tabs: 0 };
    results.push(res);
    const before = await skipLinkState(page, link.href);
    res.hiddenBefore = Boolean(before && !before.focused && before.width <= 1 && before.height <= 1);
    if (!res.hiddenBefore) problems.push(`${name}: visible before it has focus (${before?.width}x${before?.height} px)`);

    // Tab until this link has focus. Another Skip link first means the tab order skipped this one.
    let at = null;
    while (res.tabs < MAX_TABS) {
      await page.keyboard.press("Tab");
      res.tabs++;
      at = await page.evaluate(() => {
        const a = document.activeElement;
        return a && a.classList.contains("skip-link") ? a.getAttribute("href") : null;
      });
      if (at) break;
    }
    res.reached = at === link.href;
    if (!res.reached) {
      problems.push(at ? `${name}: Tab reached ${at} first` : `${name}: not reached in ${MAX_TABS} Tab presses`);
      break; // the rest of the walk would start from the wrong place
    }

    // Measured at once, in the frame focus arrived: it must already be fully shown.
    const shown = await skipLinkState(page, link.href);
    res.shown = shown;
    const shownProblems = [];
    if (shown.clipped || shown.width <= 1 || shown.height < 44) shownProblems.push(`not shown on focus (${shown.width}x${shown.height} px)`);
    if (!shown.instant) shownProblems.push("animates in (transition or animation)");
    if (!shown.inView) shownProblems.push(`out of view (top ${shown.top} px)`);
    // PinnedChapter brings the chapter's first screen into view on focus, so the link sits just below the header.
    else if (Math.abs(shown.top - shown.expectedFromStageTop) > 2) shownProblems.push(`not at the top of the window (top ${shown.top} px, expected ${shown.expectedFromStageTop})`);
    if (!shown.onTop) shownProblems.push("covered by another element");
    if (shown.fromStageTop === null || Math.abs(shown.fromStageTop - shown.expectedFromStageTop) > 2)
      shownProblems.push(`not at the top of its stage (${shown.fromStageTop} px from it, expected ${shown.expectedFromStageTop})`);
    problems.push(...shownProblems.map((p) => `${name}: ${p}`));

    // Enter: an instant jump to the target, which takes focus just below the fixed header (html's scroll-padding-top).
    await page.keyboard.press("Enter");
    await page.waitForTimeout(800);
    res.landed = await page.evaluate((id) => {
      const t = document.getElementById(id);
      const top = t ? t.getBoundingClientRect().top : null;
      const pad = parseFloat(getComputedStyle(document.documentElement).scrollPaddingTop) || 0;
      return { targetTop: top === null ? null : Math.round(top), expectedTop: Math.round(pad), focused: document.activeElement?.id === id };
    }, link.href.slice(1));
    const { targetTop, expectedTop, focused } = res.landed;
    if (!focused) problems.push(`${name}: Enter did not move focus to the target`);
    if (targetTop === null || Math.abs(targetTop - expectedTop) >= 40) problems.push(`${name}: target landed at ${targetTop} px, expected ${expectedTop}`);

    const after = await skipLinkState(page, link.href);
    res.hiddenAfter = Boolean(after && !after.focused && after.width <= 1 && after.height <= 1);
    if (!res.hiddenAfter) problems.push(`${name}: still visible after focus moved on`);
  }
  out.skip = { ok: problems.length === 0, links: results, problems };
  return out;
}

// ---------- the NDA gate (--gate) ----------
// Strings that must never reach a visitor before the NDA: a claim, a price and the stills.
const GATE_LEAKS = ["15 microns", "€", "/stills/"];
const GATE_EMAIL = "harness@kinetiq.invalid";

// One viewport without the cookie: the gate screen (fill rule, no leaks, no og:image, no stills requested), then the
// whole flow by keyboard: Tab to Yes, Not yet and Back, Yes, an invalid address (inline error), a valid one with
// Enter, and the real page at the same URL with the kq_nda cookie set as the contract says.
async function runGateCase(browser, statsPage, vp, mode) {
  const context = await browser.newContext({
    viewport: { width: vp.width, height: vp.height },
    deviceScaleFactor: vp.deviceScaleFactor,
    isMobile: vp.isMobile,
    hasTouch: vp.hasTouch,
    reducedMotion: mode.reducedMotion,
  });
  await context.addInitScript(metricsInit);
  const page = await context.newPage();
  const consoleErrors = [];
  const failedRequests = [];
  const stillsRequested = [];
  let opening = false; // after the valid email, the real page loads its stills by design
  page.on("console", (m) => m.type() === "error" && consoleErrors.push(m.text()));
  page.on("pageerror", (e) => consoleErrors.push(`pageerror: ${e.message}`));
  page.on("requestfailed", (r) => failedRequests.push(`${r.failure()?.errorText} ${r.url()}`));
  page.on("request", (r) => !opening && new URL(r.url()).pathname.startsWith("/stills/") && stillsRequested.push(r.url()));
  if (vp.name === "phone") await throttle(context, page);

  const id = `gate-${vp.name}-${mode.name}`;
  log(`${id}: loading ${targetUrl} without the NDA cookie`);
  const res = await page.goto(targetUrl, { waitUntil: "load", timeout: 120_000 });
  const html = res ? await res.text() : "";
  await page.waitForLoadState("networkidle", { timeout: 30_000 }).catch(() => {});
  await page.waitForTimeout(1200);
  const load = await page.evaluate(() => ({ ...window.__check }));

  const g = { steps: {} };
  const screen = await page.evaluate(() => ({
    gate: Boolean(document.querySelector("[data-nda-gate]")),
    url: location.pathname + location.search,
    title: document.title,
    ogImage: Boolean(document.querySelector('meta[property="og:image"], meta[name="twitter:image"]')),
    robots: document.querySelector('meta[name="robots"]')?.getAttribute("content") ?? "",
    h1: document.querySelectorAll("h1").length,
    overflowX: document.documentElement.scrollWidth > window.innerWidth + 1,
  }));
  Object.assign(g, screen, { status: res?.status() ?? 0, leaks: GATE_LEAKS.filter((t) => html.includes(t)) });

  const steps = [];
  const shoot = async (name, pct) => {
    const file = `${id}-${name}.png`;
    const png = await capture(page, join(outDir, file));
    steps.push(fillStep(await imageStats(statsPage, png), pct, file));
  };
  const active = () => page.evaluate(() => document.activeElement?.getAttribute("data-nda") ?? document.activeElement?.id ?? "");
  const settle = () => page.waitForTimeout(vp.name === "phone" ? 900 : 500);

  await shoot("1-ask", 0);
  // Keyboard only from here: Tab to Yes, then Not yet, its message, Back, and back to Yes.
  for (let i = 0; i < 8 && (await active()) !== "yes"; i++) await page.keyboard.press("Tab");
  g.steps.tabToYes = (await active()) === "yes";
  await page.keyboard.press("Tab");
  g.steps.tabToNo = (await active()) === "no";
  await page.keyboard.press("Enter");
  await settle();
  g.steps.notYetFocus = (await active()) === "message";
  await shoot("2-not-yet", 30);
  await page.keyboard.press("Tab");
  g.steps.tabToBack = (await active()) === "back";
  await page.keyboard.press("Enter");
  await settle();
  g.steps.backFocus = (await active()) === "no";
  await page.keyboard.press("Shift+Tab");
  await page.keyboard.press("Enter");
  await settle();
  g.steps.emailFocus = (await active()) === "nda-email";
  await shoot("3-email", 60);
  await page.keyboard.type("not-an-address");
  await page.keyboard.press("Enter");
  await settle();
  g.steps.invalidShown = await page.evaluate(
    () => Boolean(document.getElementById("nda-email-error")?.textContent?.trim()) && document.getElementById("nda-email")?.getAttribute("aria-invalid") === "true",
  );
  await shoot("4-invalid", 80);
  const after = await page.evaluate(() => ({ ...window.__check }));
  await page.keyboard.press(process.platform === "darwin" ? "Meta+A" : "Control+A");
  await page.keyboard.type(GATE_EMAIL);
  const reloaded = page.waitForEvent("load", { timeout: 120_000 });
  opening = true;
  await page.keyboard.press("Enter");
  await reloaded.catch(() => {});
  await page.waitForLoadState("networkidle", { timeout: 30_000 }).catch(() => {});
  await page.waitForTimeout(1500);
  const opened = await page.evaluate(() => ({
    url: location.pathname + location.search,
    gate: Boolean(document.querySelector("[data-nda-gate]")),
    title: document.title,
    main: Boolean(document.getElementById("main")),
  }));
  await capture(page, join(outDir, `${id}-5-opened.png`));
  const cookie = (await context.cookies(baseUrl)).find((c) => c.name === NDA_COOKIE);
  const decoded = cookie ? safeJson(Buffer.from(cookie.value, "base64url").toString("utf8")) : null;
  const yearAhead = Date.now() / 1000 + 365 * 24 * 3600;
  g.opened = { ...opened, sameUrl: opened.url === screen.url };
  g.cookie = cookie
    ? {
        httpOnly: cookie.httpOnly,
        sameSite: cookie.sameSite,
        path: cookie.path,
        secure: cookie.secure,
        days: Math.round((cookie.expires - Date.now() / 1000) / 86400),
        email: decoded?.email === GATE_EMAIL,
        at: typeof decoded?.at === "string" && !Number.isNaN(Date.parse(decoded.at)),
      }
    : null;
  const cookieOk =
    g.cookie &&
    g.cookie.httpOnly &&
    g.cookie.sameSite === "Lax" &&
    g.cookie.path === "/" &&
    g.cookie.secure === baseUrl.startsWith("https:") &&
    Math.abs(cookie.expires - yearAhead) < 2 * 86400 &&
    g.cookie.email &&
    g.cookie.at;
  g.problems = [
    g.status !== 200 ? `gate answered ${g.status}` : null,
    !g.gate ? "the gate did not show" : null,
    g.url !== new URL(targetUrl).pathname + new URL(targetUrl).search ? `address bar changed to ${g.url}` : null,
    g.title !== "KINETIQ" ? `title "${g.title}"` : null,
    g.ogImage ? "og:image or twitter:image present" : null,
    !/noindex/.test(g.robots) ? "not noindex" : null,
    g.h1 !== 1 ? `${g.h1} h1 elements` : null,
    g.leaks.length ? `HTML contains ${g.leaks.join(", ")}` : null,
    stillsRequested.length ? `requested ${stillsRequested.length} still(s)` : null,
    ...Object.entries(g.steps).filter(([, ok]) => !ok).map(([k]) => `keyboard step failed: ${k}`),
    opened.gate || !opened.main ? "the real page did not open after the email" : null,
    !g.opened.sameUrl ? `opened at ${opened.url}, not ${screen.url}` : null,
    !cookieOk ? `kq_nda cookie wrong: ${JSON.stringify(g.cookie)}` : null,
  ].filter(Boolean);
  g.ok = g.problems.length === 0;
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
    sceneState: null,
    sceneStd: null,
    overflowX: screen.overflowX,
    interactions: { gate: g },
    consoleErrors,
    failedRequests,
    blankSteps: steps.filter((s) => s.blank).map((s) => s.pct),
    fillSteps: steps.filter((s) => s.fillFail.length).map((s) => `${s.file} (${s.fillFail.join(", ")})`),
    steps,
    libs: null,
  };
}

function safeJson(text) {
  try {
    return JSON.parse(text);
  } catch {
    return null;
  }
}

// Server side of the gate, once per run, from a cookie-less HTTP client (no browser): pages are the gate,
// assets and APIs are an empty 403, /nda with the cookie goes to /, and POST /api/nda keeps its contract.
async function gateServerChecks() {
  const api = await apiRequest.newContext({ baseURL: baseUrl, proxy: proxyConfig() });
  const withCookie = { Cookie: ndaHeader() };
  const checks = [];
  const check = (name, ok, detail) => checks.push({ name, ok: Boolean(ok), detail });
  try {
    const stills = JSON.parse(readFileSync(join(process.cwd(), "src/content/stills.generated.json"), "utf8"));
    const [key, size] = Object.entries(stills).find(([, v]) => v.hash && v.widths?.length) ?? [];
    const still = key ? `/stills/${key}-${size.widths[0]}.${size.hash}.avif` : null;
    const og = existsSync(join(process.cwd(), "public/stills/og.jpg")) ? "/stills/og.jpg" : null;

    const page = await api.get(pagePath);
    const body = await page.text();
    check(`GET ${pagePath} without cookie is the gate`, page.status() === 200 && body.includes("data-nda-gate") && !GATE_LEAKS.some((t) => body.includes(t)), `${page.status()}`);
    for (const path of [still, og, "/CREDITS.md"].filter(Boolean)) {
      const r = await api.get(path);
      check(`GET ${path} without cookie: 403, empty`, r.status() === 403 && (await r.body()).length === 0, `${r.status()}`);
      const c = await api.get(path, { headers: withCookie });
      check(`GET ${path} with cookie: 200`, c.status() === 200, `${c.status()}`);
    }
    for (const [method, path] of [["post", "/api/reserve"], ["get", "/api/reserve"], ["post", "/api/invite"]]) {
      const r = method === "post" ? await api.post(path, { data: {} }) : await api.get(path);
      check(`${method.toUpperCase()} ${path} without cookie: 403, empty`, r.status() === 403 && (await r.body()).length === 0, `${r.status()}`);
    }
    const credits = await api.get("/credits");
    check("GET /credits without cookie is the gate", credits.status() === 200 && (await credits.text()).includes("data-nda-gate"), `${credits.status()}`);
    const nda = await api.get("/nda", { headers: withCookie, maxRedirects: 0 });
    const to = nda.headers().location ?? "";
    check("GET /nda with cookie redirects to /", [307, 308].includes(nda.status()) && new URL(to, baseUrl).pathname === "/", `${nda.status()} ${to}`);
    const bad = await api.post("/api/nda", { data: { email: "not-an-address" } });
    const badJson = safeJson(await bad.text());
    check("POST /api/nda with a bad address: ok false, no cookie", badJson?.ok === false && !bad.headers()["set-cookie"], `${bad.status()}`);
    const good = await api.post("/api/nda", { data: { email: GATE_EMAIL } });
    const setCookie = good.headers()["set-cookie"] ?? "";
    const flags = /^kq_nda=[A-Za-z0-9_-]+;/.test(setCookie) && /HttpOnly/i.test(setCookie) && /SameSite=Lax/i.test(setCookie) && /Path=\//.test(setCookie) && /Max-Age=31536000/.test(setCookie) && /Secure/i.test(setCookie) === baseUrl.startsWith("https:");
    check("POST /api/nda sets kq_nda (HttpOnly, SameSite=Lax, Path=/, Max-Age 365 days)", good.status() === 200 && flags, setCookie.replace(/kq_nda=[^;]+/, "kq_nda=…"));
  } finally {
    await api.dispose();
  }
  return checks;
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
    if (r.interactions?.skip && !r.interactions.skip.ok) failures.push(`${r.id}: Skip links: ${r.interactions.skip.problems.join("; ")}`);
    if (r.interactions?.sweet && !r.interactions.sweet.ok) failures.push(`${r.id}: sweet-spot ‡ by Tab: ${r.interactions.sweet.problems.join("; ")}`);
    if (r.interactions?.gate && !r.interactions.gate.ok) failures.push(`${r.id}: gate: ${r.interactions.gate.problems.join("; ")}`);
    if (r.fillSteps.length) failures.push(`${r.id}: fill rule broken at ${r.fillSteps.join("; ")}`);
  }
  return failures;
}

function markdown(results, failures, server = []) {
  const rows = results.map(
    (r) =>
      `| ${r.id} | ${r.lcpMs} (${r.lcpElement || "?"}) | ${r.clsAfterScroll} | ${r.longFrames}/${r.frames} (worst ${r.worstFrameMs} ms) | ${r.sceneState ?? "-"} (${r.sceneStd ?? "-"}) | ${r.interactions?.skip ? (r.interactions.skip.ok ? `ok (${r.interactions.skip.links.length}, by Tab)` : "FAIL") : r.interactions?.gate ? (r.interactions.gate.ok ? "gate ok" : "gate FAIL") : "-"}${r.interactions?.sweet ? (r.interactions.sweet.ok ? `; ‡ ok (${r.interactions.sweet.reached}, by Tab)` : "; ‡ FAIL") : ""} | ${r.consoleErrors.length} | ${r.blankSteps.length ? r.blankSteps.join(",") : "none"} | ${r.fillSteps.length ? r.fillSteps.length : "ok"} |`,
  );
  return [
    `# Check report: ${targetUrl}`,
    "",
    `Run at ${new Date().toISOString()}. Phone runs use 4x CPU slowdown, 150 ms RTT, 1.6 Mbps.`,
    "Long frames are measured in headless Chromium with software WebGL, so treat them as a smoke signal, not a device measurement.",
    "",
    "| Case | LCP ms (element) | CLS | Long frames >50 ms | Scene (contrast) | Skip link / gate | Console errors | Blank steps | Fill rule |",
    "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ...rows,
    "",
    ...(server.length ? ["## Gate, server side (no cookie unless stated)", "", ...server.map((c) => `- ${c.ok ? "ok" : "FAIL"}: ${c.name} (${c.detail})`), ""] : []),
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
  let serverChecks = [];
  try {
    for (const vp of VIEWPORTS.filter((v) => !args.only || v.name === args.only)) {
      for (const mode of MODES.filter((m) => !args.mode || m.name === args.mode)) {
        const browser = await launchBrowser();
        try {
          const statsPage = await (await browser.newContext()).newPage();
          results.push(await (gateMode ? runGateCase : runCase)(browser, statsPage, vp, mode));
        } finally {
          await browser.close();
        }
      }
    }
    if (gateMode) serverChecks = await gateServerChecks();
  } finally {
    if (server) {
      try {
        process.kill(-server.pid);
      } catch {}
    }
  }

  const failures = study ? [] : [...evaluate(results), ...serverChecks.filter((c) => !c.ok).map((c) => `gate server: ${c.name} (${c.detail})`)];
  writeFileSync(join(outDir, "report.json"), JSON.stringify({ baseUrl, results, serverChecks, failures }, null, 2));
  writeFileSync(join(outDir, "report.md"), markdown(results, failures, serverChecks));
  console.log(markdown(results, failures, serverChecks));
  log(`screenshots and report in ${outDir}`);
  if (failures.length) process.exit(1);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
