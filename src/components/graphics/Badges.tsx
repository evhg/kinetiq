"use client";

import { useRef } from "react";
import { gsap, useGSAP } from "@/lib/gsap";
import { useMotion } from "@/components/motion/MotionProvider";
import { bornWhole } from "@/content/copy";
import { Icon } from "./Icons";
import styles from "./Badges.module.css";

export type BadgeId = "swiss" | "patent";

const BADGES: Record<BadgeId, { icon: "swissCross" | "mould"; text: string }> = {
  swiss: { icon: "swissCross", text: bornWhole.badges[0] },
  patent: { icon: "mould", text: bornWhole.badges[1] },
};

export type BadgesProps = {
  className?: string;
  items?: BadgeId[];
  /** "row" wraps side by side (chapter band); "stack" lists them full width (reserve trust list). */
  layout?: "row" | "stack";
  align?: "start" | "center";
  /**
   * "self": fade up 12px when the badges enter the viewport.
   * "none": static; a parent scrub can animate the `[data-badge]` items instead.
   */
  reveal?: "self" | "none";
};

/** G13: hairline Swiss Made and patent badges. */
export function Badges({ className, items = ["swiss", "patent"], layout = "row", align = "start", reveal = "self" }: BadgesProps) {
  const root = useRef<HTMLUListElement>(null);
  const { motionOn } = useMotion();

  useGSAP(
    () => {
      if (!motionOn || reveal !== "self") return;
      const mm = gsap.matchMedia();
      mm.add("(prefers-reduced-motion: no-preference)", () => {
        gsap.from("[data-badge]", {
          y: 12,
          opacity: 0,
          duration: 0.6,
          ease: "power3.out",
          stagger: 0.08,
          scrollTrigger: { trigger: root.current, start: "top 85%", once: true },
        });
      });
      return () => mm.revert();
    },
    { scope: root, dependencies: [motionOn, reveal], revertOnUpdate: true },
  );

  return (
    <ul ref={root} className={`${styles.badges} ${className ?? ""}`} data-layout={layout} data-align={align}>
      {items.map((id) => (
        <li key={id} className={styles.badge} data-badge={id}>
          <Icon name={BADGES[id].icon} className={styles.icon} />
          <span>{BADGES[id].text}</span>
        </li>
      ))}
    </ul>
  );
}
