import { ReserveLink } from "@/components/chrome/ReserveLink";
import { Still } from "@/components/media/Still";
import { finale } from "@/content/copy";
import { site } from "@/content/site";
import { Reveal } from "./Reveal";
import styles from "./Finale.module.css";

/**
 * The page ends where it began: one screen with the whole racket in its beam over a lit horizon, and the
 * closing line and the last Reserve Now on the floor beneath it.
 */
export function Finale() {
  return (
    <section id="finale" className={styles.section} aria-labelledby="finale-title">
      <div className={styles.media} aria-hidden="true">
        {/* the 4:5 card crop on phones taller than 740 px; short phones keep the wide crop (Finale.module.css) */}
        <Still id="K01-finale" phoneCrop="card" phoneMedia="(max-width: 699px) and (min-height: 741px), (max-width: 699px) and (orientation: landscape)" alt="" phoneSizes="100vw" className={styles.still} />
      </div>
      <Reveal className={styles.copy}>
        <h2 id="finale-title" className="t-h2">
          {finale.headline}
        </h2>
        <p className="t-lead">{finale.sub}</p>
        {/* data-cta: the header's compact Reserve Now hides while this one is on screen (HeaderClient) */}
        <ReserveLink href="/reserve" className={`btn btn-primary ${styles.cta}`} data-cta="">
          {site.ctaLabel}
        </ReserveLink>
      </Reveal>
    </section>
  );
}
