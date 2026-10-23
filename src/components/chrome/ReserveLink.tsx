"use client";

import Link from "next/link";
import type { ComponentProps } from "react";
import { useFeel, withFeel } from "@/lib/feel-store";

/**
 * A link into checkout that carries the visitor's chosen feel (`/reserve?tier=limited&feel=pace`), so /reserve opens on
 * the feel the toggle shows. Before any choice (and in the server render) it is the plain link: /reserve then falls
 * back to the stored choice, or Command.
 */
export function ReserveLink({ href, ...rest }: Omit<ComponentProps<typeof Link>, "href"> & { href: string }) {
  const { chosen } = useFeel();
  return <Link href={withFeel(href, chosen)} {...rest} />;
}
