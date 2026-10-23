"use client";

import { useState, useSyncExternalStore } from "react";
import type { TierId } from "@/content/lineup";
import { DEFAULT_FEEL, FEEL_PREFERENCE_KEY, storedFeel, type FeelId } from "@/content/site";
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

/** Follows the stored feel across tabs (the toggle a later release adds writes it). */
const subscribeFeel = (onChange: () => void) => {
  const onStorage = (e: StorageEvent) => {
    if (e.key === null || e.key === FEEL_PREFERENCE_KEY) onChange();
  };
  window.addEventListener("storage", onStorage);
  return () => window.removeEventListener("storage", onStorage);
};
const noStoredFeel = () => null;

/**
 * The reservation page: a sticky gallery for the chosen edition beside the options column. The feel is Command until
 * the buyer chooses (owner, 2026-10-23: the site opens on Command); a feel from the link (?feel=) or the site-wide
 * choice counts as chosen. Until a feel is chosen, the gallery opens on the two feels together (Gallery `chosen`).
 */
export function ReserveExperience({ initialTier, initialFeel = null, invitesOpen = false, initialInvite = null }: Props) {
  const [tierId, setTierId] = useState<TierId>(initialTier ?? "reserve");
  const [picked, setPicked] = useState<FeelId | null>(null);
  const stored = useSyncExternalStore(subscribeFeel, storedFeel, noStoredFeel);
  const choice = picked ?? initialFeel ?? stored;
  const feel = choice ?? DEFAULT_FEEL;

  return (
    <div className={styles.layout}>
      <Gallery tierId={tierId} feel={feel} chosen={choice !== null} />
      <ReservePanel
        tierId={tierId}
        onTier={setTierId}
        feel={feel}
        onFeel={setPicked}
        invitesOpen={invitesOpen}
        initialInvite={initialInvite}
        preselected={initialTier !== undefined}
      />
    </div>
  );
}
