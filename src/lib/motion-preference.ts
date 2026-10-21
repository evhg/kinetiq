/**
 * Runs before hydration (inlined in <head>): html[data-motion] follows the OS
 * reduced-motion setting only. There is no on-page motion switch (owner, 2026-10-21).
 */
export const motionInitScript = `(() => {
  try {
    var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    document.documentElement.dataset.motion = reduce ? "off" : "on";
  } catch (e) {
    document.documentElement.dataset.motion = "on";
  }
})();`;
