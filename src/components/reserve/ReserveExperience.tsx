"use client";

import { useState } from "react";
import type { TierId } from "@/content/lineup";
import { DEFAULT_FEEL, type FeelId } from "@/content/site";
import { setFeel, useFeel } from "@/lib/feel-store";
import { Gallery } from "./Gallery";
import { ReservePanel } from "./ReservePanel";
import styles from "./Reserve.module.css";

type Props = {
  /** Preselected from ?tier= by the page (already checked for availability). */
  initialTier?: TierId;
  /** Preselected from ?feel= by the page; otherwise the stored site-wide choice, or Command (an option is always chosen). */
  initialFeel?: FeelId | null;
  /** Whether invitation codes exist (decided on the server); One of Ten still needs a valid one. */
  invitesOpen?: boolean;
  /** ?invite= from the link: a code to check on load, "" to open the code field, null without it. */
  initialInvite?: string | null;
};

/**
 * The reservation page: a sticky gallery for the chosen edition beside the options column. The feel is Command until
 * the buyer chooses (owner, 2026-10-23: the site opens on Command); a feel from the link (?feel=) or the site-wide
 * choice counts as chosen. Until a feel is chosen, the gallery opens on the two feels together (Gallery `chosen`).
 */
export function ReserveExperience({ initialTier, initialFeel = null, invitesOpen = false, initialInvite = null }: Props) {
  const [tierId, setTierId] = useState<TierId>(initialTier ?? "reserve");
  const [picked, setPicked] = useState<FeelId | null>(null);
  // The site-wide choice (the landing's toggle, or an earlier visit here), followed across tabs (lib/feel-store.ts).
  const { chosen: stored } = useFeel();
  const choice = picked ?? initialFeel ?? stored;
  const feel = choice ?? DEFAULT_FEEL;

  return (
    <div className={styles.layout}>
      <Gallery tierId={tierId} feel={feel} chosen={choice !== null} />
      <ReservePanel
        tierId={tierId}
        onTier={setTierId}
        feel={feel}
        onFeel={(id) => {
          // The feel chosen here is the site's choice too: the landing's toggles and stills follow it.
          setPicked(id);
          setFeel(id);
        }}
        invitesOpen={invitesOpen}
        initialInvite={initialInvite}
        preselected={initialTier !== undefined}
      />
    </div>
  );
}
