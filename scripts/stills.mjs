// Export the product stills from 16-bit Blender masters to AVIF and WebP.
// Usage: node scripts/stills.mjs <masters dir> [id ...]
// Reads src/content/stills.json (crops and widths); writes public/stills/<id>-<crop>-<width>.(avif|webp)
// and src/content/stills.generated.json (pixel size and exported widths of every crop, read by <Still>).
// Masters are not committed (too large); the exported files are.
import { readFileSync, writeFileSync, existsSync, mkdirSync } from "node:fs";
import { join } from "node:path";
import sharp from "sharp";

const root = new URL("..", import.meta.url).pathname;
const config = JSON.parse(readFileSync(join(root, "src/content/stills.json"), "utf8"));
const [src, ...only] = process.argv.slice(2);
if (!src) throw new Error("Pass the masters directory.");
const out = join(root, "public/stills");
mkdirSync(out, { recursive: true });
const sizesFile = join(root, "src/content/stills.generated.json");
const sizes = existsSync(sizesFile) ? JSON.parse(readFileSync(sizesFile, "utf8")) : {};

// Triangular-PDF dither of about one 8-bit step, applied once at full size: stops banding in the dark gradients.
async function dithered(img) {
  const { data, info } = await img.toColourspace("rgb16").raw({ depth: "ushort" }).toBuffer({ resolveWithObject: true });
  const px = new Uint16Array(data.buffer, data.byteOffset, data.length / 2);
  const out8 = Buffer.alloc(px.length);
  let seed = 1234567;
  const rnd = () => ((seed = (seed * 1664525 + 1013904223) >>> 0) / 4294967296);
  for (let i = 0; i < px.length; i++) {
    const v = px[i] / 257 + (rnd() - rnd()) * 0.9;
    out8[i] = v < 0 ? 0 : v > 255 ? 255 : Math.round(v);
  }
  return { buf: out8, width: info.width, height: info.height, channels: info.channels };
}

for (const [id, still] of Object.entries(config.stills)) {
  if (only.length && !only.includes(id)) continue;
  const file = join(src, `${id}.png`);
  if (!existsSync(file)) {
    console.log(`skip ${id}: no master`);
    continue;
  }
  for (const [crop, c] of Object.entries(still.crops)) {
    let img = sharp(file, { limitInputPixels: false }).removeAlpha();
    if (c.rotate) img = sharp(await img.rotate(-c.rotate).png({ compressionLevel: 0 }).toBuffer());
    const meta = await img.metadata();
    const [W, H] = [meta.width, meta.height];
    if (c.w) {
      img = img.extract({
        left: Math.round((c.x ?? 0) * W),
        top: Math.round((c.y ?? 0) * H),
        width: Math.round(c.w * W),
        height: Math.round((c.h ?? 1) * H),
      });
    }
    const d = await dithered(img);
    const base = sharp(d.buf, { raw: { width: d.width, height: d.height, channels: d.channels } });
    const widths = (config.widths[crop] ?? config.widths.card).filter((w) => w < d.width);
    widths.push(Math.min(d.width, Math.max(...(config.widths[crop] ?? config.widths.card))));
    sizes[`${id}-${crop}`] = { w: d.width, h: d.height, widths };
    for (const w of widths) {
      const resized = base.clone().resize({ width: w, kernel: "lanczos3" });
      await resized.clone().avif({ quality: 58, effort: 5, chromaSubsampling: "4:4:4" }).toFile(join(out, `${id}-${crop}-${w}.avif`));
      await resized.clone().webp({ quality: 80, effort: 5, smartSubsample: true }).toFile(join(out, `${id}-${crop}-${w}.webp`));
      // Social cards: crawlers want a plain JPEG at 1200 x 630.
      if (crop === "og") await resized.clone().resize({ width: 1200, height: 630, fit: "cover" }).jpeg({ quality: 86, mozjpeg: true }).toFile(join(out, "og.jpg"));
    }
    console.log(`${id}-${crop}: ${d.width}x${d.height}, widths ${widths.join(", ")}`);
  }
}
writeFileSync(sizesFile, JSON.stringify(sizes, null, 1) + "\n");
