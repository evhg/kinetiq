import Link from "next/link";
import { Icon, TierGlyph } from "@/components/graphics/Icons";
import { Still } from "@/components/media/Still";
import { editions } from "@/content/copy";
import { includeIcons, priceLabel, tiers, type TierId } from "@/content/lineup";
import { Reveal } from "./Reveal";
import styles from "./Editions.module.css";

const IMAGE: Record<TierId, { id: string; crop: string }> = {
  // ConQuer: one racket, three-quarter (the hero and the finale already show the beam camera).
  reserve: { id: "K08", crop: "left" },
  limited: { id: "K06-full", crop: "card" },
  invite: { id: "K09-card", crop: "card" },
};

/**
 * The three editions as whole-card links into the reservation page. Every card lists what it includes,
 * and the price with its arrow sits on one shared foot line.
 */
export function Editions() {
  return (
    <section id="editions" className={styles.section} aria-labelledby="editions-title">
      <h2 id="editions-title" className={`t-h2 ${styles.title}`}>
        {editions.headline}
      </h2>
      <Reveal as="ul" className={styles.cards} y={16}>
        {tiers.map((t) => (
          <li key={t.id} className={styles.item}>
            <Link href={`/reserve?tier=${t.id}`} className={styles.card} data-tier={t.id}>
              <div className={styles.media} aria-hidden="true">
                <Still id={IMAGE[t.id].id} crop={IMAGE[t.id].crop} alt="" sizes="(max-width: 699px) 84vw, 33vw" className={styles.still} />
              </div>
              <div className={styles.body}>
                <div className={styles.head}>
                  <TierGlyph tier={t.id} className={styles.glyph} />
                  <h3 className={styles.name}>{t.name}</h3>
                  <span className={`t-label ${styles.status}`} data-tier={t.id}>
                    {t.availability}
                  </span>
                </div>
                <p className={styles.line}>{t.cardLine}</p>
                <ul className={styles.includes}>
                  {t.includes.map((inc, n) => (
                    <li key={inc}>
                      <Icon name={includeIcons[t.id][n] ?? "shieldCheck"} size={20} className={styles.includeIcon} />
                      {inc}
                    </li>
                  ))}
                </ul>
                <div className={styles.foot}>
                  <p className={`t-num ${styles.price}`}>{priceLabel(t.priceEur)}</p>
                  <svg viewBox="0 0 24 24" className={styles.arrow} aria-hidden="true">
                    <path d="M5 12h13M13 6.5l5.5 5.5-5.5 5.5" />
                  </svg>
                </div>
              </div>
            </Link>
          </li>
        ))}
      </Reveal>
    </section>
  );
}
