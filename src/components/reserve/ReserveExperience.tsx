"use client";

import { useState } from "react";
import type { TierId } from "@/content/lineup";
import type { FeelId } from "@/content/site";
import { Gallery } from "./Gallery";
import { ReservePanel } from "./ReservePanel";
import styles from "./Reserve.module.css";

type Props = {
  /** Preselected from ?tier= by the page (already checked for availability). */
  initialTier?: TierId;
  /** Preselected from ?feel= by the page; Command otherwise (an option is always chosen, as on Tesla's page). */
  initialFeel?: FeelId | null;
  /** Whether invitation codes exist (decided on the server); InviQtus still needs a valid one. */
  invitesOpen?: boolean;
  /** ?invite= from the link: a code to check on load, "" to open the code field, null without it. */
  initialInvite?: string | null;
};

/** The reservation page: a sticky gallery for the chosen edition beside the options column. */
export function ReserveExperience({ initialTier, initialFeel = null, invitesOpen = false, initialInvite = null }: Props) {
  const [tierId, setTierId] = useState<TierId>(initialTier ?? "reserve");
  const [feel, setFeel] = useState<FeelId>(initialFeel ?? "command");

  return (
    <div className={styles.layout}>
      <Gallery tierId={tierId} feel={feel} />
      <ReservePanel
        tierId={tierId}
        onTier={setTierId}
        feel={feel}
        onFeel={setFeel}
        invitesOpen={invitesOpen}
        initialInvite={initialInvite}
        preselected={initialTier !== undefined}
      />
    </div>
  );
}
