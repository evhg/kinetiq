import { NDA_ARRIVE_MS, NDA_TRIED_KEY } from "./nda";

/**
 * Runs before hydration (inlined in <head>): html[data-motion] follows the OS
 * reduced-motion setting only. There is no on-page motion switch (owner, 2026-10-21).
 * It also marks a page that loads right after the NDA gate (html[data-arrive]): its first frame is painted under
 * the same void the gate faded into, which then lifts (globals.css), so leaving the gate and arriving read as one
 * move. Reduced motion: no veil.
 */
export const motionInitScript = `(() => {
  var reduce = false;
  try {
    reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    document.documentElement.dataset.motion = reduce ? "off" : "on";
  } catch (e) {
    document.documentElement.dataset.motion = "on";
  }
  try {
    var tried = Number(sessionStorage.getItem(${JSON.stringify(NDA_TRIED_KEY)})) || 0;
    if (!reduce && tried && Date.now() - tried < ${NDA_ARRIVE_MS}) document.documentElement.dataset.arrive = "";
  } catch (e) {}
})();`;
