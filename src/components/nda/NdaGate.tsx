"use client";

import { useEffect, useRef, useState, type ChangeEvent, type FormEvent, type MouseEvent } from "react";
import chrome from "@/components/chrome/Chrome.module.css";
import { useMotion } from "@/components/motion/MotionProvider";
import { ndaCopy as copy } from "@/content/nda";
import { NDA_ARRIVE_MS, NDA_TRIED_KEY, isEmail, normaliseEmail } from "@/lib/nda";
import styles from "./NdaGate.module.css";

type Step = "ask" | "email" | "notYet";

/** How long the gate takes to leave (the veil's fade in NdaGate.module.css) before the page reloads at its URL. */
const LEAVE_MS = 260;

/**
 * The NDA gate: step 1 asks for the declaration, Yes opens the email step in place, Not yet explains what to do.
 * The steps share one grid cell and cross-fade (exit 150 ms, enter 240 ms after it), so nothing moves; a step
 * opened from the keyboard appears at once. On success the cookie is set by POST /api/nda, a void veil fades in
 * under the wordmark and the page reloads at the same URL, where src/proxy.ts now lets the real page through.
 */
/** `recorded`: sign-in emails to the owner are switched on, so the note says the email is recorded. */
export function NdaGate({ recorded = false }: { recorded?: boolean }) {
  const { motionOn } = useMotion();
  const [step, setStep] = useState<Step>("ask");
  const [instant, setInstant] = useState(false);
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [leaving, setLeaving] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const notYetRef = useRef<HTMLParagraphElement>(null);
  const yesRef = useRef<HTMLButtonElement>(null);
  const noRef = useRef<HTMLButtonElement>(null);
  const moved = useRef(false);
  // The step a Back came from: focus returns to the answer that opened it (Yes for the email step, Not yet for its own).
  const [cameFrom, setCameFrom] = useState<Step>("ask");

  // The cookie did not stick (the gate is back right after a successful submit): say so on the email step.
  useEffect(() => {
    let tried = 0;
    try {
      tried = Number(sessionStorage.getItem(NDA_TRIED_KEY)) || 0;
      sessionStorage.removeItem(NDA_TRIED_KEY);
    } catch {}
    if (tried && Date.now() - tried < NDA_ARRIVE_MS) {
      /* eslint-disable react-hooks/set-state-in-effect -- one-time client read after a failed reload */
      setInstant(true);
      setStep("email");
      setError(copy.email.blocked);
      /* eslint-enable react-hooks/set-state-in-effect */
    }
  }, []);

  // Focus follows a step the visitor opened: the email field, the Not yet message, or back to the answer that
  // opened the step they left (Yes from the email step, Not yet from its message).
  useEffect(() => {
    if (!moved.current) return;
    moved.current = false;
    const back = cameFrom === "email" ? yesRef.current : noRef.current;
    const target = step === "email" ? inputRef.current : step === "notYet" ? notYetRef.current : back;
    target?.focus({ preventScroll: true });
  }, [step, cameFrom]);

  const goTo = (next: Step, from: Step = "ask") => (e: MouseEvent<HTMLButtonElement>) => {
    // Enter or Space on a button arrives as a click with detail 0: keyboard moves jump, pointer moves fade.
    setInstant(e.detail === 0);
    setError("");
    moved.current = true;
    setCameFrom(from);
    setStep(next);
  };

  const onChange = (e: ChangeEvent<HTMLInputElement>) => {
    setEmail(e.target.value);
    if (error) setError("");
  };

  const submit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (busy || leaving) return;
    const value = normaliseEmail(email);
    if (!isEmail(value)) {
      setError(copy.email.invalid);
      inputRef.current?.focus();
      return;
    }
    setError("");
    setBusy(true);
    try {
      const res = await fetch("/api/nda", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ email: value }),
        credentials: "same-origin",
        cache: "no-store",
      });
      const data = (await res.json().catch(() => null)) as { ok?: boolean; reason?: string } | null;
      if (!res.ok || !data?.ok) {
        setBusy(false);
        setError(data?.reason === "email" ? copy.email.invalid : copy.email.failed);
        inputRef.current?.focus();
        return;
      }
    } catch {
      setBusy(false);
      setError(copy.email.failed);
      return;
    }
    try {
      sessionStorage.setItem(NDA_TRIED_KEY, String(Date.now()));
    } catch {}
    setLeaving(true);
    window.setTimeout(() => window.location.reload(), motionOn ? LEAVE_MS : 0);
  };

  const describedBy = error ? "nda-email-error nda-email-lead nda-email-note" : "nda-email-lead nda-email-note";

  return (
    <div className={styles.gate} data-nda-gate="" data-leaving={leaving || undefined}>
      <header className={chrome.header}>
        <div className={chrome.row}>
          <span className={chrome.wordmark}>KINETIQ</span>
        </div>
      </header>

      <main id="main" className={styles.stage}>
        <div className={styles.panel}>
          <p className={`t-eyebrow ${styles.eyebrow}`}>{copy.eyebrow}</p>
          <h1 className={`t-h1 ${styles.title}`}>{copy.title}</h1>

          <div className={styles.steps} data-instant={instant || undefined}>
            <div className={styles.step} data-active={step === "ask"} inert={step !== "ask"}>
              <p className={`t-lead ${styles.lead}`}>{copy.ask.lead}</p>
              <div className={styles.choices}>
                <button ref={yesRef} type="button" className="btn btn-primary" data-nda="yes" onClick={goTo("email")}>
                  {copy.ask.yes}
                </button>
                <button ref={noRef} type="button" className="btn btn-secondary" data-nda="no" onClick={goTo("notYet")}>
                  {copy.ask.no}
                </button>
              </div>
            </div>

            <div className={styles.step} data-active={step === "email"} inert={step !== "email"}>
              <p id="nda-email-lead" className={`t-lead ${styles.lead}`}>
                {copy.email.lead}
              </p>
              <form className={styles.form} onSubmit={submit} noValidate>
                <div className={styles.field} data-invalid={error ? true : undefined}>
                  <label htmlFor="nda-email" className={styles.label}>
                    {copy.email.label}
                  </label>
                  <div className={styles.row}>
                    <input
                      ref={inputRef}
                      id="nda-email"
                      name="email"
                      type="email"
                      inputMode="email"
                      autoComplete="email"
                      autoCapitalize="none"
                      autoCorrect="off"
                      spellCheck={false}
                      required
                      maxLength={254}
                      value={email}
                      onChange={onChange}
                      aria-invalid={error ? true : undefined}
                      aria-describedby={describedBy}
                      className={styles.input}
                    />
                    <button type="submit" className={`btn btn-primary ${styles.open}`} data-nda="open" aria-busy={busy || leaving} data-busy={busy || leaving || undefined}>
                      {copy.email.submit}
                    </button>
                  </div>
                </div>
                <div className={styles.foot}>
                  {/* The error takes the note's place while it shows, so the step never changes height. */}
                  <div className={styles.messages} data-error={error ? true : undefined}>
                    <p id="nda-email-note" className={styles.note}>
                      {recorded ? copy.email.noteRecorded : copy.email.note}
                    </p>
                    <p id="nda-email-error" className={styles.error} role="alert">
                      {error}
                    </p>
                  </div>
                  {/* A quiet way back to the question, for a visitor who pressed Yes by mistake. */}
                  <button type="button" className={styles.back} data-nda="email-back" onClick={goTo("ask", "email")}>
                    {copy.email.back}
                  </button>
                </div>
              </form>
            </div>

            <div className={styles.step} data-active={step === "notYet"} inert={step !== "notYet"}>
              <p ref={notYetRef} tabIndex={-1} className={`t-lead ${styles.lead}`} data-nda="message">
                {copy.notYet.lead}
              </p>
              <div className={styles.choices} data-single="">
                <button type="button" className="btn btn-secondary" data-nda="back" onClick={goTo("ask", "notYet")}>
                  {copy.notYet.back}
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>

      <div className={`lightline ${styles.horizon}`} aria-hidden="true" />
      <div className={styles.veil} aria-hidden="true" />
    </div>
  );
}
