import Link from "next/link";
import { site, type ModelId } from "@/content/site";

/** The site's one call to action. Same words, same destination, everywhere. */
export function Cta({ model, note = true }: { model?: ModelId; note?: boolean }) {
  return (
    <div className="cta-wrap">
      <Link className="cta" href={model ? `/checkout?model=${model}` : "/checkout"} prefetch={false}>
        {site.ctaLabel}
      </Link>
      {note ? (
        <p className="cta-note">
          {site.priceLabel}. {site.shipLabel}.
        </p>
      ) : null}
    </div>
  );
}
