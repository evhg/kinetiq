import { Cta } from "@/components/Cta";
import { site } from "@/content/site";

/** The last emotional peak, and the end of the page. Nothing competes with it. */
export function Finale() {
  return (
    <section className="section finale" aria-labelledby="finale-title">
      <h2 id="finale-title" className="display">
        The first run leaves the mould in January.
      </h2>
      <p className="lead">
        Reserve yours today. {site.refundLabel}.
      </p>
      <Cta />
    </section>
  );
}
