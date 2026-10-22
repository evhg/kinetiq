/**
 * Emails the owner each time someone opens the presentation through the NDA gate (owner, 2026-10-22), through the
 * Resend account the owner also uses for Kicksmash. Three Vercel settings, none of them in this public repo:
 * RESEND_API_KEY, NDA_NOTIFY_TO (the owner's inbox) and NDA_NOTIFY_FROM (a sender on that account's verified domain).
 * Without all three nothing is sent, and the gate's note does not mention it (ndaNotifyConfigured). It runs after the
 * response (`after` in /api/nda), so a slow or failed email never holds up the gate; a failure is logged without the
 * visitor's address. It says only the address, the time and the page (its path and edition, no other parameter).
 */
export type NdaSignIn = {
  email: string;
  at: string;
  page: string;
  origin: string;
};

const TIMEOUT_MS = 8000;
const DAY_MS = 86_400_000;
const HOUR_MS = 3_600_000;
const MAX_PER_HOUR = 20;

/**
 * The addresses emailed in the last day, oldest first, in this server instance's memory. At most 20 an hour, so it
 * holds at most 480; a new instance starts empty.
 */
const sent = new Map<string, number>();

/**
 * Whether this sign-in may email the owner: once per address a day, and at most 20 an hour, so a script posting to
 * the gate cannot flood the inbox or spend the Resend account's quota. The cookie is set either way.
 */
export function mayNotify(email: string, now = Date.now()): boolean {
  for (const [address, at] of sent) {
    if (at > now - DAY_MS) break;
    sent.delete(address);
  }
  const key = email.toLowerCase();
  if (sent.has(key)) return false;
  let lastHour = 0;
  for (const at of sent.values()) if (at > now - HOUR_MS) lastHour++;
  if (lastHour >= MAX_PER_HOUR) return false;
  sent.set(key, now);
  return true;
}

export function ndaNotifyConfigured(): boolean {
  return Boolean(process.env.RESEND_API_KEY?.trim() && process.env.NDA_NOTIFY_TO?.trim() && process.env.NDA_NOTIFY_FROM?.trim());
}

export async function notifyNdaSignIn(s: NdaSignIn): Promise<void> {
  if (!ndaNotifyConfigured()) return;
  const text = [
    `${s.email} declared the NDA and opened the presentation.`,
    "",
    `When: ${s.at}`,
    `Page: ${s.origin}${s.page}`,
  ].join("\n");
  try {
    const res = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: { Authorization: `Bearer ${process.env.RESEND_API_KEY!.trim()}`, "Content-Type": "application/json" },
      body: JSON.stringify({
        from: process.env.NDA_NOTIFY_FROM!.trim(),
        to: [process.env.NDA_NOTIFY_TO!.trim()],
        reply_to: s.email,
        subject: `KINETIQ presentation opened by ${s.email}`,
        text,
      }),
      signal: AbortSignal.timeout(TIMEOUT_MS),
    });
    if (!res.ok) console.warn(`[nda] sign-in email was not sent (${res.status})`);
  } catch {
    console.warn("[nda] sign-in email was not sent");
  }
}
