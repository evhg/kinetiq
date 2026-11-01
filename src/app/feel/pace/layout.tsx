import type { ReactNode } from "react";
import { ServerFeel } from "@/lib/feel-context";

// The Pace variants of /, /reserve and /reserved: the same pages, rendered (and prerendered) in Pace for a visitor whose
// `kq-feel` cookie names it. src/proxy.ts rewrites to them, so the address bar keeps /, /reserve or /reserved; a direct
// request for /feel/* is a 404. lib/feel-context.tsx.
export default function PaceLayout({ children }: { children: ReactNode }) {
  return <ServerFeel feel="pace">{children}</ServerFeel>;
}
