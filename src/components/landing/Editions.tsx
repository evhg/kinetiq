import Link from "next/link";
import type { ReactNode } from "react";
import { Icon, TierGlyph } from "@/components/graphics/Icons";
import { Still } from "@/components/media/Still";
import { Hyphens } from "@/components/text/Hyphens";
import {
  editionsIntro,
  guaranteeFine,
  identicalFine,
  includeIcons,
  invitesOpen,
  lifetime,
  priceLabel,
  tiers,
  type Tier,
  type TierId,
} from "@/content/lineup";
import { reserveCopy } from "@/content/reserve";
import { Reveal } from "./Reveal";
import styles from "./Editions.module.css";

const IMAGE: Record<TierId, { id: string; crop: string }> = {
  // KINETIQ: one racket, three-quarter (the hero and the finale already show the beam camera).
  reserve: { id: "K08", crop: "left" },
  // First 500: the set of two, both throats laser-marked with the set number (027/500). Command: the K11 Pace render's
  // 12K face reads as a flat checkerboard at this size (art review, 2026-10-22).
  limited: { id: "K11-command", crop: "card" },
  // One of Ten: the set of three in its fitted case.
  invite: { id: "K09-card", crop: "card" },
};

// "Identical: one mould ..." leads its fine-print line the way "*Built to last five years." leads the design life's.
const [IDENTICAL_HEAD, IDENTICAL_BODY] = (() => {
  const at = identicalFine.indexOf(": ");
  return [identicalFine.slice(0, at + 1), identicalFine.slice(at + 2)];
})();

/**
 * One racket, in three editions. KINETIQ and First 500 are whole-card links into the reservation page; One of Ten is
 * by invitation only, so its card is not a link (no hover, no arrow): it says so where the arrow would be, and a quiet
 * "Have an invitation?" opens the code field on /reserve. Every card lists what it includes and ends on the same price
 * line. The lead says plainly that every edition holds the same racket.
 */
export function Editions() {
  // Read at build: Vercel rebuilds when INVITE_CODES changes.
  const open = invitesOpen(process.env.INVITE_CODES);
  return (
    <section id="editions" className={styles.section} aria-labelledby="editions-title">
      <div className={styles.intro}>
        <h2 id="editions-title" className={`t-h2 ${styles.title}`}>
          {editionsIntro.headline}
        </h2>
        <p className={`t-lead ${styles.lead}`}>{editionsIntro.lead}</p>
      </div>
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
                  end={<span className={`t-label ${styles.byInvite}`}>{editionsIntro.byInvitation}</span>}
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
      {/* The fine print under the cards, one line per claim: the design life (*), what "identical" means (the two sets'
          card lines promise identical rackets), then One of Ten's guarantee (\u00a7), so "a design life, not a
          guarantee" never runs into the one guarantee. */}
      <div className={styles.notes}>
        <p className={styles.fine}>
          <span className={styles.fineHead}>
            {lifetime.mark}
            {lifetime.line}.
          </span>{" "}
          {lifetime.fine}
        </p>
        <p className={styles.fine}>
          <span className={styles.fineHead}>{IDENTICAL_HEAD}</span> {IDENTICAL_BODY}
        </p>
        <p className={styles.fine}>
          <span className={styles.fineHead}>{lifetime.guaranteeMark}</span>
          {guaranteeFine}
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
                {/* the design life is a property, not a perk, and the guarantee is One of Ten's alone: each marker
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
