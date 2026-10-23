import { useSyncExternalStore } from "react";
import { DEFAULT_FEEL, FEEL_PREFERENCE_KEY, isFeelId, storedFeel, type FeelId } from "@/content/site";

/**
 * The site-wide feel (Command or Pace), shared by every feel toggle, every still that has a Pace version, the Reserve
 * Now links and the checkout. Kept in the visitor's own browser (localStorage, FEEL_PREFERENCE_KEY), never sent
 * anywhere; when storage is blocked the choice lasts for the page's life only. `html[data-feel]` mirrors it: the head
 * script sets it before the first paint (feelInitScript, lib/motion-preference.ts), and CSS that must not flash (the
 * toggles' thumb, a still waiting for its Pace version) reads it from there. Client modules only.
 */
let memory: FeelId | null = null;
const listeners = new Set<() => void>();

function read(): FeelId | null {
  return storedFeel() ?? memory;
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
  mark(f);
  for (const l of listeners) l();
}

const none = () => null;

/**
 * The feel on show (`feel`, Command until a choice is made) and the choice itself (`chosen`, null until one is made).
 * The server and the hydrating render see no choice, so they paint Command; a stored Pace follows right after.
 */
export function useFeel() {
  const chosen = useSyncExternalStore(subscribe, read, none);
  return { feel: chosen ?? DEFAULT_FEEL, chosen, setFeel };
}

/** `/reserve?tier=limited` with the chosen feel added (`&feel=pace`), or the link unchanged before any choice. */
export function withFeel(href: string, feel: FeelId | null) {
  if (!feel) return href;
  return `${href}${href.includes("?") ? "&" : "?"}feel=${feel}`;
}
