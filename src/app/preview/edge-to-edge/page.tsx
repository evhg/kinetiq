import type { Metadata } from "next";
import { SiteFooter, SiteHeader } from "@/components/chrome/Chrome";
import { Still } from "@/components/media/Still";
import { EdgeOptions } from "@/components/preview/EdgeOptions";
import styles from "./page.module.css";

/**
 * A private preview (owner, 2026-11-11): three options for the image under the Sweet spot's "Edge to edge.", each played
 * by scroll as it would run on the landing page, and today's K14 for reference. Linked from nowhere, never indexed, and
 * behind the NDA gate like every page (src/proxy.ts). Lives on the preview/edge-to-edge branch only.
 */
export const metadata: Metadata = {
  title: "Edge to edge: three options",
  robots: { index: false, follow: false, nocache: true },
};

export default function EdgeToEdgePreview() {
  return (
    <>
      <SiteHeader toggles />
      <main id="main" className={styles.main}>
        <header className={styles.intro}>
          <p className="t-eyebrow">Preview · Sweet spot</p>
          <h1 className={`t-h2 ${styles.h1}`}>Edge to edge: three options for the image.</h1>
          <p className={`t-lead ${styles.lead}`}>
            Each option plays as it would under “Edge to edge.” on the page. Scroll to run it; the Command and Pace switch
            in the header changes the feel.
          </p>
          <ol className={styles.index}>
            <li>
              <a href="#option-a">A · The face fills with light</a>
            </li>
            <li>
              <a href="#option-b">B · Flat to the edge</a>
            </li>
            <li>
              <a href="#option-c">C · A ball at the very edge</a>
            </li>
          </ol>
        </header>
        <EdgeOptions />
        <section id="edge-reference" tabIndex={-1} className={styles.reference} aria-labelledby="edge-reference-title">
          <p className="t-eyebrow">For reference</p>
          <h2 id="edge-reference-title" className={`t-h3 ${styles.refTitle}`}>
            The image on the page today (K14).
          </h2>
          <div className={styles.refFrame}>
            <Still id="K14" phoneCrop="portrait" alt="Today's sweet spot image: a KINETIQ face up close in raking light, running out to the rim." sizes="(min-width: 900px) 70vw, 100vw" className={styles.refStill} />
          </div>
        </section>
      </main>
      <SiteFooter />
    </>
  );
}
