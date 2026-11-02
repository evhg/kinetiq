import type { ReactNode } from "react";
import { ServerGrip } from "@/lib/grip-context";

// The bare variant of / (owner, 2026-11-02, the grip toggle): the same page, rendered (and prerendered) with the hero
// racket's overgrip off for a visitor whose `kq-grip` cookie says "off". src/proxy.ts rewrites / to it (inside the feel
// variant when `kq-feel` names one), so the address bar keeps /; a direct request for /feel/* is a 404.
export default function BareLayout({ children }: { children: ReactNode }) {
  return <ServerGrip grip="off">{children}</ServerGrip>;
}
