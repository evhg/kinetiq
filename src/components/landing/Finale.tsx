import Link from "next/link";
import { Still } from "@/components/media/Still";
import { finale, lifeNote } from "@/content/copy";
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
        <Still id="K01-finale" phoneCrop="card" alt="" phoneSizes="100vw" className={styles.still} />
      </div>
      <Reveal className={styles.copy}>
        <h2 id="finale-title" className="t-h2">
          {finale.headline}
          <a href={`#${lifeNote.id}`} className="footmark" aria-label={lifeNote.label}>
            {lifeNote.mark}
          </a>
        </h2>
        <p className="t-lead">{finale.sub}</p>
        <Link href="/reserve" className={`btn btn-primary ${styles.cta}`}>
          {site.ctaLabel}
        </Link>
      </Reveal>
    </section>
  );
}
