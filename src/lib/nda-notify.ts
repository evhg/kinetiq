/**
 * Emails the owner each time someone opens the presentation through the NDA gate (owner, 2026-10-22).
 * The recipient is NDA_NOTIFY_TO, a Vercel setting that never goes in this public repo. With RESEND_API_KEY set the
 * email goes through Resend (from NDA_NOTIFY_FROM, or Resend's onboarding sender); otherwise through FormSubmit, which
 * needs no account: the first sign-in sends the recipient one activation email, and every sign-in after that arrives.
 * It runs after the response (`after` in /api/nda), so a slow or failed email never holds up or blocks the gate,
 * and a failure is logged without the visitor's address.
 */
export type NdaSignIn = {
  email: string;
  at: string;
  page: string;
  origin: string;
  country?: string;
  browser?: string;
};

const TIMEOUT_MS = 8000;

export async function notifyNdaSignIn(s: NdaSignIn): Promise<void> {
  const to = process.env.NDA_NOTIFY_TO?.trim();
  if (!to) return;
  const subject = `KINETIQ presentation opened by ${s.email}`;
  const lines = [
    `${s.email} declared the NDA and opened the presentation.`,
    "",
    `When: ${s.at}`,
    `Page: ${s.page}`,
    s.country ? `Country: ${s.country}` : "",
    s.browser ? `Browser: ${s.browser}` : "",
  ].filter(Boolean);
  const signal = AbortSignal.timeout(TIMEOUT_MS);
  try {
    const key = process.env.RESEND_API_KEY?.trim();
    const res = key
      ? await fetch("https://api.resend.com/emails", {
          method: "POST",
          headers: { Authorization: `Bearer ${key}`, "Content-Type": "application/json" },
          body: JSON.stringify({
            from: process.env.NDA_NOTIFY_FROM?.trim() || "KINETIQ <onboarding@resend.dev>",
            to: [to],
            reply_to: s.email,
            subject,
            text: lines.join("\n"),
          }),
          signal,
        })
      : await fetch(`https://formsubmit.co/ajax/${encodeURIComponent(to)}`, {
          method: "POST",
          // FormSubmit only accepts posts that come from a website.
          headers: { "Content-Type": "application/json", Accept: "application/json", Origin: s.origin, Referer: `${s.origin}/` },
          body: JSON.stringify({
            _subject: subject,
            _template: "table",
            _captcha: "false",
            email: s.email,
            when: s.at,
            page: s.page,
            country: s.country ?? "",
            browser: s.browser ?? "",
          }),
          signal,
        });
    if (!res.ok) console.warn(`[nda] sign-in email was not sent (${res.status})`);
  } catch {
    console.warn("[nda] sign-in email was not sent");
  }
}
