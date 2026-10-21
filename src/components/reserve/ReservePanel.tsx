"use client";

import { useEffect, useId, useRef, useState, type FormEvent } from "react";
import { Badges } from "@/components/graphics/Badges";
import { TierGlyph } from "@/components/graphics/Icons";
import { EXTRAS_THRESHOLD_EUR, deliveryCountries, priceLabel, tiers, tierById, type TierId } from "@/content/lineup";
import { reserveCopy } from "@/content/reserve";
import { feels, site, type FeelId } from "@/content/site";
import { loadStripe, type Stripe, type StripeElement, type StripeElements } from "@/lib/stripe-client";
import styles from "./Reserve.module.css";

type Stage = "choose" | "details" | "processing" | "done";
type Fields = {
  name: string;
  email: string;
  line1: string;
  line2: string;
  postal_code: string;
  city: string;
  country: string;
  invite: string;
};

const EMPTY: Fields = { name: "", email: "", line1: "", line2: "", postal_code: "", city: "", country: "", invite: "" };
const PK = process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY;

type Props = {
  tierId: TierId;
  onTier: (id: TierId) => void;
  feel: FeelId | null;
  onFeel: (id: FeelId) => void;
};

/**
 * The options column: edition, feel, Due Today and Pay with Card. Pay with Card opens the delivery
 * and card form in place, ending in one Place Reservation button that charges the card right here.
 */
export function ReservePanel({ tierId, onTier, feel, onFeel }: Props) {
  const [stage, setStage] = useState<Stage>("choose");
  const [fields, setFields] = useState<Fields>(EMPTY);
  const [error, setError] = useState<string | null>(null);
  const [badFields, setBadFields] = useState<string[]>([]);
  const [feelMissing, setFeelMissing] = useState(false);
  const [cardReady, setCardReady] = useState(false);
  const [paid, setPaid] = useState<{ tier: TierId; feel: FeelId; email: string } | null>(null);
  const [payVisible, setPayVisible] = useState(true);
  const formRef = useRef<HTMLFormElement>(null);
  const payRef = useRef<HTMLButtonElement>(null);
  const feelRef = useRef<HTMLFieldSetElement>(null);
  const cardRef = useRef<HTMLDivElement>(null);
  const stripeRef = useRef<Stripe | null>(null);
  const elementsRef = useRef<StripeElements | null>(null);
  const paymentRef = useRef<StripeElement | null>(null);
  const attemptRef = useRef<string>("");
  const uid = useId();
  const tier = tierById(tierId)!;
  const open = stage !== "choose";
  const extras = tier.priceEur > EXTRAS_THRESHOLD_EUR;

  // Keep the card element's amount in step with the chosen edition.
  useEffect(() => {
    elementsRef.current?.update({ amount: tier.priceEur * 100 });
  }, [tier.priceEur]);

  // The phone bar shows only while the in-page Pay with Card is off screen.
  useEffect(() => {
    const el = payRef.current;
    if (!el) return;
    const io = new IntersectionObserver(([e]) => setPayVisible(e.isIntersecting), { threshold: 0 });
    io.observe(el);
    return () => io.disconnect();
  }, []);

  // Mount Stripe's card field when the form opens.
  useEffect(() => {
    if (stage !== "details" || paymentRef.current || !cardRef.current) return;
    let cancelled = false;
    loadStripe(PK).then((stripe) => {
      if (cancelled || !stripe || !cardRef.current) return;
      stripeRef.current = stripe;
      const elements = stripe.elements({
        mode: "payment",
        amount: tier.priceEur * 100,
        currency: "eur",
        paymentMethodTypes: ["card"],
        fonts: [{ cssSrc: "https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600&display=swap" }],
        appearance: {
          theme: "night",
          variables: {
            fontFamily: "Archivo, system-ui, sans-serif",
            fontSizeBase: "18px",
            colorPrimary: "#f5f5f3",
            colorBackground: "#111113",
            colorText: "#f5f5f3",
            colorTextSecondary: "#9b9ea6",
            colorDanger: "#ff8f87",
            borderRadius: "4px",
            spacingUnit: "6px",
          },
          rules: {
            ".Input": { border: "1px solid #6b6e76", boxShadow: "none", padding: "18px 16px" },
            ".Input:focus": { border: "1px solid #f5f5f3", boxShadow: "0 0 0 1px #e3a467" },
            ".Label": { fontSize: "16px", color: "#c9ccd1" },
          },
        },
      });
      const payment = elements.create("payment", {
        layout: "tabs",
        wallets: { applePay: "never", googlePay: "never" },
        fields: { billingDetails: { name: "never", email: "never", address: "never", phone: "never" } },
        terms: { card: "never" },
      });
      payment.on("ready", () => setCardReady(true));
      payment.mount(cardRef.current);
      elementsRef.current = elements;
      paymentRef.current = payment;
    });
    return () => {
      cancelled = true;
    };
  }, [stage, tier.priceEur]);

  useEffect(
    () => () => {
      paymentRef.current?.destroy();
    },
    [],
  );

  const set = (k: keyof Fields) => (e: { target: { value: string } }) => {
    setFields((f) => ({ ...f, [k]: e.target.value }));
    setBadFields((b) => b.filter((x) => !x.startsWith(k === "line1" ? "address" : k === "postal_code" ? "postal" : k)));
  };

  const togglePay = (viaKeyboard: boolean) => {
    if (!tier.available || stage === "processing") return;
    if (open) {
      setStage("choose");
      return;
    }
    if (!feel) {
      setFeelMissing(true);
      feelRef.current?.scrollIntoView({ block: "center", behavior: viaKeyboard ? "instant" : "smooth" });
      feelRef.current?.querySelector<HTMLInputElement>("input")?.focus({ preventScroll: true });
      return;
    }
    attemptRef.current = crypto.randomUUID();
    setStage("details");
    requestAnimationFrame(() => {
      const first = formRef.current?.querySelector<HTMLInputElement>("input");
      if (!first) return;
      const top = first.getBoundingClientRect().top + window.scrollY - 96;
      if (viaKeyboard) {
        window.scrollTo({ top, behavior: "instant" });
        first.focus({ preventScroll: true });
      } else {
        if (window.__lenis) window.__lenis.scrollTo(top);
        else window.scrollTo({ top, behavior: "smooth" });
      }
    });
  };

  const placeReservation = async (e: FormEvent) => {
    e.preventDefault();
    if (!feel) return;
    setError(null);
    setStage("processing");
    try {
      const elements = elementsRef.current;
      const stripe = stripeRef.current;
      if (elements) {
        const { error: submitError } = await elements.submit();
        if (submitError) throw new Error(submitError.message ?? "Please check your card details.");
      }
      const res = await fetch("/api/reserve", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          tier: tier.id,
          feel,
          invite: fields.invite,
          name: fields.name,
          email: fields.email,
          address: { line1: fields.line1, line2: fields.line2, postal_code: fields.postal_code, city: fields.city, country: fields.country },
          attempt: attemptRef.current,
        }),
      });
      const data = (await res.json()) as { clientSecret?: string; error?: string; fields?: string[] };
      if (!res.ok || !data.clientSecret) {
        setBadFields(data.fields ?? []);
        throw new Error(data.error ?? "Something went wrong. Nothing was charged.");
      }
      if (!stripe || !elements) throw new Error("Card payments are not available yet. Nothing was charged.");
      const result = await stripe.confirmPayment({
        elements,
        clientSecret: data.clientSecret,
        redirect: "if_required",
        confirmParams: {
          return_url: `${window.location.origin}/reserved?tier=${tier.id}&feel=${feel}`,
          payment_method_data: {
            billing_details: {
              name: fields.name,
              email: fields.email,
              phone: "",
              address: {
                line1: fields.line1,
                line2: fields.line2 || "",
                postal_code: fields.postal_code,
                city: fields.city,
                state: "",
                country: fields.country,
              },
            },
          },
        },
      });
      if (result.error) throw new Error(result.error.message ?? "Your card was not charged. Please try again.");
      if (result.paymentIntent?.status === "succeeded" || result.paymentIntent?.status === "processing") {
        setPaid({ tier: tier.id, feel, email: fields.email });
        setStage("done");
        return;
      }
      throw new Error("Your card was not charged. Please try again.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong. Nothing was charged.");
      setStage("details");
    }
  };

  const bad = (k: string) => badFields.some((b) => b.startsWith(k));

  return (
    <div className={styles.options} data-open={open}>
      <div className={styles.columnHead}>
        <h1 className={styles.logotype}>{site.name}</h1>
        <p className={styles.ships}>{site.shipLabel}</p>
      </div>

      {stage === "done" && paid ? (
        <Confirmation tier={paid.tier} feel={paid.feel} email={paid.email} />
      ) : (
        <>
          <fieldset className={styles.tiers} disabled={open}>
            <legend className="visually-hidden">{reserveCopy.chooseLegend}</legend>
            {tiers.map((t, i) => {
              const checked = tierId === t.id;
              return (
                <div key={t.id} className={styles.tierWrap}>
                  {i === 1 ? <p className={styles.group}>{reserveCopy.editionsHeading}</p> : null}
                  <label className={styles.tier} data-checked={checked} data-tier={t.id} data-disabled={!t.available}>
                    <input
                      type="radio"
                      className="visually-hidden"
                      name={`${uid}-tier`}
                      value={t.id}
                      checked={checked}
                      disabled={!t.available}
                      onChange={() => onTier(t.id)}
                    />
                    <span className={styles.tierHead}>
                      <TierGlyph tier={t.id} selected={checked} className={styles.tierGlyph} />
                      <span className={styles.tierName}>{t.name}</span>
                      <span className={styles.tierStatus} data-tier={t.id}>
                        {t.available ? t.availability : "Sold out"}
                      </span>
                    </span>
                    <span className={styles.tierLine}>{t.cardLine}</span>
                    <span className={`t-num ${styles.tierPrice}`}>{priceLabel(t.priceEur)}</span>
                    {checked && t.priceEur > EXTRAS_THRESHOLD_EUR ? (
                      <span className={styles.extras}>
                        <span className={styles.extrasHead}>{reserveCopy.extrasHeading}</span>
                        {t.includes.map((x) => (
                          <span key={x} className={styles.extra}>
                            {x}
                          </span>
                        ))}
                      </span>
                    ) : null}
                  </label>
                </div>
              );
            })}
          </fieldset>

          <fieldset ref={feelRef} className={styles.feel} disabled={open} data-missing={feelMissing && !feel}>
            <legend className={styles.feelLegend}>{reserveCopy.feelLegend}</legend>
            <div className={styles.feelOptions}>
              {(Object.keys(feels) as FeelId[]).map((id) => (
                <label key={id} className={styles.feelOption} data-checked={feel === id}>
                  <input
                    type="radio"
                    className="visually-hidden"
                    name={`${uid}-feel`}
                    value={id}
                    checked={feel === id}
                    onChange={() => {
                      onFeel(id);
                      setFeelMissing(false);
                    }}
                  />
                  <Swatch weave={id} />
                  <span className={styles.feelText}>
                    <span className={styles.feelName}>{feels[id].name}</span>
                    <span className={styles.feelSub}>{feels[id].sub}</span>
                  </span>
                </label>
              ))}
            </div>
            <p className={styles.hint} aria-live="polite">
              {feelMissing && !feel ? reserveCopy.feelRequired : extras ? `${reserveCopy.feelHint} ${reserveCopy.feelAllThree}` : reserveCopy.feelHint}
            </p>
          </fieldset>

          <ul className={styles.trust}>
            {reserveCopy.trustLines.map((l) => (
              <li key={l}>{l}</li>
            ))}
          </ul>
          <Badges className={styles.badges} />

          <div className={styles.due}>
            <div className={styles.dueRow}>
              <span className={styles.dueLabel}>{reserveCopy.dueTodayLabel}</span>
              <span className={`t-num ${styles.dueAmount}`}>{priceLabel(tier.priceEur)}</span>
            </div>
            <p className={styles.dueRefund}>{reserveCopy.refundLine}</p>
            {tier.id === "invite" ? <p className={styles.dueNote}>{reserveCopy.inviteNote}</p> : null}
            <p className={styles.fine}>{reserveCopy.fineprint}</p>
          </div>

          <button
            ref={payRef}
            type="button"
            className={styles.pay}
            aria-expanded={open}
            aria-controls={`${uid}-form`}
            disabled={!tier.available || stage === "processing"}
            onClick={(e) => togglePay(e.detail === 0)}
          >
            <span>{site.payLabel}</span>
            <svg viewBox="0 0 24 24" aria-hidden="true" className={styles.chevron}>
              <path d="m6 9.5 6 6 6-6" />
            </svg>
          </button>

          {open ? (
            <form id={`${uid}-form`} ref={formRef} className={styles.form} onSubmit={placeReservation} noValidate>
              <h2 className="visually-hidden">{reserveCopy.formHeading}</h2>
              {tier.id === "invite" ? (
                <Field label="Invitation code" name="invite" value={fields.invite} onChange={set("invite")} autoComplete="off" invalid={bad("invite")} />
              ) : null}
              <Field label="Full name" name="name" value={fields.name} onChange={set("name")} autoComplete="name" invalid={bad("name")} />
              <Field label="Email" name="email" type="email" value={fields.email} onChange={set("email")} autoComplete="email" invalid={bad("email")} />
              <Field label="Address" name="line1" value={fields.line1} onChange={set("line1")} autoComplete="shipping address-line1" invalid={bad("address")} />
              <Field label="Apartment, suite (optional)" name="line2" value={fields.line2} onChange={set("line2")} autoComplete="shipping address-line2" required={false} />
              <div className={styles.pair}>
                <Field label="Postal code" name="postal_code" value={fields.postal_code} onChange={set("postal_code")} autoComplete="shipping postal-code" invalid={bad("postal")} />
                <Field label="City" name="city" value={fields.city} onChange={set("city")} autoComplete="shipping address-level2" invalid={bad("city")} />
              </div>
              <label className={styles.field} data-invalid={bad("country") || undefined}>
                <span>Country</span>
                <select name="country" value={fields.country} onChange={set("country")} autoComplete="shipping country" required aria-invalid={bad("country") || undefined}>
                  <option value="" disabled>
                    Select
                  </option>
                  {deliveryCountries.map(([c, n]) => (
                    <option key={c} value={c}>
                      {n}
                    </option>
                  ))}
                </select>
              </label>
              <div className={styles.card}>
                <span className={styles.cardLabel}>Card</span>
                {PK ? (
                  <div ref={cardRef} className={styles.cardElement} data-ready={cardReady} />
                ) : (
                  <p className={styles.cardPreview}>{reserveCopy.cardPreview}</p>
                )}
              </div>
              <p className={styles.error} role="alert" aria-live="assertive">
                {error}
              </p>
              <button type="submit" className={styles.place} disabled={stage === "processing" || !PK} data-busy={stage === "processing"}>
                {stage === "processing" ? reserveCopy.processing : site.placeLabel}
              </button>
            </form>
          ) : null}
        </>
      )}

      {stage === "choose" ? (
        <div className={styles.bar} data-hidden={payVisible} aria-hidden={payVisible}>
          <span className={styles.barText}>
            <span className={styles.barTier}>{tier.name}</span>
            <span className="t-num">
              {reserveCopy.dueTodayLabel} {priceLabel(tier.priceEur)}
            </span>
          </span>
          <button type="button" className={styles.barPay} tabIndex={payVisible ? -1 : 0} onClick={(e) => togglePay(e.detail === 0)}>
            {reserveCopy.stickyPay}
          </button>
        </div>
      ) : null}
    </div>
  );
}

function Confirmation({ tier, feel, email }: { tier: TierId; feel: FeelId; email: string }) {
  const t = tierById(tier)!;
  return (
    <div className={styles.done} role="status">
      <h2 className={styles.doneTitle}>{reserveCopy.confirmationHeadline}</h2>
      <p className={styles.doneTier}>
        {t.name}, {feels[feel].name}. <span className="t-num">{priceLabel(t.priceEur)}</span>
      </p>
      <p className="t-body">{reserveCopy.confirmationBody}</p>
      {email ? <p className={styles.fine}>Receipt sent to {email}.</p> : null}
    </div>
  );
}

/** A woven-carbon swatch: fine 3K twill for Command, wide 12K spread tow for Pace. */
function Swatch({ weave }: { weave: FeelId }) {
  const id = useId();
  const cell = weave === "command" ? 5 : 12;
  return (
    <svg viewBox="0 0 56 56" className={styles.swatch} aria-hidden="true">
      <defs>
        <pattern id={id} width={cell * 2} height={cell * 2} patternUnits="userSpaceOnUse" patternTransform="rotate(45 28 28)">
          <rect width={cell * 2} height={cell * 2} fill="#0d0d0f" />
          <rect width={cell} height={cell} fill="#26262b" />
          <rect x={cell} y={cell} width={cell} height={cell} fill="#26262b" />
          <path d={`M0 ${cell / 2}h${cell}M${cell} ${cell * 1.5}h${cell}`} stroke="#3a3a41" strokeWidth={cell / 5} />
        </pattern>
        <radialGradient id={`${id}-g`} cx="30%" cy="25%" r="80%">
          <stop offset="0" stopColor="#fff" stopOpacity="0.22" />
          <stop offset="0.5" stopColor="#fff" stopOpacity="0" />
        </radialGradient>
      </defs>
      <circle cx="28" cy="28" r="27" fill={`url(#${id})`} />
      <circle cx="28" cy="28" r="27" fill={`url(#${id}-g)`} />
      <circle cx="28" cy="28" r="27.5" fill="none" stroke="#6b6e76" strokeWidth="1" />
    </svg>
  );
}

function Field({
  label,
  name,
  value,
  onChange,
  type = "text",
  autoComplete,
  invalid,
  required = true,
}: {
  label: string;
  name: string;
  value: string;
  onChange: (e: { target: { value: string } }) => void;
  type?: string;
  autoComplete?: string;
  invalid?: boolean;
  required?: boolean;
}) {
  return (
    <label className={styles.field} data-invalid={invalid || undefined}>
      <span>{label}</span>
      <input name={name} type={type} value={value} onChange={onChange} autoComplete={autoComplete} required={required} aria-invalid={invalid || undefined} />
    </label>
  );
}
