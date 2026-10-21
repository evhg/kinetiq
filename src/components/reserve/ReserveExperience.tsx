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
  /** Whether InviQtus can be paid for (decided on the server: codes plus a signed ambassador). */
  invitesOpen?: boolean;
};

/** The reservation page: a sticky gallery for the chosen edition beside the options column. */
export function ReserveExperience({ initialTier, initialFeel = null, invitesOpen = false }: Props) {
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
        preselected={initialTier !== undefined}
      />
    </div>
  );
}
