import Link from "next/link";
import { Icon, TierGlyph, type IconName } from "@/components/graphics/Icons";
import { Still } from "@/components/media/Still";
import { editions } from "@/content/copy";
import { priceLabel, tiers, type TierId } from "@/content/lineup";
import { Reveal } from "./Reveal";
import styles from "./Editions.module.css";

const IMAGE: Record<TierId, { id: string; crop: string }> = {
  reserve: { id: "K01-full", crop: "card" },
  limited: { id: "K06-full", crop: "card" },
  invite: { id: "K09", crop: "card" },
};

const EXTRA_ICONS: IconName[] = ["penNib", "court", "fittedCase"];

/** The three editions as whole-card links into the reservation page. */
export function Editions() {
  return (
    <section id="editions" className={`lift ${styles.section}`} aria-labelledby="editions-title">
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
                <p className={`t-num ${styles.price}`}>{priceLabel(t.priceEur)}</p>
                <p className={styles.line}>{t.cardLine}</p>
                {t.rackets > 1 ? (
                  <ul className={styles.includes}>
                    {t.includes.slice(0, 3).map((inc, n) => (
                      <li key={inc}>
                        <Icon name={EXTRA_ICONS[n]} size={20} className={styles.includeIcon} />
                        {inc}
                      </li>
                    ))}
                  </ul>
                ) : null}
              </div>
            </Link>
          </li>
        ))}
      </Reveal>
    </section>
  );
}
