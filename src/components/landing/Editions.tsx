import Link from "next/link";
import type { ReactNode } from "react";
import { Icon, TierGlyph } from "@/components/graphics/Icons";
import { Still } from "@/components/media/Still";
import { Hyphens } from "@/components/text/Hyphens";
import { editions } from "@/content/copy";
import { includeIcons, includesFine, invitesOpen, lifetime, priceLabel, tiers, type Tier, type TierId } from "@/content/lineup";
import { reserveCopy } from "@/content/reserve";
import { Reveal } from "./Reveal";
import styles from "./Editions.module.css";

const IMAGE: Record<TierId, { id: string; crop: string }> = {
  // ConQuer: one racket, three-quarter (the hero and the finale already show the beam camera).
  reserve: { id: "K08", crop: "left" },
  // VanQuish: the set of two, both throats laser-marked 027/500. Command: the K11 Pace render's 12K face reads as a
  // flat checkerboard at this size (art review, 2026-10-22) until it is re-rendered with spread-tow sheen.
  limited: { id: "K11-command", crop: "card" },
  invite: { id: "K09-card", crop: "card" },
};

const BY_INVITATION = "By invitation";

/**
 * The three editions. ConQuer and VanQuish are whole-card links into the reservation page; InviQtus is
 * by invitation only, so its card is not a link (no hover, no arrow): it says so where the arrow would
 * be, and a quiet "Have an invitation?" opens the code field on /reserve. Every card lists what it
 * includes and ends on the same price line.
 */
export function Editions() {
  // Read at build: Vercel rebuilds when INVITE_CODES changes.
  const open = invitesOpen(process.env.INVITE_CODES);
  return (
    <section id="editions" className={styles.section} aria-labelledby="editions-title">
      <h2 id="editions-title" className={`t-h2 ${styles.title}`}>
        {editions.headline}
      </h2>
      <Reveal as="ul" className={styles.cards} y={16}>
        {tiers.map((t) => (
          <li key={t.id} className={styles.item}>
            {t.id === "invite" ? (
              <div className={styles.card} data-tier={t.id}>
                <CardBody
                  t={t}
                  after={
                    open ? (
                      <Link href="/reserve?invite" className={styles.inviteLink}>
                        {reserveCopy.invite.ask}
                      </Link>
                    ) : (
                      <p className={styles.inviteSoon}>{reserveCopy.invitesClosedNote}</p>
                    )
                  }
                  end={<span className={`t-label ${styles.byInvite}`}>{BY_INVITATION}</span>}
                />
              </div>
            ) : (
              <Link href={`/reserve?tier=${t.id}`} className={styles.card} data-tier={t.id}>
                <CardBody
                  t={t}
                  end={
                    <svg viewBox="0 0 24 24" className={styles.arrow} aria-hidden="true">
                      <path d="M5 12h13M13 6.5l5.5 5.5-5.5 5.5" />
                    </svg>
                  }
                />
              </Link>
            )}
          </li>
        ))}
      </Reveal>
      {/* The fine print the include lines' markers point to, one line per claim: the design life (*), then
          InviQtus's guarantee (\u2021), so "a design life, not a guarantee" never runs into the one guarantee. */}
      <div className={styles.notes}>
        <p className={styles.fine}>
          <span className={styles.fineHead}>
            {lifetime.mark}
            {lifetime.line}.
          </span>{" "}
          {lifetime.fine}
        </p>
        <p className={styles.fine}>
          <span className={styles.fineHead}>{lifetime.guaranteeMark}</span>
          {includesFine("invite")}
        </p>
      </div>
    </section>
  );
}

function CardBody({ t, after, end }: { t: Tier; after?: ReactNode; end: ReactNode }) {
  return (
    <>
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
              <span>
                <Hyphens text={inc} />
                {/* the design life is a property, not a perk, and the guarantee is InviQtus's alone: each marker
                    points to its own line of fine print under the cards */}
                {inc === lifetime.include ? <span className={styles.mark}>{lifetime.mark}</span> : null}
                {inc === lifetime.guarantee ? <span className={`${styles.mark} ${styles.raised}`}>{lifetime.guaranteeMark}</span> : null}
              </span>
            </li>
          ))}
        </ul>
        {after}
        <div className={styles.foot}>
          <p className={`t-num ${styles.price}`}>{priceLabel(t.priceEur)}</p>
          {end}
        </div>
      </div>
    </>
  );
}
