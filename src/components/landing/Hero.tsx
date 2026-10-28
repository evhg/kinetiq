"use client";

import { useRef } from "react";
import { HeroSwivel, type SwivelHandle } from "./HeroSwivel";
import { FeelToggle } from "@/components/chrome/FeelToggle";
import { ReserveLink } from "@/components/chrome/ReserveLink";
import { Still } from "@/components/media/Still";
import { useMotion } from "@/components/motion/MotionProvider";
import { Hyphens } from "@/components/text/Hyphens";
import { hero } from "@/content/copy";
import { feelToggleLabels, site } from "@/content/site";
import { gsap, useGSAP } from "@/lib/gsap";
import styles from "./Hero.module.css";

/**
 * Where the hero takes its portrait layout and the 9:16 phone master: phones, tablets in portrait below 1000 px, and
 * any window narrower than 4:5 (an iPad Pro in portrait). Keep it in step with Hero.module.css.
 */
const PORTRAIT = "(max-width: 699px), (max-width: 999px) and (max-aspect-ratio: 1/1), (max-aspect-ratio: 4/5)";
/** On a portrait tablet the master is drawn wider than the screen (up to about 1.4 times), sized by its band. */
const PORTRAIT_SIZES = "(min-width: 700px) 140vw, 100vw";

/**
 * Hero: K01 rises out of the dark (base, then the beam) and turns as the page scrolls (HeroSwivel), one CTA. Wide screens set the words, Reserve Now
 * and the price line in the left seven columns beside the racket, which stands large on the right; phones and
 * portrait tablets keep the words above the racket and Reserve Now on the floor below it.
 */
export function Hero() {
  const root = useRef<HTMLElement>(null);
  const { motionOn } = useMotion();
  const swivel = useRef<SwivelHandle>(null);

  useGSAP(
    (_, contextSafe) => {
      if (!motionOn) return;
      const mm = gsap.matchMedia();
      mm.add("(prefers-reduced-motion: no-preference)", () => {
        // The frame settles from the scale the CSS painted first (Hero.module.css), so nothing jumps.
        gsap.fromTo(`.${styles.media}`, { scale: 1.035 }, { scale: 1, duration: 2.4, ease: "expo.out" });
        // The beam: the lit render fades over the dark base once its image has decoded, never before.
        const full = root.current?.querySelector<HTMLElement>(`.${styles.full}`);
        const img = full?.querySelector("img");
        let live = true;
        // Never call a contextSafe function from inside this matchMedia context: it pushes the hook's context into the
        // matchMedia one, which is already inside the hook's, and that cycle makes the hook's revert recurse until the
        // stack overflows (Back from /reserve re-showed the cached landing with the image decoded: "This page couldn't
        // load"). A decoded image runs the tween here, in this context; a later decode goes through contextSafe.
        const beam = () => {
          if (live && full) gsap.fromTo(full, { opacity: 0 }, { opacity: 1, duration: 1.6, delay: 0.2, ease: "power2.out" });
        };
        if (img?.complete && img.naturalWidth > 0) beam();
        else {
          const later = contextSafe!(beam);
          img?.decode().then(later, later);
        }
        // Scroll away: the image drifts and a veil darkens it. The words and the button simply scroll
        // with the page, so Reserve Now stays fully opaque.
        const tl = gsap.timeline({
          defaults: { ease: "none" },
          scrollTrigger: { trigger: root.current, start: "top top", end: "bottom top", scrub: 0.4 },
        });
        tl.to(`.${styles.drift}`, { yPercent: 6 }, 0).to(`.${styles.veil}`, { opacity: 0.55 }, 0);
        return () => {
          live = false;
        };
      });
      // The swivel (owner, 2026-10-23): the racket turns about its handle as the hero scrolls away (HeroSwivel draws the
      // frames; until they are decoded, or without a sequence, this only moves a number). Wide screens finish the turn by
      // 26% of the hero scrolled, while the racket is still in view (it fades out between 10% and 32%); phones and
      // portrait tablets by 30% (iPhone, 2026-10-28: at 60% the racket had already slid up under the header, so most of
      // the turn happened off screen; at 30% of a 664 px hero the whole racket is still below the header).
      const turn = (end: string) => {
        const state = { p: 0 };
        gsap.to(state, {
          p: 1,
          ease: "none",
          scrollTrigger: { trigger: root.current, start: "top top", end, scrub: 0.4 },
          onUpdate: () => swivel.current?.progress(state.p),
        });
        return () => swivel.current?.progress(0);
      };
      // The layout decides, not the width alone: a portrait window from 1000 px (an iPad Pro) has the phone layout. One
      // conditions object, never CSS range syntax here (older iOS Safari's matchMedia cannot parse it, so it never matched).
      mm.add({ portrait: PORTRAIT, motion: "(prefers-reduced-motion: no-preference)" }, (ctx) => {
        const { portrait, motion } = ctx.conditions as { portrait: boolean; motion: boolean };
        if (!motion) return;
        const reset = turn(portrait ? "top -30%" : "top -26%");
        // Wide screens: the racket fades out between 10% and 32% of the hero scrolled, once it has turned, so the Unibody
        // chapter's edge-on racket (K02) arrives on a dark stage and the two rackets never stand side by side.
        if (!portrait)
          gsap.fromTo(
            `.${styles.drift}`,
            { opacity: 1 },
            { opacity: 0, ease: "none", scrollTrigger: { trigger: root.current, start: "top -10%", end: "top -32%", scrub: 0.4 } },
          );
        return reset;
      });
      return () => mm.revert();
    },
    { scope: root, dependencies: [motionOn], revertOnUpdate: true },
  );

  return (
    <section ref={root} id="hero" className={styles.hero} aria-labelledby="hero-title">
      <div className={styles.drift} aria-hidden="true">
        <div className={styles.media}>
          {/* Wide: the close beam camera (the racket spans 27-80% of the frame). Phones and portrait tablets: their own
              9:16 master (PORTRAIT, the same condition as Hero.module.css's portrait layouts). */}
          <Still id="K01-base" phoneId="K01-hero-base-phone" phoneCrop="portrait" phoneMedia={PORTRAIT} phoneSizes={PORTRAIT_SIZES} alt="" priority className={styles.base} />
          {/* The lit layer: the K01-full still and, over it, the swivel's canvas (frame 0 is this still), faded in
              together by the beam. */}
          <div className={styles.full}>
            <Still id="K01-full" phoneId="K01-hero-full-phone" phoneCrop="portrait" phoneMedia={PORTRAIT} phoneSizes={PORTRAIT_SIZES} alt="" loading="eager" fetchPriority="low" className={styles.layer} />
            <HeroSwivel ref={swivel} portraitQuery={PORTRAIT} className={styles.swivel} />
          </div>
        </div>
      </div>
      <div className={styles.veil} aria-hidden="true" />
      <div className={styles.scrim} aria-hidden="true" />
      <div className={styles.top}>
        <p className={`t-eyebrow ${styles.eyebrow}`}>{hero.eyebrow}</p>
        <h1 id="hero-title" className={`t-h1 ${styles.title}`}>
          {hero.headline}
        </h1>
        <p className={`t-lead ${styles.lead}`}>
          <Hyphens text={hero.lead} />
        </p>
      </div>
      <div className={styles.bottom}>
        {/* Reserve Now and, beside it, the feel toggle (owner, 2026-10-23; made minimal 2026-10-28: two face swatches
            with their names): one row from 700 px, the toggle above the button on phones, under the racket like a
            caption. The stills with a Pace version and the checkout follow it (DESIGN.md
            "Feel toggle"). */}
        <div className={styles.actions}>
          <ReserveLink href="/reserve" className={`btn btn-primary ${styles.cta}`}>
            {site.ctaLabel}
          </ReserveLink>
          <FeelToggle label={site.feelToggleLabel} labels={feelToggleLabels} size="hero" />
        </div>
        <p className={`t-label ${styles.note}`}>{hero.ctaNote}</p>
      </div>
    </section>
  );
}
