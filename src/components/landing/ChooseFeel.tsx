import { feelChoice } from "@/content/copy";
import { Reveal } from "./Reveal";
import { SettleStill } from "./SettleStill";
import styles from "./ChooseFeel.module.css";

/**
 * Two feels: Command (white 3K) and Pace (black 12K). On wide screens one K08 frame holds both rackets, split by a
 * hairline, and each feel's name and purpose sit directly under its racket's cap, shown with the photo (they never
 * wait for the words' rise), so the pair is never two unnamed rackets. Below the name, what we made it to do, then
 * four ruled rows (feel, face, core, the game it suits) that read across the two columns. One closing line across
 * both says that only the core and the face differ. Phones stack a 4:5 crop of each, its name, then its words.
 * K08 is rendered in K04's language (owner, 2026-11-07): as the frame scrolls in, the pair settles from close and the
 * warm glow in the bores, the throats and along the edges comes up over the raking light (SettleStill.tsx).
 */
export function ChooseFeel() {
  return (
    <section id="feels" className={styles.section} aria-labelledby="feels-title">
      <Reveal className={styles.intro}>
        <p className="t-eyebrow">{feelChoice.eyebrow}</p>
        <h2 id="feels-title" className="t-h2">
          {feelChoice.headline}
        </h2>
      </Reveal>
      <div className={styles.stage}>
        <SettleStill id="K08" className={styles.wide} stillClassName={styles.still} />
        <div className={styles.panels}>
          {feelChoice.feels.map((f, i) => (
            <article key={f.id} className={styles.panel} aria-labelledby={`feel-${f.id}`}>
              <SettleStill
                id="K08"
                crop={i === 0 ? "left" : "right"}
                // contained in the 4:5 frame, the 2048 x 2880 half is 89% of its width
                sizes="89vw"
                baseSizes="54vw"
                className={styles.phoneMedia}
                stillClassName={styles.still}
              />
              {/* the caption of the photo above it: "Command, built for control" */}
              <div className={styles.tag}>
                <h3 id={`feel-${f.id}`} className={styles.name}>
                  {f.name}
                </h3>
                <p className={`t-lead ${styles.sub}`}>
                  {feelChoice.builtFor} {f.sub.toLowerCase()}
                </p>
              </div>
              <Reveal className={styles.text}>
                <p className={`t-lead ${styles.line}`}>{f.line}</p>
                <dl className={styles.rows}>
                  {f.rows.map(([label, value]) => (
                    <div key={label} className={styles.row}>
                      <dt className={`t-label ${styles.label}`}>{label}</dt>
                      <dd className={styles.value}>{value}</dd>
                    </div>
                  ))}
                </dl>
              </Reveal>
            </article>
          ))}
        </div>
        <Reveal className={styles.closing}>
          <p className="t-lead">{feelChoice.closing}</p>
        </Reveal>
      </div>
    </section>
  );
}
