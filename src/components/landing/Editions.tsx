import Link from "next/link";
import { ReserveLink } from "@/components/chrome/ReserveLink";
import { Fragment, type ReactNode } from "react";
import { Icon, TierGlyph } from "@/components/graphics/Icons";
import { Still } from "@/components/media/Still";
import { Hyphens } from "@/components/text/Hyphens";
import { editionsIntro, includeIcons, priceLabel, tiers, type Tier, type TierId } from "@/content/lineup";
import { reserveCopy } from "@/content/reserve";
import { invitationsOpen } from "@/lib/stripe-server";
import { Reveal } from "./Reveal";
import styles from "./Editions.module.css";

const IMAGE: Record<TierId, { id: string; crop: string }> = {
  // KINETIQ: one white Command racket (KQ-000427) shot with K11's camera and light, so the three cards read as one
  // shoot (the hero and the finale show the beam camera, and Choose your feel shows K08 just before).
  reserve: { id: "K11-single", crop: "card" },
  // First 500: the set of two, both throats laser-marked with the set number (027/500). Command: the K11 Pace render's
  // 12K face reads as a flat checkerboard at this size (art review, 2026-10-22).
  limited: { id: "K11-command", crop: "card" },
  // One of Ten: the set of three in its fitted case.
  invite: { id: "K09-card", crop: "card" },
};

/**
 * One racket, in three editions. KINETIQ and First 500 are whole-card links into the reservation page; One of Ten is
 * by invitation only, so its card is not a link (no hover, no arrow). While invitations are open it says so where the
 * arrow would be, and a quiet "Have an invitation?" opens the code field on /reserve; while they are closed, its
 * "open soon" note says it once. Every card lists what it includes and ends on the same price line. The lead says
 * plainly that every edition holds the same racket. No footnote markers and no fine print under the cards (owner,
 * 2026-10-22): what "identical" means is told by the Identical section's own body.
 */
export function Editions() {
  // Read at build: Vercel rebuilds when INVITE_CODES changes. The same rule as /reserve and both APIs (paperwork, valid
  // codes and the one-use check), so the card never offers what /reserve refuses.
  const open = invitationsOpen();
  return (
    <section id="editions" className={styles.section} aria-labelledby="editions-title">
      <div className={styles.intro}>
        <h2 id="editions-title" className={`t-h2 ${styles.title}`}>
          {/* each clause keeps its words together: "We make one racket, / in three editions." */}
          {editionsIntro.headline.split(/(?<=,) /).map((clause, n) => (
            <Fragment key={clause}>
              {n ? " " : null}
              <span className={styles.clause}>{clause}</span>
            </Fragment>
          ))}
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
                  end={open ? <span className={`t-label ${styles.byInvite}`}>{editionsIntro.byInvitation}</span> : null}
                />
              </div>
            ) : (
              <ReserveLink href={`/reserve?tier=${t.id}`} className={styles.card} data-tier={t.id}>
                <CardBody
                  t={t}
                  end={
                    <svg viewBox="0 0 24 24" className={styles.arrow} aria-hidden="true">
                      <path d="M5 12h13M13 6.5l5.5 5.5-5.5 5.5" />
                    </svg>
                  }
                />
              </ReserveLink>
            )}
          </li>
        ))}
      </Reveal>
    </section>
  );
}

function CardBody({ t, after, end }: { t: Tier; after?: ReactNode; end: ReactNode }) {
  return (
    <>
      <div className={styles.media} aria-hidden="true">
        <Still id={IMAGE[t.id].id} crop={IMAGE[t.id].crop} alt="" sizes="(max-width: 599px) 84vw, (max-width: 899px) 57vw, 33vw" className={styles.still} />
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
              </span>
            </li>
          ))}
        </ul>
        {t.note ? <p className={styles.note}>{t.note}</p> : null}
        {after}
        <div className={styles.foot}>
          <p className={`t-num ${styles.price}`}>{priceLabel(t.priceEur)}</p>
          {end}
        </div>
      </div>
    </>
  );
}
