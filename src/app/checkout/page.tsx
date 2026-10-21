import type { Metadata } from "next";
import { Suspense } from "react";
import { CheckoutForm } from "./CheckoutForm";

export const metadata: Metadata = { title: "Reserve | KINETIQ" };

export default function CheckoutPage() {
  return (
    <main id="main" className="page-narrow">
      <Suspense fallback={<p className="fineprint">Loading checkout…</p>}>
        <CheckoutForm />
      </Suspense>
    </main>
  );
}
