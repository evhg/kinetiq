// Load budget (2026-11-01): how long the whole home page takes to load on the phone profile (4x CPU, 150 ms RTT,
// 1.6 Mbps, as check.mjs), read like a visitor would: the page loads, the visitor reads the first screen, then scrolls
// through the page a screen at a time, lingering on each, to the end. Every request is recorded with its bytes on the
// wire (CDP encodedDataLength), so the report gives the bytes by type (document, script, font, still, swivel frame)
// and the time the last byte arrived after navigation (the page is "complete" when nothing has loaded for 4 s).
// Usage: node scripts/load-budget.mjs <base url> [--device=iphone|iphone-short|ipad-pro|desktop] [--feel=command|pace]
//   [--dwell=quiet|<ms per screen>] (default quiet: each screen waits for the network) [--json=<file>]
import { writeFileSync } from "node:fs";
import { chromium } from "@playwright/test";
import { ndaCookie } from "./nda-cookie.mjs";

const args = process.argv.slice(2);
const flags = Object.fromEntries(args.filter((a) => a.startsWith("--")).map((a) => a.slice(2).split("=")));
const [base = "http://127.0.0.1:3100/"] = args.filter((a) => !a.startsWith("--"));
const DEVICES = {
  iphone: { width: 390, height: 844, dpr: 3, mobile: true },
  "iphone-short": { width: 390, height: 664, dpr: 3, mobile: true },
  "ipad-pro": { width: 1024, height: 1366, dpr: 2, mobile: true },
  desktop: { width: 1440, height: 900, dpr: 1, mobile: false },
};
const device = DEVICES[flags.device ?? "iphone"];
const DWELL = Number(flags.dwell) || 1200;
const THROTTLE = { cpuRate: 4, latency: 150, down: (1.6 * 1024 * 1024) / 8, up: (750 * 1024) / 8 };

// A remote site goes through the sandbox's HTTPS proxy (as check.mjs); a local server never does.
const local = ["localhost", "127.0.0.1", "[::1]"].includes(new URL(base).hostname);
const browser = await chromium.launch({
  args: ["--disable-gpu-compositing"],
  proxy: !local && process.env.HTTPS_PROXY ? { server: process.env.HTTPS_PROXY } : undefined,
  executablePath: process.env.PLAYWRIGHT_CHROMIUM_PATH || undefined,
});
const context = await browser.newContext({
  viewport: { width: device.width, height: device.height },
  deviceScaleFactor: device.dpr,
  isMobile: device.mobile,
  hasTouch: device.mobile,
});
await context.addCookies([ndaCookie(base)]);
if (flags.feel) await context.addInitScript((f) => localStorage.setItem("kq-feel", f), flags.feel);
await context.addInitScript(() => {
  window.__lcp = 0;
  new PerformanceObserver((l) => {
    for (const e of l.getEntries()) window.__lcp = e.startTime;
  }).observe({ type: "largest-contentful-paint", buffered: true });
});
const page = await context.newPage();
const cdp = await context.newCDPSession(page);
await cdp.send("Network.enable");
await cdp.send("Network.setCacheDisabled", { cacheDisabled: true });
await cdp.send("Emulation.setCPUThrottlingRate", { rate: THROTTLE.cpuRate });
await cdp.send("Network.emulateNetworkConditions", {
  offline: false,
  latency: THROTTLE.latency,
  downloadThroughput: THROTTLE.down,
  uploadThroughput: THROTTLE.up,
});

const reqs = new Map();
let t0 = 0;
let lastByte = 0;
cdp.on("Network.requestWillBeSent", (e) => {
  if (!t0) t0 = e.timestamp;
  reqs.set(e.requestId, { url: e.request.url, type: e.type, start: e.timestamp - t0, bytes: 0, done: false });
});
cdp.on("Network.responseReceived", (e) => {
  const r = reqs.get(e.requestId);
  if (r) r.mime = e.response.mimeType;
});
cdp.on("Network.loadingFinished", (e) => {
  const r = reqs.get(e.requestId);
  if (!r) return;
  r.bytes = e.encodedDataLength;
  r.done = true;
  r.end = e.timestamp - t0;
  lastByte = Math.max(lastByte, r.end);
});
cdp.on("Network.loadingFailed", (e) => {
  const r = reqs.get(e.requestId);
  if (r) r.failed = e.canceled ? "cancelled" : e.errorText;
});

const wait = (ms) => new Promise((r) => setTimeout(r, ms));
await page.goto(new URL("/", base).href, { waitUntil: "load", timeout: 120000 });
const loadAt = lastByte;
await wait(2500);
const lcp = await page.evaluate(() => window.__lcp);
// Scroll a screen at a time, lingering, like a visitor reading the page; by default (--dwell=quiet) each screen
// waits until the network is quiet, so every lazy asset and every swivel frame is requested and arrives (nothing is
// cancelled by scrolling past it), and the network's busy time is the page's complete-load time.
const quietStep = flags.dwell === undefined || flags.dwell === "quiet";
const inflight = () => [...reqs.values()].some((r) => !r.done && !r.failed);
let height = await page.evaluate(() => document.documentElement.scrollHeight);
for (let y = 0; y < height; y += device.height * 0.8) {
  await page.evaluate((v) => window.scrollTo(0, v), y);
  if (device.mobile) await page.dispatchEvent("body", "touchstart").catch(() => {});
  if (quietStep) {
    await wait(600);
    for (let q = 0, t = 0; q < 600 && t < 30000; t += 100) {
      await wait(100);
      q = inflight() ? 0 : q + 100;
    }
  } else await wait(DWELL);
  height = await page.evaluate(() => document.documentElement.scrollHeight);
}
// Then wait for the network to fall silent (4 s with nothing finishing and nothing in flight).
for (let quiet = 0; quiet < 4000; ) {
  const before = lastByte;
  await wait(500);
  const inflight = [...reqs.values()].some((r) => !r.done && !r.failed);
  quiet = before === lastByte && !inflight ? quiet + 500 : 0;
}
// The network's busy time: the union of every request's time in flight (the time to load everything, had the
// visitor scrolled just ahead of the loads).
const spans = [...reqs.values()].filter((r) => r.done).map((r) => [r.start, r.end]).sort((a, b) => a[0] - b[0]);
let busy = 0;
let [cs, ce] = [0, 0];
for (const [a, b] of spans) {
  if (a > ce) {
    busy += ce - cs;
    [cs, ce] = [a, b];
  } else ce = Math.max(ce, b);
}
busy += ce - cs;

const kind = (r) => {
  const u = r.url;
  if (u.includes("/stills/seq/")) return `frames ${u.split("/stills/seq/")[1].split("/")[0]}`;
  if (u.includes("/stills/")) return "stills";
  if (r.type === "Script") return "script";
  if (r.type === "Font") return "font";
  if (r.type === "Stylesheet") return "css";
  if (r.type === "Document") return "document";
  if (r.type === "Image") return "image";
  return r.type ?? "other";
};
const groups = {};
for (const r of reqs.values()) {
  if (!r.done) continue;
  const g = (groups[kind(r)] ??= { n: 0, bytes: 0, last: 0 });
  g.n++;
  g.bytes += r.bytes;
  g.last = Math.max(g.last, r.end);
}
const total = Object.values(groups).reduce((a, g) => a + g.bytes, 0);
const cancelled = [...reqs.values()].filter((r) => r.failed).length;
const report = {
  base,
  device: flags.device ?? "iphone",
  feel: flags.feel ?? "default",
  lcpMs: Math.round(lcp),
  loadEventS: Number(loadAt.toFixed(1)),
  completeS: Number(lastByte.toFixed(1)),
  busyS: Number(busy.toFixed(1)),
  totalKB: Math.round(total / 1024),
  wireSecondsAt1600kbps: Number((total / THROTTLE.down).toFixed(1)),
  failedOrCancelled: cancelled,
  groups: Object.fromEntries(
    Object.entries(groups)
      .sort((a, b) => b[1].bytes - a[1].bytes)
      .map(([k, g]) => [k, { n: g.n, KB: Math.round(g.bytes / 1024), lastS: Number(g.last.toFixed(1)) }]),
  ),
};
console.log(JSON.stringify(report, null, 1));
if (flags.json) writeFileSync(flags.json, JSON.stringify({ ...report, requests: [...reqs.values()] }, null, 1));
await browser.close();
