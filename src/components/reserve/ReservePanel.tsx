"use client";

import { useEffect, useId, useRef, useState, type FormEvent } from "react";
import { Badges } from "@/components/graphics/Badges";
import { Icon, TierGlyph, type IconName } from "@/components/graphics/Icons";
import { useMotion } from "@/components/motion/MotionProvider";
import { Hyphens } from "@/components/text/Hyphens";
import { deliveryCountries, includeIcons, includesFine, orderLine, priceLabel, tiers, tierById, type TierId } from "@/content/lineup";
import { reserveCopy } from "@/content/reserve";
import { feels, site, type FeelId } from "@/content/site";
import { isPaid, loadStripe, type Stripe, type StripeElement, type StripeElements } from "@/lib/stripe-client";
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
};

// Icons for the trust lines, in the order of their strings.
const TRUST_ICONS: IconName[] = ["refundArrow", "deliveryBox", "measurementCard"];

const EMPTY: Fields = { name: "", email: "", line1: "", line2: "", postal_code: "", city: "", country: "" };
const PK = process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY;
const F = reserveCopy.fields;
const E = reserveCopy.errors;
const INV = reserveCopy.invite;
// The card field runs in Stripe's iframe: system fonts, so no buyer's browser is sent to a font host.
const CARD_FONT = 'system-ui, -apple-system, "Segoe UI", Roboto, sans-serif';

/** An error whose message is written for the buyer. */
class Shown extends Error {}

/** Asks the server whether an invitation code is valid: true, or the message to show. */
async function checkInvite(code: string): Promise<true | string> {
  try {
    const res = await fetch("/api/invite", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ code }),
    });
    const data = (await res.json().catch(() => ({}))) as { ok?: boolean; error?: string };
    if (res.ok && data.ok === true) return true;
    return data.error ?? INV.invalid;
  } catch {
    return INV.offline;
  }
}

/** A random attempt id. crypto.randomUUID needs a secure context, which a phone on http://<lan-ip> is not. */
function attemptId() {
  if (typeof crypto.randomUUID === "function") return crypto.randomUUID();
  return Array.from(crypto.getRandomValues(new Uint8Array(16)), (b) => b.toString(16).padStart(2, "0")).join("");
}

/**
 * The scroll position that puts `el` `gutter` px below the fixed header. Pages kept by Next's Activity stay
 * in the DOM with display: none (their header measures 0), and graphics use <header> too.
 */
function topBelowHeader(el: HTMLElement, gutter = 24) {
  const chrome = Array.from(document.querySelectorAll("header"))
    .filter((h) => getComputedStyle(h).position === "fixed")
    .map((h) => h.getBoundingClientRect().bottom);
  return el.getBoundingClientRect().top + window.scrollY - Math.max(0, ...chrome) - gutter;
}

/**
 * Where a preselected edition's card lands: a clean gutter below the header, small enough that the card above it
 * (14 px higher) ends inside the column's top fade (Reserve.module.css .topFade), so no sliver of it shows.
 */
const PRESELECT_GUTTER = 20;

function scrollToY(top: number, smooth: boolean) {
  const lenis = window.__lenis;
  if (lenis) {
    // Lenis re-measures the page on a debounce; the form has only just made it taller.
    lenis.resize();
    lenis.scrollTo(top, { immediate: !smooth });
  } else {
    window.scrollTo({ top, behavior: smooth ? "smooth" : "instant" });
  }
}

type Props = {
  tierId: TierId;
  onTier: (id: TierId) => void;
  feel: FeelId | null;
  onFeel: (id: FeelId) => void;
  /** Invitation codes exist (decided on the server). One of Ten still needs a valid one from the buyer. */
  invitesOpen: boolean;
  /** ?invite= from the link: a code to check on load, "" to open the code field, null without it. */
  initialInvite?: string | null;
  /** The edition came from the link (?tier=): bring its card into view on wide screens. */
  preselected?: boolean;
};

/**
 * The options column: edition, feel, Due Today and Pay with Card. Pay with Card opens the delivery
 * and card form in place, ending in one Place Reservation button that charges the card right here.
 */
export function ReservePanel({ tierId, onTier, feel, onFeel, invitesOpen, initialInvite = null, preselected = false }: Props) {
  const { motionOn } = useMotion();
  const [stage, setStage] = useState<Stage>("choose");
  const [fields, setFields] = useState<Fields>(EMPTY);
  const [error, setError] = useState<string | null>(null);
  const [badFields, setBadFields] = useState<string[]>([]);
  const [feelMissing, setFeelMissing] = useState(false);
  const [cardReady, setCardReady] = useState(false);
  const [soldOut, setSoldOut] = useState<TierId[]>([]);
  const [instantForm, setInstantForm] = useState(false);
  const [paid, setPaid] = useState<{ tier: TierId; feel: FeelId; email: string; secret: string } | null>(null);
  const [payVisible, setPayVisible] = useState(true);
  // One of Ten: locked for everyone until a valid invitation code unlocks (and selects) it.
  const [inviteCode, setInviteCode] = useState<string | null>(null);
  const [inviteFieldOpen, setInviteFieldOpen] = useState(invitesOpen && initialInvite === "");
  const [inviteDraft, setInviteDraft] = useState(initialInvite ?? "");
  const [inviteBusy, setInviteBusy] = useState(invitesOpen && Boolean(initialInvite));
  const [inviteError, setInviteError] = useState<string | null>(null);
  const [inviteInstant, setInviteInstant] = useState(false);
  const [revealInvite, setRevealInvite] = useState(0);
  const inviteWrapRef = useRef<HTMLDivElement>(null);
  const inviteInputRef = useRef<HTMLInputElement>(null);
  const inviteRadioRef = useRef<HTMLInputElement>(null);
  // Set when a typed code is accepted: focus moves on to the One of Ten option once it is a real radio.
  const focusInviteRef = useRef(false);
  const formRef = useRef<HTMLFormElement>(null);
  const tiersRef = useRef<HTMLFieldSetElement>(null);
  const payRef = useRef<HTMLButtonElement>(null);
  const feelRef = useRef<HTMLFieldSetElement>(null);
  const cardRef = useRef<HTMLDivElement>(null);
  const stripeRef = useRef<Stripe | null>(null);
  const elementsRef = useRef<StripeElements | null>(null);
  const paymentRef = useRef<StripeElement | null>(null);
  const attemptRef = useRef<string>("");
  // The last PaymentIntent this page started, with what it was for.
  const secretRef = useRef<{ secret: string; tier: TierId; feel: FeelId; email: string } | null>(null);
  const uid = useId();
  const tier = tierById(tierId)!;
  // On sale and not sold out. One of Ten also needs an accepted invitation code before it can be chosen.
  const isSelectable = (id: TierId) => tierById(id)!.available && !soldOut.includes(id);
  const isLocked = (id: TierId) => id === "invite" && (!invitesOpen || !inviteCode);
  const isAvailable = (id: TierId) => isSelectable(id) && !isLocked(id);
  const available = isAvailable(tier.id);
  const open = stage !== "choose";
  const formOpen = stage === "details" || stage === "processing";

  // Load Stripe.js with the page, so its fraud signals cover the whole visit (no element yet).
  useEffect(() => {
    void loadStripe(PK);
  }, []);

  // A buyer who clicked an edition on the landing page sees that edition's card, not the first one.
  useEffect(() => {
    if (!preselected || !window.matchMedia("(min-width: 1024px)").matches) return;
    const card = tiersRef.current?.querySelector<HTMLElement>('[data-checked="true"]');
    if (card && card.getBoundingClientRect().bottom > window.innerHeight - 120) scrollToY(topBelowHeader(card, PRESELECT_GUTTER), false);
  }, [preselected]);

  // Brings the code field and its message into view (centred, clear of the phone's Pay with Card bar), or
  // the invitation card while the field is closed, and focuses the field.
  const revealInviteField = () => {
    const wrap = inviteWrapRef.current;
    const form = inviteInputRef.current?.closest("form");
    if (form) {
      const r = form.getBoundingClientRect();
      scrollToY(Math.max(0, r.top + window.scrollY - (window.innerHeight - r.height) / 2), false);
    } else if (wrap) scrollToY(topBelowHeader(wrap), false);
    inviteInputRef.current?.focus({ preventScroll: true });
  };

  // A link with ?invite: a bare one brings the code field into view; one with a code checks it, and a
  // valid code unlocks and selects One of Ten, while a wrong one brings the field and its message into view.
  // Closed invitations show the card's "open soon" note. A checked code leaves the address bar (and so
  // the history), as the page's own state now holds it.
  useEffect(() => {
    if (initialInvite === null) return;
    const code = initialInvite;
    if (!code || !invitesOpen) {
      revealInviteField();
      return;
    }
    let cancelled = false;
    void checkInvite(code).then((ok) => {
      if (cancelled) return;
      setInviteBusy(false);
      const url = new URL(window.location.href);
      url.searchParams.delete("invite");
      window.history.replaceState(window.history.state, "", url);
      if (ok === true) {
        setInviteCode(code);
        onTier("invite");
      } else {
        setInviteError(ok);
        setInviteFieldOpen(true);
        setRevealInvite((n) => n + 1);
      }
    });
    return () => {
      cancelled = true;
    };
    // Once, for the link the page was opened with (the page keys this panel by it).
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // A wrong code from the link: reveal the field and its message once the render that shows them is in.
  useEffect(() => {
    if (revealInvite) revealInviteField();
  }, [revealInvite]);

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

  // Stripe's card field lives exactly as long as the open form: closing the form, finishing, unmounting
  // or Next's Activity hiding the page destroys it, and the next open (or show) mounts a fresh one.
  useEffect(() => {
    if (!PK || !formOpen || !cardRef.current) return;
    let cancelled = false;
    let payment: StripeElement | null = null;
    loadStripe(PK).then((stripe) => {
      if (cancelled || !cardRef.current) return;
      if (!stripe) {
        setError(E.cardUnavailable);
        return;
      }
      stripeRef.current = stripe;
      let elements: StripeElements;
      try {
        elements = stripe.elements({
          mode: "payment",
          amount: tier.priceEur * 100,
          currency: "eur",
          allowedPaymentMethodTypes: ["card"],
          appearance: {
            theme: "night",
            variables: {
              fontFamily: CARD_FONT,
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
        payment = elements.create("payment", {
          layout: "tabs",
          wallets: { applePay: "never", googlePay: "never" },
          // Name and email come from our form; the billing address only where the card needs one
          // (the delivery address is not the cardholder's billing address).
          fields: { billingDetails: { name: "never", email: "never", phone: "never", address: "if_required" } },
          terms: { card: "never" },
        });
      } catch {
        // Stripe.js throws integration errors synchronously (a rejected option, a bad key).
        setError(E.cardUnavailable);
        return;
      }
      payment.on("ready", () => {
        if (!cancelled) setCardReady(true);
      });
      payment.on("loaderror", () => {
        if (!cancelled) setError(E.cardUnavailable);
      });
      payment.mount(cardRef.current);
      elementsRef.current = elements;
      paymentRef.current = payment;
    });
    return () => {
      cancelled = true;
      payment?.destroy();
      paymentRef.current = null;
      elementsRef.current = null;
      setCardReady(false);
    };
  }, [formOpen, tier.priceEur]);

  const set = (k: keyof Fields) => (e: { target: { value: string } }) => {
    setFields((f) => ({ ...f, [k]: e.target.value }));
    setBadFields((b) => b.filter((x) => !x.startsWith(k === "line1" ? "address" : k === "postal_code" ? "postal" : k)));
  };

  // Closing unmounts the card field's container; the effect above destroys the element with it.
  const closeForm = () => {
    setError(null);
    setStage("choose");
  };

  const togglePay = (viaKeyboard: boolean, fromBar = false) => {
    if (stage === "processing") return;
    if (open) {
      closeForm();
      return;
    }
    if (!available) return;
    const smooth = motionOn && !viaKeyboard;
    if (!feel) {
      setFeelMissing(true);
      feelRef.current?.scrollIntoView({ block: "center", behavior: smooth ? "smooth" : "instant" });
      feelRef.current?.querySelector<HTMLInputElement>("input")?.focus({ preventScroll: true });
      return;
    }
    attemptRef.current = attemptId();
    setInstantForm(viaKeyboard);
    setStage("details");
    requestAnimationFrame(() => {
      const form = formRef.current;
      const first = form?.querySelector<HTMLInputElement>("input");
      if (!form || !first) return;
      scrollToY(topBelowHeader(form), smooth);
      // The bar unmounts as the form opens, so focus moves on with it whatever the input.
      if (viaKeyboard || fromBar) first.focus({ preventScroll: true });
    });
  };

  const placeReservation = async (e: FormEvent) => {
    e.preventDefault();
    if (!PK || !feel || !available || stage === "processing") return;
    const stripe = stripeRef.current;
    const elements = elementsRef.current;
    if (!stripe || !elements) {
      setError(E.cardUnavailable);
      return;
    }
    // Confirms the reservation the last PaymentIntent was for (it may predate an edit to the form).
    const paidEarlier = async () => {
      const last = secretRef.current;
      if (!last || !(await isPaid(stripe, last.secret))) return false;
      setPaid({ tier: last.tier, feel: last.feel, email: last.email, secret: last.secret });
      setStage("done");
      return true;
    };
    setError(null);
    setStage("processing");
    try {
      // An earlier attempt may have been charged even though this page never heard back.
      if (await paidEarlier()) return;
      const { error: submitError } = await elements.submit();
      if (submitError) throw new Shown(submitError.message ?? E.checkCard);
      const res = await fetch("/api/reserve", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          tier: tier.id,
          feel,
          invite: inviteCode ?? "",
          name: fields.name,
          email: fields.email,
          address: { line1: fields.line1, line2: fields.line2, postal_code: fields.postal_code, city: fields.city, country: fields.country },
          attempt: attemptRef.current,
        }),
      });
      let data: { clientSecret?: string; error?: string; fields?: string[]; soldOut?: boolean } = {};
      try {
        data = await res.json();
      } catch {
        data = {};
      }
      if (data.soldOut) setSoldOut((s) => (s.includes(tier.id) ? s : [...s, tier.id]));
      if (!res.ok || !data.clientSecret) {
        setBadFields(data.fields ?? []);
        throw new Shown(data.error ?? E.generic);
      }
      secretRef.current = { secret: data.clientSecret, tier: tier.id, feel, email: fields.email };
      const result = await stripe.confirmPayment({
        elements,
        clientSecret: data.clientSecret,
        redirect: "if_required",
        confirmParams: {
          return_url: `${window.location.origin}/reserved?tier=${tier.id}&feel=${feel}`,
          payment_method_data: { billing_details: { name: fields.name, email: fields.email, phone: "" } },
        },
      });
      const status = result.paymentIntent?.status;
      if (status === "succeeded" || status === "processing") {
        setPaid({ tier: tier.id, feel, email: fields.email, secret: data.clientSecret });
        setStage("done");
        return;
      }
      throw new Shown(result.error?.message ?? E.notCharged);
    } catch (err) {
      // A lost reply is not a failed charge: ask Stripe before saying nothing was charged.
      if (await paidEarlier()) return;
      setError(err instanceof Shown ? err.message : E.generic);
      setStage("details");
    }
  };

  const bad = (k: string) => badFields.some((b) => b.startsWith(k));

  // "Have an invitation?": opens the code field in place (keyboard opens jump; pointer opens rise 8 px).
  const toggleInviteField = (viaKeyboard: boolean) => {
    const next = !inviteFieldOpen;
    setInviteFieldOpen(next);
    setInviteInstant(viaKeyboard);
    setInviteError(null);
    if (next) requestAnimationFrame(() => inviteInputRef.current?.focus({ preventScroll: true }));
  };

  const submitInvite = async (e: FormEvent) => {
    e.preventDefault();
    const code = inviteDraft.trim();
    if (inviteBusy) return;
    if (!code) {
      setInviteError(INV.invalid);
      inviteInputRef.current?.focus();
      return;
    }
    setInviteBusy(true);
    setInviteError(null);
    const ok = await checkInvite(code);
    setInviteBusy(false);
    if (ok !== true) {
      setInviteError(ok);
      inviteInputRef.current?.focus();
      return;
    }
    focusInviteRef.current = true;
    setInviteCode(code);
    setInviteFieldOpen(false);
    onTier("invite");
  };

  // The One of Ten option is a real radio once unlocked: focus continues from it.
  useEffect(() => {
    if (!inviteCode || !focusInviteRef.current) return;
    focusInviteRef.current = false;
    inviteRadioRef.current?.focus({ preventScroll: true });
  }, [inviteCode]);

  return (
    <div className={styles.options} data-open={open}>
      {/* wide screens: the column's text fades out under the header instead of being sliced by it */}
      <div className={styles.topFade} aria-hidden="true" />
      <div className={styles.columnHead}>
        <h1 className={styles.columnTitle}>{reserveCopy.columnTitle}</h1>
        <p className={styles.ships}>{site.shipLabel}</p>
      </div>

      {stage === "done" && paid ? (
        <Confirmation tier={paid.tier} feel={paid.feel} email={paid.email} paymentId={paid.secret.split("_secret_")[0]} />
      ) : (
        <>
          <fieldset ref={tiersRef} className={styles.tiers} disabled={open}>
            <legend className="visually-hidden">{reserveCopy.chooseLegend}</legend>
            {tiers.map((t) => {
              const checked = tierId === t.id;
              const can = isSelectable(t.id);
              // One of Ten reads "Invite Only" whatever the state of the invitations (the note below the
              // includes says when they open); an accepted code makes it "Invited".
              const status = !can ? reserveCopy.soldOut : t.id === "invite" && inviteCode ? INV.acceptedStatus : t.availability;
              const extras = (
                <span className={styles.extras} data-quiet={!checked || undefined}>
                  <span className={styles.extrasHead}>{reserveCopy.included}</span>
                  {t.includes.map((x, n) => (
                    <span key={x} className={styles.extra}>
                      <Icon name={includeIcons[t.id][n] ?? "shieldCheck"} size={20} className={styles.extraIcon} />
                      <span>
                        <Hyphens text={x} />
                      </span>
                    </span>
                  ))}
                  <span className={styles.extrasFine}>{includesFine(t.id)}</span>
                </span>
              );
              const head = (
                <>
                  <span className={styles.tierHead}>
                    <TierGlyph tier={t.id} selected={checked} className={styles.tierGlyph} />
                    <span className={styles.tierName} id={`${uid}-${t.id}-name`}>
                      {t.name}
                    </span>
                    <span className={styles.tierStatus} data-tier={t.id} id={`${uid}-${t.id}-status`}>
                      {status}
                    </span>
                  </span>
                  <span className={styles.tierLine}>{t.cardLine}</span>
                  <span className={`t-num ${styles.tierPrice}`}>{priceLabel(t.priceEur)}</span>
                </>
              );

              // One of Ten without an accepted invitation: shown whole (price and what it includes), but
              // not an option. No hover, press or selected state; its radio stays disabled.
              if (isLocked(t.id)) {
                return (
                  <div key={t.id} ref={inviteWrapRef} className={styles.tierWrap}>
                    <div className={styles.tier} data-tier={t.id} data-locked="true" aria-disabled="true">
                      <input
                        type="radio"
                        className="visually-hidden"
                        name={`${uid}-tier`}
                        value={t.id}
                        disabled
                        aria-labelledby={`${uid}-${t.id}-name`}
                        aria-describedby={`${uid}-${t.id}-status`}
                      />
                      {head}
                      {extras}
                      {!invitesOpen ? <span className={styles.lockedNote}>{reserveCopy.invitesClosedNote}</span> : null}
                    </div>
                    {invitesOpen ? (
                      <div className={styles.invite}>
                        <button
                          type="button"
                          className={styles.inviteAsk}
                          aria-expanded={inviteFieldOpen}
                          aria-controls={inviteFieldOpen ? `${uid}-invite` : undefined}
                          onClick={(e) => toggleInviteField(e.detail === 0)}
                        >
                          {INV.ask}
                        </button>
                        {inviteFieldOpen || inviteBusy ? (
                          <form
                            id={`${uid}-invite`}
                            className={styles.inviteForm}
                            data-instant={inviteInstant || undefined}
                            onSubmit={submitInvite}
                            noValidate
                          >
                            <label htmlFor={`${uid}-invite-code`} className={styles.inviteLabel}>
                              {INV.label}
                            </label>
                            <div className={styles.inviteRow} data-invalid={inviteError ? true : undefined}>
                              <input
                                ref={inviteInputRef}
                                id={`${uid}-invite-code`}
                                name="invite"
                                value={inviteDraft}
                                onChange={(e) => {
                                  setInviteDraft(e.target.value);
                                  setInviteError(null);
                                }}
                                autoComplete="off"
                                autoCapitalize="characters"
                                spellCheck={false}
                                maxLength={40}
                                aria-invalid={inviteError ? true : undefined}
                                aria-describedby={`${uid}-invite-msg`}
                              />
                              <button type="submit" className={styles.inviteUnlock} disabled={inviteBusy} data-busy={inviteBusy}>
                                {inviteBusy ? INV.checking : INV.unlock}
                              </button>
                            </div>
                            <p id={`${uid}-invite-msg`} className={styles.inviteError} role="alert">
                              {inviteError}
                            </p>
                          </form>
                        ) : null}
                      </div>
                    ) : null}
                  </div>
                );
              }

              return (
                <div key={t.id} className={styles.tierWrap}>
                  <label className={styles.tier} data-checked={checked} data-tier={t.id} data-disabled={!can}>
                    <input
                      ref={t.id === "invite" ? inviteRadioRef : undefined}
                      type="radio"
                      className="visually-hidden"
                      name={`${uid}-tier`}
                      value={t.id}
                      checked={checked}
                      disabled={!can}
                      onChange={() => onTier(t.id)}
                    />
                    {head}
                    {/* One of Ten keeps its includes in view; the others show theirs when chosen */}
                    {checked || t.id === "invite" ? extras : null}
                  </label>
                  {t.id === "invite" && inviteCode ? (
                    <p className="visually-hidden" aria-live="polite">
                      {INV.accepted}
                    </p>
                  ) : null}
                </div>
              );
            })}
          </fieldset>

          <fieldset ref={feelRef} className={styles.feel} disabled={open} data-missing={feelMissing && !feel}>
            <legend className={styles.feelLegend}>{reserveCopy.feelLegend(tier.rackets)}</legend>
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
                    <span className={styles.feelTitle}>
                      <span className={styles.feelName}>{feels[id].name}</span>
                      <span className={styles.feelSub}>{feels[id].sub}</span>
                    </span>
                    <span className={styles.feelSpec}>{feels[id].spec}</span>
                    <span className={styles.feelLine}>{reserveCopy.feelLines[id]}</span>
                  </span>
                </label>
              ))}
            </div>
            <p className={styles.feelHelper}>{reserveCopy.feelHelper}</p>
            <p className={styles.hint} aria-live="polite">
              {feelMissing && !feel ? reserveCopy.feelRequired : reserveCopy.feelHint(tier.rackets)}
            </p>
          </fieldset>

          <ul className={styles.trust}>
            {reserveCopy.trustLines.map((l, n) => (
              <li key={l}>
                <Icon name={TRUST_ICONS[n] ?? "shieldCheck"} className={styles.trustIcon} />
                {l}
              </li>
            ))}
          </ul>
          <Badges className={styles.badges} reveal="none" align="start" />

          <div className={styles.due}>
            <div className={styles.dueRow}>
              <span className={styles.dueLabel}>{reserveCopy.dueTodayLabel}</span>
              <span className={`t-num ${styles.dueAmount}`}>{priceLabel(tier.priceEur)}</span>
            </div>
            <p className={styles.fine}>{PK ? reserveCopy.fineprint : reserveCopy.previewLine}</p>
          </div>

          <button
            ref={payRef}
            type="button"
            className={styles.pay}
            aria-expanded={open}
            aria-controls={open ? `${uid}-form` : undefined}
            disabled={(!available && !open) || stage === "processing"}
            onClick={(e) => togglePay(e.detail === 0)}
          >
            <span>{site.payLabel}</span>
            <svg viewBox="0 0 24 24" aria-hidden="true" className={styles.chevron}>
              <path d="m6 9.5 6 6 6-6" />
            </svg>
          </button>

          {open ? (
            <form
              id={`${uid}-form`}
              ref={formRef}
              className={styles.form}
              data-instant={instantForm || undefined}
              onSubmit={placeReservation}
              noValidate
            >
              <h2 className="visually-hidden">{reserveCopy.formHeading}</h2>
              <Field label={F.name} name="name" value={fields.name} onChange={set("name")} autoComplete="name" invalid={bad("name")} />
              <Field label={F.email} name="email" type="email" value={fields.email} onChange={set("email")} autoComplete="email" invalid={bad("email")} />
              <Field label={F.line1} name="line1" value={fields.line1} onChange={set("line1")} autoComplete="shipping address-line1" invalid={bad("address")} />
              <Field label={F.line2} name="line2" value={fields.line2} onChange={set("line2")} autoComplete="shipping address-line2" required={false} />
              <div className={styles.pair}>
                <Field label={F.postalCode} name="postal_code" value={fields.postal_code} onChange={set("postal_code")} autoComplete="shipping postal-code" invalid={bad("postal")} />
                <Field label={F.city} name="city" value={fields.city} onChange={set("city")} autoComplete="shipping address-level2" invalid={bad("city")} />
              </div>
              <label className={styles.field} data-invalid={bad("country") || undefined}>
                <span>{F.country}</span>
                <select name="country" value={fields.country} onChange={set("country")} autoComplete="shipping country" required aria-invalid={bad("country") || undefined}>
                  <option value="" disabled>
                    {F.countryPlaceholder}
                  </option>
                  {deliveryCountries.map(([c, n]) => (
                    <option key={c} value={c}>
                      {n}
                    </option>
                  ))}
                </select>
              </label>
              <div className={styles.card}>
                <span className={styles.cardLabel}>{F.card}</span>
                {PK ? (
                  <div ref={cardRef} className={styles.cardElement} data-ready={cardReady} />
                ) : (
                  <p className={styles.cardPreview}>{reserveCopy.cardPreview}</p>
                )}
              </div>
              <p className={styles.error} role="alert" aria-live="assertive">
                {error}
              </p>
              <p id={`${uid}-due`} className={styles.placeDue}>
                {reserveCopy.placeDue(orderLine(tier, feel ? feels[feel].name : ""), priceLabel(tier.priceEur))}
              </p>
              <button
                type="submit"
                className={styles.place}
                disabled={stage === "processing" || !PK || !cardReady || !available}
                data-busy={stage === "processing"}
                aria-describedby={`${uid}-due`}
              >
                {stage === "processing" ? reserveCopy.processing : site.placeLabel}
              </button>
            </form>
          ) : null}
        </>
      )}

      {stage === "choose" ? (
        <div className={styles.bar} data-hidden={payVisible} inert={payVisible} data-reserve-bar="">
          <span className={styles.barText}>
            <span className={styles.barTier}>{reserveCopy.barCount(tier.rackets)}</span>
            <span className="t-num">
              {reserveCopy.dueTodayLabel} {priceLabel(tier.priceEur)}
            </span>
          </span>
          <button type="button" className={styles.barPay} disabled={!available} onClick={(e) => togglePay(e.detail === 0, true)}>
            {reserveCopy.stickyPay}
          </button>
        </div>
      ) : null}
    </div>
  );
}

/** The confirmation, in place of the options. Focus moves to its heading so it is announced. */
function Confirmation({ tier, feel, email, paymentId }: { tier: TierId; feel: FeelId; email: string; paymentId: string }) {
  const t = tierById(tier)!;
  const box = useRef<HTMLDivElement>(null);
  const heading = useRef<HTMLHeadingElement>(null);

  useEffect(() => {
    heading.current?.focus({ preventScroll: true });
    if (box.current) scrollToY(topBelowHeader(box.current), false);
  }, []);

  return (
    <div ref={box} className={styles.done}>
      <h2 ref={heading} tabIndex={-1} className={styles.doneTitle}>
        {reserveCopy.confirmationHeadline(t.rackets)}
      </h2>
      <p className={styles.doneTier}>
        {orderLine(t, feels[feel].name)}. <span className="t-num">{priceLabel(t.priceEur)}</span>
      </p>
      <p className="t-body">{reserveCopy.confirmationBody(t.id)}</p>
      <p className={`t-num ${styles.doneRef}`}>{reserveCopy.reference(paymentId)}</p>
      {email ? <p className={styles.fine}>{reserveCopy.receiptSent(email)}</p> : null}
    </div>
  );
}

/** A woven-carbon swatch: fine white 3K twill for Command, wide black 12K spread tow for Pace (owner, 2026-10-22). */
const SWATCH: Record<FeelId, { ground: string; tow: string; line: string; edge: string }> = {
  command: { ground: "#b9b6b1", tow: "#e4e1dc", line: "#f3f1ed", edge: "#c9ccd1" },
  pace: { ground: "#0d0d0f", tow: "#26262b", line: "#3a3a41", edge: "#6b6e76" },
};

function Swatch({ weave }: { weave: FeelId }) {
  const id = useId();
  const cell = weave === "command" ? 5 : 12;
  const c = SWATCH[weave];
  return (
    <svg viewBox="0 0 56 56" className={styles.swatch} aria-hidden="true">
      <defs>
        <pattern id={id} width={cell * 2} height={cell * 2} patternUnits="userSpaceOnUse" patternTransform="rotate(45 28 28)">
          <rect width={cell * 2} height={cell * 2} fill={c.ground} />
          <rect width={cell} height={cell} fill={c.tow} />
          <rect x={cell} y={cell} width={cell} height={cell} fill={c.tow} />
          <path d={`M0 ${cell / 2}h${cell}M${cell} ${cell * 1.5}h${cell}`} stroke={c.line} strokeWidth={cell / 5} />
        </pattern>
        <radialGradient id={`${id}-g`} cx="30%" cy="25%" r="80%">
          <stop offset="0" stopColor="#fff" stopOpacity="0.22" />
          <stop offset="0.5" stopColor="#fff" stopOpacity="0" />
        </radialGradient>
      </defs>
      <circle cx="28" cy="28" r="27" fill={`url(#${id})`} />
      <circle cx="28" cy="28" r="27" fill={`url(#${id}-g)`} />
      <circle cx="28" cy="28" r="27.5" fill="none" stroke={c.edge} strokeWidth="1" />
    </svg>
  );
}

function Field({
  label,
  name,
  value,
  onChange,
  onBlur,
  type = "text",
  autoComplete,
  invalid,
  required = true,
}: {
  label: string;
  name: string;
  value: string;
  onChange: (e: { target: { value: string } }) => void;
  onBlur?: () => void;
  type?: string;
  autoComplete?: string;
  invalid?: boolean;
  required?: boolean;
}) {
  return (
    <label className={styles.field} data-invalid={invalid || undefined}>
      <span>{label}</span>
      <input
        name={name}
        type={type}
        value={value}
        onChange={onChange}
        onBlur={onBlur}
        autoComplete={autoComplete}
        required={required}
        aria-invalid={invalid || undefined}
      />
    </label>
  );
}
