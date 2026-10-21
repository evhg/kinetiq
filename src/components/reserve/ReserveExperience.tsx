"use client";

import { useEffect, useState } from "react";
import { tierById, type TierId } from "@/content/lineup";
import { isFeelId, type FeelId } from "@/content/site";
import { Gallery } from "./Gallery";
import { ReservePanel } from "./ReservePanel";
import styles from "./Reserve.module.css";

/** The reservation page: a sticky gallery for the chosen edition beside the options column. */
export function ReserveExperience() {
  const [tierId, setTierId] = useState<TierId>("reserve");
  const [feel, setFeel] = useState<FeelId | null>(null);

  // Links from the landing page can preselect an edition (?tier=) and a feel (?feel=).
  useEffect(() => {
    const q = new URLSearchParams(window.location.search);
    const t = tierById(q.get("tier"));
    const f = q.get("feel");
    /* eslint-disable react-hooks/set-state-in-effect -- one-time sync from the URL */
    if (t && t.available) setTierId(t.id);
    if (isFeelId(f)) setFeel(f);
    /* eslint-enable react-hooks/set-state-in-effect */
  }, []);

  return (
    <div className={styles.layout}>
      <Gallery tierId={tierId} feel={feel ?? "command"} />
      <ReservePanel tierId={tierId} onTier={setTierId} feel={feel} onFeel={setFeel} />
    </div>
  );
}
