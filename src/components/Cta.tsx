import Link from "next/link";
import { site } from "@/content/site";

/** The site's one call to action. Same words, same destination, everywhere. */
export function Cta({ note = true }: { note?: boolean }) {
  return (
    <div className="cta-wrap">
      <Link className="cta" href="/reserve" prefetch={false}>
        {site.ctaLabel}
      </Link>
      {note ? (
        <p className="cta-note">
          {site.fromPriceLabel}. {site.refundShort}.
        </p>
      ) : null}
    </div>
  );
}
