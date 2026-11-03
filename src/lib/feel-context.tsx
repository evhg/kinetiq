"use client";

import { createContext, type ReactNode } from "react";
import type { FeelId } from "@/content/prefs";

/**
 * The feel the server rendered this page in: null for the default pages (no choice known, so Command), or the visitor's
 * choice for the feel variants under app/feel/<feel>/, which src/proxy.ts serves in place of /, /reserve and /reserved
 * when the request carries the `kq-feel` cookie (lib/feel-store.ts). useFeel hydrates from it, so a returning Pace
 * visitor's page arrives in Pace, the hero and every still with a Pace version already pointing at their Pace files.
 */
export const ServerFeelContext = createContext<FeelId | null>(null);

export function ServerFeel({ feel, children }: { feel: FeelId; children: ReactNode }) {
  return <ServerFeelContext value={feel}>{children}</ServerFeelContext>;
}
