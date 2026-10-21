import type { Metadata } from "next";
import Link from "next/link";
import { site } from "@/content/site";

export const metadata: Metadata = { title: "Reserved | KINETIQ" };

export default function ReservedPage() {
  return (
    <main id="main" className="page-narrow reserved">
      <h1 className="display">You&rsquo;re in.</h1>
      <p className="lead">Your KINETIQ is reserved from the first production run.</p>
      <ul className="terms">
        <li>Stripe has emailed your receipt.</li>
        <li>{site.shipLabel}. We&rsquo;ll email you before it leaves St. Gallen.</li>
        <li>{site.refundLabel}.</li>
      </ul>
      <Link className="link-quiet" href="/">
        Back to KINETIQ
      </Link>
    </main>
  );
}
