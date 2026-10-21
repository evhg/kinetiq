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
  /** Preselected from ?feel= by the page. */
  initialFeel?: FeelId | null;
};

/** The reservation page: a sticky gallery for the chosen edition beside the options column. */
export function ReserveExperience({ initialTier = "reserve", initialFeel = null }: Props) {
  const [tierId, setTierId] = useState<TierId>(initialTier);
  const [feel, setFeel] = useState<FeelId | null>(initialFeel);

  return (
    <div className={styles.layout}>
      <Gallery tierId={tierId} feel={feel ?? "command"} />
      <ReservePanel tierId={tierId} onTier={setTierId} feel={feel} onFeel={setFeel} />
    </div>
  );
}
