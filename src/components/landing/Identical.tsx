import { ReserveLink } from "@/components/chrome/ReserveLink";
import { ConsistencySpikes } from "@/components/graphics/ConsistencySpikes";
import { MeasurementCard } from "@/components/graphics/MeasurementCard";
import { identical } from "@/content/copy";
import { site } from "@/content/site";
import { Reveal } from "./Reveal";
import { SettleStill } from "./SettleStill";
import styles from "./Identical.module.css";

/**
 * Identical: five rackets (K07, Command and Pace alternating), one standard; the distribution, the certificate, and the
 * second CTA. K07 is rendered in K04's language (owner, 2026-11-07): as the frame scrolls in, the row settles from
 * close and the warm glow in the bores, the throats and along the edges comes up over the raking light (SettleStill.tsx).
 */
export function Identical() {
  return (
    <>
      <section id="identical" className={styles.lineup} aria-labelledby="identical-title">
        <SettleStill id="K07" phoneCrop="trio" className={styles.media} stillClassName={styles.still} />
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
          {/* The certificate, then the payoff of the same weight and balance: the second Reserve Now, right under it. */}
          <div className={styles.card}>
            <MeasurementCard rotate />
            {/* Only the price line rises in: the button is never invisible while on screen, since the header's compact
                Reserve Now hides as soon as it enters (data-cta, HeaderClient) */}
            <Reveal className={styles.cta} items=":scope > p">
              <ReserveLink href="/reserve" className="btn btn-primary" data-cta="">
                {site.ctaLabel}
              </ReserveLink>
              <p className="t-label">{site.priceNote}</p>
            </Reveal>
          </div>
        </div>
      </section>
    </>
  );
}
