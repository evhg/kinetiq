// Export a Blender frame sequence (the swivels) to AVIF and WebP frames for the scrub canvas (media/Swivel.tsx).
// Usage: node scripts/sequence.mjs <sequences dir> [name ...] [--frames=N] [--formats=avif,webp] [--quality=84]
//   [--avif-quality=58] [--keep=N] [--out=<dir>]
// (--keep=N: export N frames spread evenly over the source's, first and last kept; e.g. Command's 60-frame K02 phone
// sequence as 45, like Pace's, for the phone load budget; the manifest then names each kept frame's source frame)
// (the phone sets, *-phone, are exported with --avif-quality=50 since 2026-11-01; the desktop sets keep 58:
//   node scripts/sequence.mjs <dir> K01-swivel-command-phone ... --formats=avif --avif-quality=50 [--keep=45])
// (--formats: the encodings to write now; any other encoding already exported for the sequence is kept, if its crop
// is unchanged, so AVIF can be added to a sequence without re-encoding its WebP)
// (--out writes the frames and manifest under another root, for trials: <dir>/seq/... and <dir>/sequences.json)
// Each <sequences dir>/<name>/ holds 16-bit PNG frames f000.png, f001.png, ... (desktop 1920x1080, phone
// 1080x1920; frame 0 is the matching still's composition). A folder is exported only once all its frames are there and
// decode (one still rendering is skipped, so it is safe to run while Blender works).
// Only the part of the frame that ever changes is kept: the union of every frame's difference from frame 0, padded,
// so the canvas draws that rectangle over the still and the rest of the frame stays the still's own pixels.
// Writes public/stills/seq/<name>/<NNN>-<width>.<hash>.<avif|webp> (one hash per sequence and format: the names change
// with the bytes, served private and immutable to cleared visitors, next.config.ts) and
// src/content/sequences.generated.json (per sequence: frames, size, crop, widths, and `formats`: hash, quality, bytes).
// AVIF and WebP (2026-11-01, the phone load budget): compared at the same quality number AVIF was only 4 to 6% smaller
// (2026-10-23), but compared at the same sharpness (SSIM against the dithered frame, and side-by-side crops at 100%
// on a 3x screen) AVIF 58 matches WebP 84 at about 40% fewer bytes. Swivel.tsx takes AVIF where the browser decodes it
// (iOS 16+) and WebP elsewhere, so both are exported.
import { createHash } from "node:crypto";
import { existsSync, mkdirSync, readFileSync, readdirSync, rmSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import sharp from "sharp";

const root = new URL("..", import.meta.url).pathname;
const args = process.argv.slice(2);
const flags = Object.fromEntries(args.filter((a) => a.startsWith("--")).map((a) => a.slice(2).split("=")));
const [src, ...only] = args.filter((a) => !a.startsWith("--"));
if (!src) throw new Error("Pass the sequences directory.");
/** Frames per sequence: --frames=N, else every f000.png ... in the folder (a frames.json from Blender may name N). */
const FRAMES_FLAG = flags.frames ? Number(flags.frames) : 0;
const KEEP = flags.keep ? Number(flags.keep) : 0;
/**
 * Exported widths of the whole frame, by orientation (the crop scales with them), up to the master's own width.
 * 2026-10-29 (owner: the swivels looked low-res on iPad and iPhone): Swivel.tsx picks the narrowest export whose crop is
 * as wide as the canvas on screen in device pixels (iPhone 3x, iPad 2x), so the set runs up to the masters' widths:
 * portrait 1170 (an iPhone's 390 x 3), 1440 and 2160 (an iPad in portrait), landscape to 2560, and
 * 3840 and 5120 for 5120 x 2880 masters (owner, 2026-11-03: a 5K screen draws 2560 x 1440 CSS at DPR 2).
 */
const WIDTHS = { landscape: [1280, 1920, 2560, 3840, 5120], portrait: [828, 1170, 1440, 2160] };
/** Quality by format: WebP 84 (the 2026-10-29 pass); AVIF 58, as sharp as WebP 84 on these frames (above). */
const QUALITY = { webp: Number(flags.quality ?? 84), avif: Number(flags["avif-quality"] ?? 58) };
/** avif and webp: Safari decodes WebP everywhere the swivel plays (iOS 14+), AVIF from iOS 16. */
const FORMATS = (flags.formats ?? flags.format ?? "avif,webp").split(",");
for (const f of FORMATS) if (!(f in QUALITY)) throw new Error(`Unknown format ${f}`);
/** The change mask: frames compared at 1/8 size, a mean step above this counts as change, then padded (source px). */
const SCALE = 8;
const THRESHOLD = 2;
const PAD = 32;
/** Crop edges snap to this many source pixels, so every exported width scales them to whole pixels. */
const SNAP = 24;

const outRoot = flags.out ? join(flags.out, "seq") : join(root, "public/stills/seq");
const manifestFile = flags.out ? join(flags.out, "sequences.json") : join(root, "src/content/sequences.generated.json");
const manifest = existsSync(manifestFile) ? JSON.parse(readFileSync(manifestFile, "utf8")) : {};
// Entries from before 2026-11-01 name one encoding (hash, bytes, format): as `formats`.
for (const e of Object.values(manifest))
  if (!e.formats) {
    e.formats = { [e.format ?? "webp"]: { hash: e.hash, bytes: e.bytes } };
    delete e.hash;
    delete e.bytes;
    delete e.format;
  }
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
  let FRAMES = FRAMES_FLAG;
  if (!FRAMES) while (existsSync(frameFile(dir, FRAMES))) FRAMES++;
  if (FRAMES < 2) {
    console.log(`skip ${name}: no frames`);
    continue;
  }
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

  // The frames exported: every one, or --keep of them spread evenly (source frame round(k * (FRAMES - 1) / (KEEP - 1))).
  const OUT = KEEP && KEEP < FRAMES ? KEEP : FRAMES;
  const source = [...Array(OUT).keys()].map((k) => (OUT === FRAMES ? k : Math.round((k * (FRAMES - 1)) / (OUT - 1))));
  // Encode every frame at every width, in every format asked for.
  const encoded = Object.fromEntries(FORMATS.map((f) => [f, []]));
  for (let i = 0; i < OUT; i++) {
    const img = sharp(frameFile(dir, source[i])).removeAlpha().extract({ left: crop.x, top: crop.y, width: crop.w, height: crop.h });
    const d = await dithered(img, 1234567 + source[i]);
    const flat = await d.png({ compressionLevel: 0 }).toBuffer();
    for (const w of widths) {
      const cw = Math.round((crop.w * w) / W);
      const ch = Math.round((crop.h * w) / W);
      const resized = await sharp(flat).resize({ width: cw, height: ch, fit: "fill", kernel: "lanczos3" }).raw().toBuffer({ resolveWithObject: true });
      for (const format of FORMATS) {
        const img = sharp(resized.data, { raw: resized.info });
        const buf = await (format === "avif"
          ? img.avif({ quality: QUALITY.avif, effort: 5, chromaSubsampling: "4:2:0" })
          : img.webp({ quality: QUALITY.webp, effort: 5, smartSubsample: true })
        ).toBuffer();
        encoded[format].push({ i, w, buf });
      }
    }
  }

  const out = join(outRoot, name);
  mkdirSync(out, { recursive: true });
  // The other encodings already exported stay if they share this crop and frame count; otherwise they go.
  const prev = manifest[name];
  const keep =
    prev && prev.frames === OUT && prev.w === W && prev.h === H && JSON.stringify([prev.crop, prev.widths]) === JSON.stringify([crop, widths])
      ? Object.fromEntries(Object.entries(prev.formats).filter(([f]) => !FORMATS.includes(f)))
      : {};
  for (const file of readdirSync(out)) if (!Object.keys(keep).includes(file.split(".").pop())) rmSync(join(out, file));
  const formats = { ...keep };
  for (const format of FORMATS) {
    const digest = createHash("sha256");
    for (const e of encoded[format]) digest.update(e.buf);
    const hash = digest.digest("hex").slice(0, 10);
    const bytes = Object.fromEntries(widths.map((w) => [w, 0]));
    for (const e of encoded[format]) {
      writeFileSync(join(out, `${String(e.i).padStart(3, "0")}-${e.w}.${hash}.${format}`), e.buf);
      bytes[e.w] += e.buf.length;
    }
    formats[format] = { hash, quality: QUALITY[format], bytes };
    console.log(
      `${name} ${format}: ${OUT} of ${FRAMES} frames ${W}x${H}, crop ${crop.w}x${crop.h} at ${crop.x},${crop.y}, ` +
        widths.map((w) => `${w}: ${Math.round(bytes[w] / 1024)} KB`).join(", ") +
        `, hash ${hash}`,
    );
  }
  if (Object.keys(keep).length) console.log(`${name}: kept ${Object.keys(keep).join(", ")}`);
  // AVIF first: Swivel.tsx takes the first format the browser decodes.
  const order = ["avif", "webp"].filter((f) => formats[f]);
  // A subsampled export names its source frames, so Swivel.tsx keeps the render's timing (the steps are uneven).
  const sub = OUT < FRAMES ? { sourceFrames: FRAMES, source } : {};
  manifest[name] = { frames: OUT, w: W, h: H, crop, widths, ...sub, formats: Object.fromEntries(order.map((f) => [f, formats[f]])) };
}
const sorted = Object.fromEntries(Object.keys(manifest).sort().map((k) => [k, manifest[k]]));
writeFileSync(manifestFile, JSON.stringify(sorted, null, 1) + "\n");
