import generated from "@/content/stills.generated.json";
import type { FeelId } from "@/content/site";
import { FeelPicture, type PictureSet } from "./FeelPicture";

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
  /** A separate still for phones (its own camera framing), used with phoneCrop. Defaults to id. */
  phoneId?: string;
  /** When the phone crop applies (default below 700 px), e.g. "(max-width: 1023px)" for a 4:5 slot on tablets. */
  phoneMedia?: string;
  alt: string;
  /** The rendered width, as a sizes attribute. */
  sizes?: string;
  phoneSizes?: string;
  priority?: boolean;
  /** Overrides for a non-priority still that should still load early, e.g. a layer revealed on load. */
  loading?: "eager" | "lazy";
  fetchPriority?: "high" | "low" | "auto";
  className?: string;
  /**
   * The feel to show where the still has a Pace version, instead of the site-wide one (the /reserve gallery passes the
   * checkout's feel). Omitted: the still follows the feel toggle.
   */
  feel?: FeelId;
};

const PHONE = "(max-width: 699px)";
/** A still's Pace version: its id plus "-pace", with the same crops ("K01-full-pace", "K05-phone-pace"). */
const PACE = "-pace";
const file = (key: string, s: Size, w: number, type: "avif" | "webp") =>
  `/stills/${key}-${w}${s.hash ? `.${s.hash}` : ""}.${type}`;
const srcset = (key: string, s: Size, type: "avif" | "webp") =>
  s.widths.map((w) => `${file(key, s, w, type)} ${w}w`).join(", ");

/** One picture's sources and fallback: the phone crop (if any) first, then the wide crop, AVIF before WebP. */
function pictureSet(
  main: [string, Size],
  phone: [string, Size] | null,
  phoneMedia: string,
  sz: string,
  phoneSizes: string,
): PictureSet {
  const [key, s] = main;
  const fallback = s.widths.find((w) => w >= 1280) ?? s.widths[s.widths.length - 1];
  const sources: PictureSet["sources"] = [];
  if (phone) {
    const [pk, p] = phone;
    sources.push(
      { media: phoneMedia, type: "image/avif", srcSet: srcset(pk, p, "avif"), sizes: phoneSizes, width: p.w, height: p.h },
      { media: phoneMedia, type: "image/webp", srcSet: srcset(pk, p, "webp"), sizes: phoneSizes, width: p.w, height: p.h },
    );
  }
  sources.push({ type: "image/avif", srcSet: srcset(key, s, "avif"), sizes: sz }, { type: "image/webp", srcSet: srcset(key, s, "webp"), sizes: sz });
  return { sources, src: file(key, s, fallback, "webp"), width: s.w, height: s.h };
}

const entry = (key: string | null): [string, Size] | null => (key && sizes[key] ? [key, sizes[key]] : null);

/**
 * A product still (own Blender render) as AVIF with a WebP fallback and a phone art-direction crop.
 * Renders nothing until scripts/stills.mjs has exported the still.
 * Where a Pace version is exported (the id plus "-pace", per crop), the still follows the feel (FeelPicture): the
 * server paints Command, and a stored or chosen Pace swaps in on the client. A crop without a Pace export keeps its
 * Command file, silently; a still with none renders exactly as before.
 */
export function Still({
  id,
  crop = "wide",
  phoneCrop,
  phoneId,
  phoneMedia = PHONE,
  alt,
  sizes: sz = "100vw",
  phoneSizes = "100vw",
  priority,
  loading,
  fetchPriority,
  className,
  feel,
}: Props) {
  const main = entry(`${id}-${crop}`);
  if (!main) return null;
  const phoneBase = phoneId ?? id;
  const phone = phoneCrop ? entry(`${phoneBase}-${phoneCrop}`) : null;
  const paceMain = entry(`${id}${PACE}-${crop}`);
  const pacePhone = phone && phoneCrop ? entry(`${phoneBase}${PACE}-${phoneCrop}`) : null;
  const command = pictureSet(main, phone, phoneMedia, sz, phoneSizes);
  const img = {
    loading: loading ?? (priority ? "eager" : "lazy"),
    fetchPriority: fetchPriority ?? (priority ? "high" : "auto"),
    decoding: priority ? "sync" : "async",
  } as const;
  if (paceMain || pacePhone) {
    const pace = pictureSet(paceMain ?? main, pacePhone ?? phone, phoneMedia, sz, phoneSizes);
    return <FeelPicture command={command} pace={pace} feel={feel} className={className} alt={alt} {...img} />;
  }
  return (
    <picture className={className}>
      {command.sources.map((s) => (
        <source key={`${s.media ?? ""}${s.type}`} {...s} />
      ))}
      <img src={command.src} width={command.width} height={command.height} alt={alt} {...img} />
    </picture>
  );
}

export function hasStill(id: string, crop = "wide") {
  return Boolean(sizes[`${id}-${crop}`]);
}

/** Whether a still has a Pace version exported for this crop. */
export function hasPaceStill(id: string, crop = "wide") {
  return Boolean(sizes[`${id}${PACE}-${crop}`]);
}
