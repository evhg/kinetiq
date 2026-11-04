import { useContext, useSyncExternalStore } from "react";
import {
  DEFAULT_GRIP,
  FEEL_COOKIE_MAX_AGE,
  FEEL_COOKIE_RENEW_URL,
  GRIP_PREFERENCE_KEY,
  gripFromCookie,
  isGripId,
  storedGrip,
  type GripId,
} from "@/content/prefs";
import { ServerGripContext } from "./grip-context";

/**
 * The hero racket with or without its overgrip (owner, 2026-11-02), shared by the grip toggle, the hero's stills (the
 * K01-nogrip variants, `<Still bare>`) and the hero swivel (K01-swivel-nogrip-<feel>-<layout> without the grip).
 * Kept in the visitor's own browser (localStorage, GRIP_PREFERENCE_KEY) and mirrored in a first-party cookie of the
 * same name, as the feel is (lib/feel-store.ts): src/proxy.ts serves a returning "Naked" visitor / already rendered bare
 * (app/feel/bare, app/feel/<feel>/bare), so the first screen downloads the bare stills alone. When storage is blocked
 * the choice lasts for the page's life (and the cookie, where cookies are allowed). `html[data-grip]` mirrors it: the
 * head script sets it before the first paint (lib/motion-preference.ts), so the toggle's ring and a still waiting for
 * its other variant never flash the wrong state (DESIGN.md "Grip toggle"). Client modules only.
 */
let memory: GripId | null = null;
const listeners = new Set<() => void>();

function cookieGrip(): GripId | null {
  try {
    return gripFromCookie(document.cookie);
  } catch {
    return null;
  }
}

function read(): GripId {
  return storedGrip() ?? memory ?? cookieGrip() ?? DEFAULT_GRIP;
}

/** The cookie mirror: lets src/proxy.ts serve the next / already in this grip state. Same attributes as `kq-feel`. */
function writeCookie(g: GripId) {
  try {
    const secure = window.location.protocol === "https:" ? "; Secure" : "";
    document.cookie = `${GRIP_PREFERENCE_KEY}=${g}; Path=/; Max-Age=${FEEL_COOKIE_MAX_AGE}; SameSite=Lax${secure}`;
  } catch {
    // cookies blocked: the page still follows the choice; the next visit opens with the grip on, then follows storage
    return;
  }
  renewCookie();
}

let renewTimer: ReturnType<typeof setTimeout> | undefined;

/**
 * As for the feel: once the choice settles, a HEAD of / carries the new cookie to src/proxy.ts, which sends it back with
 * Set-Cookie, so Safari's 7-day cap on script-written cookies does not apply. Fails quietly.
 */
function renewCookie() {
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

function mark(g: GripId) {
  document.documentElement.dataset.grip = g;
}

function subscribe(onChange: () => void) {
  listeners.add(onChange);
  // Another tab changed it: follow.
  const onStorage = (e: StorageEvent) => {
    if (e.key !== null && e.key !== GRIP_PREFERENCE_KEY) return;
    mark(storedGrip() ?? DEFAULT_GRIP);
    onChange();
  };
  window.addEventListener("storage", onStorage);
  return () => {
    listeners.delete(onChange);
    window.removeEventListener("storage", onStorage);
  };
}

/** Records a choice: in storage (quietly skipped where blocked), in the cookie, on `html[data-grip]`, then for every reader. */
export function setGrip(g: GripId) {
  if (!isGripId(g)) return;
  memory = g;
  try {
    window.localStorage.setItem(GRIP_PREFERENCE_KEY, g);
  } catch {
    // private window or blocked storage: the in-memory choice still holds for this page
  }
  writeCookie(g);
  mark(g);
  for (const l of listeners) l();
}

const on = () => DEFAULT_GRIP;
const off = (): GripId => "off";

/**
 * The grip on show. The server and the hydrating render see the state the page was rendered in (ServerGripContext:
 * "off" on the bare variants of /, else on); a stored choice the server did not know follows right after hydration.
 */
export function useGrip() {
  const server = useContext(ServerGripContext);
  const grip = useSyncExternalStore(subscribe, read, server === "off" ? off : on);
  return { grip, setGrip };
}
