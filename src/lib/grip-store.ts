import { useSyncExternalStore } from "react";
import { DEFAULT_GRIP, GRIP_PREFERENCE_KEY, isGripId, storedGrip, type GripId } from "@/content/site";

/**
 * The hero racket with or without its overgrip (owner, 2026-11-02), shared by the grip toggle, the hero's stills (the
 * K01-nogrip variants, `<Still bare>`) and the hero swivel (no sequence without the grip yet, so the still shows).
 * Kept in the visitor's own browser (localStorage, GRIP_PREFERENCE_KEY); when storage is blocked the choice lasts for
 * the page's life. `html[data-grip]` mirrors it: the head script sets it before the first paint (lib/motion-preference.ts),
 * so the toggle's ring and a still waiting for its other variant never flash the wrong state. No cookie: the server
 * always paints the grip on (the default, and the only variant the first screen downloads); a stored "off" swaps in
 * after hydration, hidden from the first paint by html[data-grip] (DESIGN.md "Grip toggle"). Client modules only.
 */
let memory: GripId | null = null;
const listeners = new Set<() => void>();

function read(): GripId {
  return storedGrip() ?? memory ?? DEFAULT_GRIP;
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

/** Records a choice: in storage (quietly skipped where blocked), on `html[data-grip]`, then for every reader. */
export function setGrip(g: GripId) {
  if (!isGripId(g)) return;
  memory = g;
  try {
    window.localStorage.setItem(GRIP_PREFERENCE_KEY, g);
  } catch {
    // private window or blocked storage: the in-memory choice still holds for this page
  }
  mark(g);
  for (const l of listeners) l();
}

const server = () => DEFAULT_GRIP;

/** The grip on show: "on" on the server and the hydrating render, then the visitor's stored choice. */
export function useGrip() {
  const grip = useSyncExternalStore(subscribe, read, server);
  return { grip, setGrip };
}
