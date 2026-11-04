"use client";

import { createContext, type ReactNode } from "react";
import type { GripId } from "@/content/prefs";

/**
 * The grip state the server rendered this page in: null for the default pages (grip on), or "off" for the bare
 * variants of / (app/feel/bare, app/feel/<feel>/bare), which src/proxy.ts serves in place of / when the request carries
 * `kq-grip=off` (lib/grip-store.ts). useGrip hydrates from it, so a returning "Naked" visitor's hero arrives bare, its
 * <picture> already pointing at the K01-nogrip files.
 */
export const ServerGripContext = createContext<GripId | null>(null);

export function ServerGrip({ grip, children }: { grip: GripId; children: ReactNode }) {
  return <ServerGripContext value={grip}>{children}</ServerGripContext>;
}
