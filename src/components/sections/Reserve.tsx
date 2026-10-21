"use client";

import { useState } from "react";
import { ModelPicker } from "@/components/ModelPicker";
import { Cta } from "@/components/Cta";
import { models, site, type ModelId } from "@/content/site";

export function Reserve() {
  const [model, setModel] = useState<ModelId>("command");
  const m = models[model];
  return (
    <section id="reserve" className="section reserve" aria-labelledby="reserve-title">
      <h2 id="reserve-title" className="display">
        Two rackets. One piece each.
      </h2>
      <ModelPicker value={model} onChange={setModel} name="reserve-model" />
      <div className="reserve-grid" aria-live="polite">
        <div>
          <p className="model-name">{m.name}</p>
          <p className="model-line">{m.line}</p>
          <p>{m.feel}</p>
          <p>{m.forPlayer}</p>
        </div>
        <dl className="specs">
          {m.specs.map(([k, v]) => (
            <div key={k}>
              <dt>{k}</dt>
              <dd>{v}</dd>
            </div>
          ))}
        </dl>
      </div>
      <div className="reserve-buy">
        <p className="price">{site.priceLabel}</p>
        <ul className="terms">
          <li>{site.paymentLabel}.</li>
          <li>{site.shipLabel}.</li>
          <li>{site.refundLabel}.</li>
          <li>{site.shippingLabel}.</li>
        </ul>
        <Cta model={model} note={false} />
      </div>
    </section>
  );
}
