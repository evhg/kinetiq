import Link from "next/link";
import { ConsistencySpikes } from "@/components/graphics/ConsistencySpikes";
import { MeasurementCard } from "@/components/graphics/MeasurementCard";
import { Still } from "@/components/media/Still";
import { identical } from "@/content/copy";
import { site } from "@/content/site";
import { Reveal } from "./Reveal";
import styles from "./Identical.module.css";

/** Identical: five rackets, one standard; the distribution, the certificate, and the second CTA. */
export function Identical() {
  return (
    <>
      <section id="identical" className={styles.lineup} aria-labelledby="identical-title">
        <div className={styles.media} aria-hidden="true">
          <Still id="K07" phoneCrop="trio" alt="" className={styles.still} />
        </div>
        <Reveal className={styles.copy}>
          <h2 id="identical-title" className="t-h2">
            {identical.headline}
          </h2>
          <p className="t-lead">{identical.body}</p>
        </Reveal>
      </section>
      <section className={styles.proof} aria-label="Measured, racket by racket">
        <div className={styles.grid}>
          <div className={styles.graph}>
            <ConsistencySpikes />
          </div>
          {/* The certificate, then the payoff of "Buy two": the second Reserve Now, right under it. */}
          <div className={styles.card}>
            <MeasurementCard rotate />
            <Reveal className={styles.cta}>
              <Link href="/reserve" className="btn btn-primary">
                {site.ctaLabel}
              </Link>
              <p className="t-label">
                {site.fromPriceLabel}. {site.refundLabel}.
              </p>
            </Reveal>
          </div>
        </div>
      </section>
    </>
  );
}
