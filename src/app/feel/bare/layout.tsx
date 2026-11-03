import type { ReactNode } from "react";
import { ServerGrip } from "@/lib/grip-context";

// The bare variants of /, /reserve and /reserved (the grip toggle, owner 2026-11-02; every image, 2026-11-03): the same
// pages, rendered (and prerendered) with every racket's overgrip off for a visitor whose `kq-grip` cookie says "off".
// src/proxy.ts rewrites to them (inside the feel variant when `kq-feel` names one), so the address bar keeps the path; a
// direct request for /feel/* is a 404.
export default function BareLayout({ children }: { children: ReactNode }) {
  return <ServerGrip grip="off">{children}</ServerGrip>;
}
