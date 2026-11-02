import {
  DEFAULT_FEEL,
  DEFAULT_GRIP,
  FEEL_COOKIE_MAX_AGE,
  FEEL_COOKIE_RENEW_URL,
  FEEL_PREFERENCE_KEY,
  GRIP_PREFERENCE_KEY,
} from "@/content/site";
import { NDA_ARRIVE_MS, NDA_TRIED_KEY } from "./nda";

/**
 * Runs before hydration (inlined in <head>): html[data-motion] follows the OS
 * reduced-motion setting only. There is no on-page motion switch (owner, 2026-10-21).
 * It also marks a page that loads right after the NDA gate (html[data-arrive]): its first frame is painted under
 * the same void the gate faded into, which then lifts (globals.css), so leaving the gate and arriving read as one
 * move. Reduced motion: no veil.
 * And html[data-feel] (command or pace): the visitor's stored feel (lib/feel-store.ts), else Command, so the feel
 * toggles and the stills with a Pace version paint the right feel from the first frame. It restores the `kq-feel`
 * cookie when it is missing or out of step with the stored choice (lib/feel-store.ts writes both on a choice), so a
 * visitor whose choice predates the cookie, or whose cookie expired, gets the page in their feel from the server on the
 * next load (src/proxy.ts), and then, after the load event, has the server renew it (a HEAD of /: site.ts
 * FEEL_COOKIE_MAX_AGE). It never rewrites a cookie that is already in step: the server renews that one on every page
 * load, and a script write would put it back under Safari's 7-day cap on script-written cookies (ITP). With nothing
 * stored (storage blocked or cleared; ITP also clears script storage after 7 days without a visit) the cookie alone
 * stands for the choice.
 * And html[data-grip] (on or off): the hero racket with or without its overgrip (lib/grip-store.ts), from localStorage,
 * else the `kq-grip` cookie, else on (a stored choice missing from the cookie is written back, as for the feel), so
 * the grip toggle's ring and the hero still hidden for a stored "off" are right from the first frame.
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
  var key = ${JSON.stringify(FEEL_PREFERENCE_KEY)};
  var feel = ${JSON.stringify(DEFAULT_FEEL)};
  var stored = null;
  try {
    stored = localStorage.getItem(key);
  } catch (e) {}
  var cookie = null;
  try {
    var m = document.cookie.match(new RegExp("(?:^|; *)" + key + "=([a-z]+)"));
    if (m) cookie = m[1];
  } catch (e) {}
  if (stored === "command" || stored === "pace") {
    feel = stored;
    if (cookie !== stored) {
      try {
        document.cookie = key + "=" + stored + "; Path=/; Max-Age=${FEEL_COOKIE_MAX_AGE}; SameSite=Lax" +
          (location.protocol === "https:" ? "; Secure" : "");
        addEventListener("load", function () {
          try {
            fetch(${JSON.stringify(FEEL_COOKIE_RENEW_URL)}, { method: "HEAD", cache: "no-store", credentials: "same-origin" })
              .catch(function () {});
          } catch (e) {}
        }, { once: true });
      } catch (e) {}
    }
  } else if (cookie === "command" || cookie === "pace") feel = cookie;
  document.documentElement.dataset.feel = feel;
  var gkey = ${JSON.stringify(GRIP_PREFERENCE_KEY)};
  var grip = ${JSON.stringify(DEFAULT_GRIP)};
  var g = null;
  try {
    g = localStorage.getItem(gkey);
  } catch (e) {}
  var gc = null;
  try {
    var gm = document.cookie.match(new RegExp("(?:^|; *)" + gkey + "=([a-z]+)"));
    if (gm) gc = gm[1];
  } catch (e) {}
  if (g === "on" || g === "off") {
    grip = g;
    if (gc !== g) {
      try {
        document.cookie = gkey + "=" + g + "; Path=/; Max-Age=${FEEL_COOKIE_MAX_AGE}; SameSite=Lax" +
          (location.protocol === "https:" ? "; Secure" : "");
      } catch (e) {}
    }
  } else if (gc === "on" || gc === "off") grip = gc;
  document.documentElement.dataset.grip = grip;
})();`;
