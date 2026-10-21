export const MOTION_STORAGE_KEY = "kinetiq-motion";

export type MotionSetting = "on" | "off";

/**
 * Runs before hydration (inlined in <head>) so the first paint already
 * matches the saved choice or the OS reduced-motion setting.
 */
export const motionInitScript = `(() => {
  try {
    var saved = localStorage.getItem("${MOTION_STORAGE_KEY}");
    var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var motion = saved === "on" || saved === "off" ? saved : reduce ? "off" : "on";
    document.documentElement.dataset.motion = motion;
  } catch (e) {
    document.documentElement.dataset.motion = "off";
  }
})();`;
