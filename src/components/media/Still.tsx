import generated from "@/content/stills.generated.json";

/** Pixel size, exported widths and content hash (part of every file name) of one crop. */
type Size = { w: number; h: number; widths: number[]; hash?: string };
const sizes = generated as Record<string, Size>;

type Props = {
  /** Still id from src/content/stills.json, e.g. "K01-full". */
  id: string;
  /** Crop for wide screens (default "wide"). */
  crop?: string;
  /** Crop for phones (below 700 px); omit to use the same crop everywhere. */
  phoneCrop?: string;
  alt: string;
  /** The rendered width, as a sizes attribute. */
  sizes?: string;
  phoneSizes?: string;
  priority?: boolean;
  /** Overrides for a non-priority still that should still load early, e.g. a layer revealed on load. */
  loading?: "eager" | "lazy";
  fetchPriority?: "high" | "low" | "auto";
  className?: string;
};

const PHONE = "(max-width: 699px)";
const file = (key: string, s: Size, w: number, type: "avif" | "webp") =>
  `/stills/${key}-${w}${s.hash ? `.${s.hash}` : ""}.${type}`;
const srcset = (key: string, s: Size, type: "avif" | "webp") =>
  s.widths.map((w) => `${file(key, s, w, type)} ${w}w`).join(", ");

/**
 * A product still (own Blender render) as AVIF with a WebP fallback and a phone art-direction crop.
 * Renders nothing until scripts/stills.mjs has exported the still.
 */
export function Still({
  id,
  crop = "wide",
  phoneCrop,
  alt,
  sizes: sz = "100vw",
  phoneSizes = "100vw",
  priority,
  loading,
  fetchPriority,
  className,
}: Props) {
  const key = `${id}-${crop}`;
  const main = sizes[key];
  if (!main) return null;
  const phoneKey = phoneCrop ? `${id}-${phoneCrop}` : null;
  const phone = phoneKey ? sizes[phoneKey] : null;
  const fallback = main.widths.find((w) => w >= 1280) ?? main.widths[main.widths.length - 1];
  return (
    <picture className={className}>
      {phone && phoneKey && (
        <>
          <source media={PHONE} type="image/avif" srcSet={srcset(phoneKey, phone, "avif")} sizes={phoneSizes} width={phone.w} height={phone.h} />
          <source media={PHONE} type="image/webp" srcSet={srcset(phoneKey, phone, "webp")} sizes={phoneSizes} width={phone.w} height={phone.h} />
        </>
      )}
      <source type="image/avif" srcSet={srcset(key, main, "avif")} sizes={sz} />
      <source type="image/webp" srcSet={srcset(key, main, "webp")} sizes={sz} />
      <img
        src={file(key, main, fallback, "webp")}
        width={main.w}
        height={main.h}
        alt={alt}
        loading={loading ?? (priority ? "eager" : "lazy")}
        fetchPriority={fetchPriority ?? (priority ? "high" : "auto")}
        decoding={priority ? "sync" : "async"}
      />
    </picture>
  );
}

export function hasStill(id: string, crop = "wide") {
  return Boolean(sizes[`${id}-${crop}`]);
}
