"use client";

import { useState } from "react";
import { useSearchParams } from "next/navigation";
import { ModelPicker } from "@/components/ModelPicker";
import { isModelId, models, site, type ModelId } from "@/content/site";

export function CheckoutForm() {
  const params = useSearchParams();
  const initial = params.get("model");
  const status = params.get("status");
  const [model, setModel] = useState<ModelId>(isModelId(initial) ? initial : "command");

  return (
    <form className="checkout" method="post" action="/api/checkout">
      {status === "preview" ? (
        <p className="notice" role="status">
          Payments are not open yet. At launch this button takes you straight to Stripe&rsquo;s secure checkout.
        </p>
      ) : null}
      {status === "error" ? (
        <p className="notice notice--error" role="alert">
          The payment page could not open. Nothing was charged. Try again in a moment.
        </p>
      ) : null}

      <h1 className="display-2">Reserve your KINETIQ</h1>
      <ModelPicker value={model} onChange={setModel} />
      <p className="checkout-line">{models[model].line}</p>

      <dl className="summary">
        <div>
          <dt>KINETIQ {models[model].name}</dt>
          <dd>{site.priceLabel}</dd>
        </div>
        <div>
          <dt>Shipping</dt>
          <dd>Free in Europe</dd>
        </div>
        <div className="summary-total">
          <dt>Total today</dt>
          <dd>{site.priceLabel}</dd>
        </div>
      </dl>
      <ul className="terms">
        <li>{site.shipLabel}.</li>
        <li>{site.refundLabel}.</li>
      </ul>
      <button className="cta cta--block" type="submit">
        Continue to secure payment
      </button>
      <p className="fineprint">Payment is handled by Stripe. We never see your card details.</p>
    </form>
  );
}
