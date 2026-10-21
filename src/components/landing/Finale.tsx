import Link from "next/link";
import { Still } from "@/components/media/Still";
import { finale } from "@/content/copy";
import { site } from "@/content/site";
import { Reveal } from "./Reveal";
import styles from "./Finale.module.css";

/** The page ends where it began: the racket in its beam, now over a lit horizon, then the last Reserve Now. */
export function Finale() {
  return (
    <section id="finale" className={styles.section} aria-labelledby="finale-title">
      <div className={styles.media} aria-hidden="true">
        <Still id="K01-finale" phoneCrop="card" alt="" phoneSizes="100vw" className={styles.still} />
      </div>
      <Reveal className={styles.copy}>
        <h2 id="finale-title" className="t-h2">
          {finale.headline}
        </h2>
        <p className="t-lead">{finale.sub}</p>
        <Link href="/reserve" className={`btn btn-primary ${styles.cta}`}>
          {site.ctaLabel}
        </Link>
      </Reveal>
    </section>
  );
}
