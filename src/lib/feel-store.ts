import { useContext, useSyncExternalStore } from "react";
import {
  DEFAULT_FEEL,
  FEEL_COOKIE_MAX_AGE,
  FEEL_COOKIE_RENEW_URL,
  FEEL_PREFERENCE_KEY,
  feelFromCookie,
  isFeelId,
  storedFeel,
  type FeelId,
} from "@/content/site";
import { ServerFeelContext } from "./feel-context";

/**
 * The site-wide feel (Command or Pace), shared by every feel toggle, every still that has a Pace version, the Reserve
 * Now links and the checkout. Kept in the visitor's own browser (localStorage, FEEL_PREFERENCE_KEY), mirrored in a
 * first-party cookie of the same name so the server can send the next page already in that feel (src/proxy.ts); when
 * storage is blocked the choice lasts for the page's life (and the cookie, where cookies are allowed). `html[data-feel]` mirrors it: the head
 * script sets it before the first paint (feelInitScript, lib/motion-preference.ts), and CSS that must not flash (the
 * toggles' thumb, a still waiting for its Pace version) reads it from there. Client modules only.
 */
let memory: FeelId | null = null;
const listeners = new Set<() => void>();

function read(): FeelId | null {
  return storedFeel() ?? memory ?? cookieFeel();
}

function cookieFeel(): FeelId | null {
  try {
    return feelFromCookie(document.cookie);
  } catch {
    return null;
  }
}

/**
 * The cookie mirror (site.ts FEEL_PREFERENCE_KEY): lets src/proxy.ts serve the next page already in this feel. The head
 * script (lib/motion-preference.ts) writes the same cookie with the same attributes.
 */
function writeCookie(f: FeelId) {
  try {
    const secure = window.location.protocol === "https:" ? "; Secure" : "";
    document.cookie = `${FEEL_PREFERENCE_KEY}=${f}; Path=/; Max-Age=${FEEL_COOKIE_MAX_AGE}; SameSite=Lax${secure}`;
  } catch {
    // cookies blocked: the page still follows the choice; the next visit simply opens on the default page
    return;
  }
  renewFeelCookie();
}

let renewTimer: ReturnType<typeof setTimeout> | undefined;

/**
 * Safari holds a cookie written by script to 7 days (ITP); one set by the server keeps its year. So once the choice
 * settles (a second after the last toggle, so a quick back-and-forth sends one request, never two that could land out
 * of order), a HEAD of / carries the new cookie to src/proxy.ts, which sends it back with Set-Cookie: the choice holds
 * even if the visitor opens no other page for a week. Fails quietly (offline, gate not cleared: no Set-Cookie).
 */
function renewFeelCookie() {
  clearTimeout(renewTimer);
  renewTimer = setTimeout(() => {
    try {
      void fetch(FEEL_COOKIE_RENEW_URL, { method: "HEAD", cache: "no-store", credentials: "same-origin", keepalive: true }).catch(
        () => {},
      );
    } catch {
      // no fetch: the next page load renews the cookie instead
    }
  }, 1000);
}

function mark(f: FeelId) {
  document.documentElement.dataset.feel = f;
}

function subscribe(onChange: () => void) {
  listeners.add(onChange);
  // Another tab changed it: follow, so the toggles, the stills and the checkout agree everywhere.
  const onStorage = (e: StorageEvent) => {
    if (e.key !== null && e.key !== FEEL_PREFERENCE_KEY) return;
    const f = storedFeel();
    mark(f ?? DEFAULT_FEEL);
    onChange();
  };
  window.addEventListener("storage", onStorage);
  return () => {
    listeners.delete(onChange);
    window.removeEventListener("storage", onStorage);
  };
}

/** Records a choice of feel: in storage (quietly skipped where blocked), on `html[data-feel]`, then for every reader. */
export function setFeel(f: FeelId) {
  if (!isFeelId(f)) return;
  memory = f;
  try {
    window.localStorage.setItem(FEEL_PREFERENCE_KEY, f);
  } catch {
    // private window or blocked storage: the in-memory choice still holds for this page
  }
  writeCookie(f);
  mark(f);
  for (const l of listeners) l();
  for (const l of choiceListeners) l(f);
}

const choiceListeners = new Set<(f: FeelId) => void>();

/**
 * Calls `onChoice` whenever any toggle on the page records a choice (setFeel), never for the hydration or another tab.
 * For a reader that holds its own feel above the stored one (the /reserve experience, preselected from ?feel=), so a
 * later choice in the header still reaches it. Returns the unsubscribe.
 */
export function onFeelChoice(onChoice: (f: FeelId) => void) {
  choiceListeners.add(onChoice);
  return () => {
    choiceListeners.delete(onChoice);
  };
}

const none = () => null;

/**
 * The feel on show (`feel`, Command until a choice is made) and the choice itself (`chosen`, null until one is made).
 * The server and the hydrating render see the feel the page was rendered in (ServerFeelContext): the visitor's choice
 * on a feel variant (app/feel/<feel>/, served by src/proxy.ts from the `kq-feel` cookie), else no choice, so Command.
 * A stored choice the server did not know (a first visit since the cookie existed) follows right after hydration.
 */
export function useFeel() {
  const server = useContext(ServerFeelContext);
  const chosen = useSyncExternalStore(subscribe, read, server === null ? none : () => server);
  return { feel: chosen ?? DEFAULT_FEEL, chosen, setFeel };
}

/** `/reserve?tier=limited` with the chosen feel added (`&feel=pace`), or the link unchanged before any choice. */
export function withFeel(href: string, feel: FeelId | null) {
  if (!feel) return href;
  return `${href}${href.includes("?") ? "&" : "?"}feel=${feel}`;
}
