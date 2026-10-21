"use client";

import { useEffect, useState } from "react";
import { ModelPicker } from "@/components/ModelPicker";
import { RacketSvg } from "@/components/RacketSvg";
import {
  editionOrder,
  editions,
  isEditionId,
  isModelId,
  models,
  site,
  type EditionId,
  type ModelId,
} from "@/content/site";

const badge: Record<EditionId, string> = {
  kinetiq: "Serial-numbered",
  founders: "No. 001 / 500",
  atelier: "No. 01 / 50",
};

export function ReserveForm() {
  // Rendered statically with defaults (fast first paint, no layout shift), then
  // synced from the URL (?edition=&model=&status=) after hydration.
  const [edition, setEdition] = useState<EditionId>("kinetiq");
  const [model, setModel] = useState<ModelId>("command");
  const [status, setStatus] = useState<string | null>(null);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const e = params.get("edition");
    const m = params.get("model");
    /* eslint-disable react-hooks/set-state-in-effect -- one-time sync from the URL */
    if (isEditionId(e) && editions[e].available) setEdition(e);
    if (isModelId(m)) setModel(m);
    setStatus(params.get("status"));
    /* eslint-enable react-hooks/set-state-in-effect */
  }, []);
  const chosen = editions[edition];

  return (
    <form className="reserve-layout" method="post" action="/api/checkout">
      <div className="reserve-visual" aria-hidden="true">
        <RacketSvg className="reserve-svg" title="" />
        <p className="reserve-badge" key={edition}>
          {badge[edition]}
        </p>
      </div>

      <div className="reserve-panel">
        {status === "preview" ? (
          <p className="notice" role="status">
            Payments open at launch. This button will take you straight to Stripe&rsquo;s secure card page.
          </p>
        ) : null}
        {status === "error" ? (
          <p className="notice notice--error" role="alert">
            The card page could not open. Nothing was charged. Please try again.
          </p>
        ) : null}

        <h1 className="display-2">Reserve your KINETIQ</h1>
        <p className="reserve-sub">{site.shipLabel}. {site.refundShort}.</p>

        <fieldset className="editions">
          <legend className="step">Choose your edition</legend>
          {editionOrder.map((id) => {
            const ed = editions[id];
            return (
              <label key={id} className="edition" data-checked={edition === id} data-disabled={!ed.available}>
                <input
                  type="radio"
                  name="edition"
                  value={id}
                  checked={edition === id}
                  disabled={!ed.available}
                  onChange={() => setEdition(id)}
                />
                <span className="edition-head">
                  <span className="edition-name">{ed.name}</span>
                  <span className="edition-price">{ed.available ? ed.priceLabel : "Sold out"}</span>
                </span>
                <span className="edition-tagline">{ed.tagline}</span>
                {edition === id ? (
                  <ul className="edition-includes">
                    {ed.includes.map((line) => (
                      <li key={line}>{line}</li>
                    ))}
                  </ul>
                ) : null}
              </label>
            );
          })}
        </fieldset>

        <div className="model-step">
          <p className="step" id="model-step">
            Choose your racket
          </p>
          <ModelPicker value={model} onChange={setModel} />
          <p className="model-step-line">
            <strong>{models[model].name}.</strong> {models[model].line} {models[model].feel}
          </p>
        </div>

        <ul className="trust">
          <li>
            <strong>{site.refundShort}.</strong> Cancel any time before your racket ships and every euro comes
            back. No questions.
          </li>
          <li>Secure card payment by Stripe. We never see your card number.</li>
          <li>{site.shippingLabel}.</li>
          <li>We only ask for what we need to deliver it: your email, name and address.</li>
        </ul>

        <div className="pay-bar">
          <div className="due">
            <span className="due-label">Due today</span>
            <span className="due-amount">{chosen.priceLabel}</span>
            <span className="due-note">{site.refundShort}</span>
          </div>
          <button className="cta cta--block" type="submit">
            {site.payLabel}
          </button>
        </div>
      </div>
    </form>
  );
}
