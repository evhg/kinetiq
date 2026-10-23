// Export a Blender frame sequence (the hero's swivel) to WebP frames for the hero's scrub canvas (Hero.tsx).
// Usage: node scripts/sequence.mjs <sequences dir> [name ...] [--frames=36]
// Each <sequences dir>/<name>/ holds 16-bit PNG frames f000.png, f001.png, ... (desktop 1920x1080, phone
// 1080x1920; frame 0 is the matching still's composition). A folder is exported only once all its frames are there and
// decode (one still rendering is skipped, so it is safe to run while Blender works).
// Only the part of the frame that ever changes is kept: the union of every frame's difference from frame 0, padded,
// so the canvas draws that rectangle over the still and the rest of the frame stays the still's own pixels.
// Writes public/stills/seq/<name>/<NNN>-<width>.<hash>.webp (one hash per sequence: the names change with the bytes,
// served private and immutable to cleared visitors, next.config.ts) and src/content/sequences.generated.json.
// WebP only: AVIF was measured at 4 to 6% smaller on these frames (2026-10-23), not worth a second set or its decode.
import { createHash } from "node:crypto";
import { existsSync, mkdirSync, readFileSync, readdirSync, rmSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import sharp from "sharp";

const root = new URL("..", import.meta.url).pathname;
const args = process.argv.slice(2);
const flags = Object.fromEntries(args.filter((a) => a.startsWith("--")).map((a) => a.slice(2).split("=")));
const [src, ...only] = args.filter((a) => !a.startsWith("--"));
if (!src) throw new Error("Pass the sequences directory.");
const FRAMES = Number(flags.frames ?? 36);
/** Exported widths of the whole frame, by orientation (the crop scales with them). */
const WIDTHS = { landscape: [1280, 1920], portrait: [720, 1080] };
const QUALITY = 84;
/** The change mask: frames compared at 1/8 size, a mean step above this counts as change, then padded (source px). */
const SCALE = 8;
const THRESHOLD = 2;
const PAD = 32;
/** Crop edges snap to this many source pixels, so every exported width scales them to whole pixels. */
const SNAP = 24;

const outRoot = join(root, "public/stills/seq");
const manifestFile = join(root, "src/content/sequences.generated.json");
const manifest = existsSync(manifestFile) ? JSON.parse(readFileSync(manifestFile, "utf8")) : {};
const frameFile = (dir, i) => join(dir, `f${String(i).padStart(3, "0")}.png`);

// Triangular-PDF dither of about one 8-bit step (as scripts/stills.mjs): no banding in the dark gradients.
async function dithered(img, seed0) {
  const { data, info } = await img.toColourspace("rgb16").raw({ depth: "ushort" }).toBuffer({ resolveWithObject: true });
  const px = new Uint16Array(data.buffer, data.byteOffset, data.length / 2);
  const out8 = Buffer.alloc(px.length);
  let seed = seed0;
  const rnd = () => ((seed = (seed * 1664525 + 1013904223) >>> 0) / 4294967296);
  for (let i = 0; i < px.length; i++) {
    const v = px[i] / 257 + (rnd() - rnd()) * 0.9;
    out8[i] = v < 0 ? 0 : v > 255 ? 255 : Math.round(v);
  }
  return sharp(out8, { raw: { width: info.width, height: info.height, channels: info.channels } });
}

const small = async (file, W) =>
  (await sharp(file).removeAlpha().greyscale().resize({ width: Math.round(W / SCALE) }).raw().toBuffer({ resolveWithObject: true }));

const names = readdirSync(src, { withFileTypes: true })
  .filter((d) => d.isDirectory() && !d.name.startsWith("_"))
  .map((d) => d.name)
  .filter((n) => !only.length || only.includes(n))
  .sort();

for (const name of names) {
  const dir = join(src, name);
  const missing = [...Array(FRAMES).keys()].filter((i) => !existsSync(frameFile(dir, i)));
  if (missing.length) {
    console.log(`skip ${name}: ${FRAMES - missing.length} of ${FRAMES} frames`);
    continue;
  }
  let meta;
  try {
    meta = await Promise.all([...Array(FRAMES).keys()].map((i) => sharp(frameFile(dir, i)).metadata()));
  } catch (e) {
    console.log(`skip ${name}: a frame does not decode yet (${e.message})`);
    continue;
  }
  const { width: W, height: H } = meta[0];
  if (meta.some((m) => m.width !== W || m.height !== H)) throw new Error(`${name}: frames differ in size`);
  const widths = WIDTHS[W >= H ? "landscape" : "portrait"].filter((w) => w <= W);

  // The change mask's bounding box over every frame.
  const base = await small(frameFile(dir, 0), W);
  const { width: sw, height: sh } = base.info;
  let [x0, y0, x1, y1] = [sw, sh, -1, -1];
  for (let i = 1; i < FRAMES; i++) {
    const f = await small(frameFile(dir, i), W);
    for (let y = 0; y < sh; y++)
      for (let x = 0; x < sw; x++)
        if (Math.abs(f.data[y * sw + x] - base.data[y * sw + x]) > THRESHOLD) {
          if (x < x0) x0 = x;
          if (x > x1) x1 = x;
          if (y < y0) y0 = y;
          if (y > y1) y1 = y;
        }
  }
  if (x1 < 0) throw new Error(`${name}: no frame differs from frame 0`);
  const snapDown = (v) => Math.max(0, Math.floor(v / SNAP) * SNAP);
  const left = snapDown((x0 * W) / sw - PAD);
  const top = snapDown((y0 * H) / sh - PAD);
  const snapUp = (v, max) => Math.min(max, Math.ceil(v / SNAP) * SNAP);
  const right = snapUp(((x1 + 1) * W) / sw + PAD, W);
  const bottom = snapUp(((y1 + 1) * H) / sh + PAD, H);
  const crop = { x: left, y: top, w: right - left, h: bottom - top };

  // Encode every frame at every width.
  const encoded = [];
  for (let i = 0; i < FRAMES; i++) {
    const img = sharp(frameFile(dir, i)).removeAlpha().extract({ left: crop.x, top: crop.y, width: crop.w, height: crop.h });
    const d = await dithered(img, 1234567 + i);
    const flat = await d.png({ compressionLevel: 0 }).toBuffer();
    for (const w of widths) {
      const cw = Math.round((crop.w * w) / W);
      const ch = Math.round((crop.h * w) / W);
      const buf = await sharp(flat).resize({ width: cw, height: ch, fit: "fill", kernel: "lanczos3" }).webp({ quality: QUALITY, effort: 5, smartSubsample: true }).toBuffer();
      encoded.push({ i, w, buf });
    }
  }
  const digest = createHash("sha256");
  for (const e of encoded) digest.update(e.buf);
  const hash = digest.digest("hex").slice(0, 10);

  const out = join(outRoot, name);
  rmSync(out, { recursive: true, force: true });
  mkdirSync(out, { recursive: true });
  const bytes = Object.fromEntries(widths.map((w) => [w, 0]));
  for (const e of encoded) {
    writeFileSync(join(out, `${String(e.i).padStart(3, "0")}-${e.w}.${hash}.webp`), e.buf);
    bytes[e.w] += e.buf.length;
  }
  manifest[name] = { frames: FRAMES, w: W, h: H, crop, widths, hash, bytes };
  console.log(
    `${name}: ${FRAMES} frames ${W}x${H}, crop ${crop.w}x${crop.h} at ${crop.x},${crop.y}, ` +
      widths.map((w) => `${w}: ${Math.round(bytes[w] / 1024)} KB`).join(", ") +
      `, hash ${hash}`,
  );
}
const sorted = Object.fromEntries(Object.keys(manifest).sort().map((k) => [k, manifest[k]]));
writeFileSync(manifestFile, JSON.stringify(sorted, null, 1) + "\n");
