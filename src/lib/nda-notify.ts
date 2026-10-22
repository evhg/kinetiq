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
const MAX_PER_DAY = 40;
/** Held-back sign-ins listed by address in the next email; beyond this many they are only counted. */
const MAX_HELD = 100;

/**
 * The addresses emailed in the last day, oldest first, in this server instance's memory. At most 40 a day, so it
 * holds at most 40; a new instance starts empty.
 */
const sent = new Map<string, number>();

/**
 * Sign-ins the caps held back, by address with the time, oldest first: the next email that is sent lists them, so a
 * flood never silently drops a real investor's sign-in (the gate tells them their email is noted). Beyond MAX_HELD
 * only their number is kept (`heldOver`). In this instance's memory only, like `sent`.
 */
const held = new Map<string, string>();
let heldOver = 0;

/**
 * Whether this sign-in may email the owner: once per address a day, at most 20 an hour and 40 a day per server
 * instance, so a script posting to the gate cannot flood the inbox or spend the Resend account's quota (across
 * instances, only a rate-limit rule on POST /api/nda in Vercel's firewall bounds it: .env.example). A sign-in over the
 * caps is held for the next email. The cookie is set either way.
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
  if (sent.size >= MAX_PER_DAY || lastHour >= MAX_PER_HOUR) {
    if (held.has(key)) return false;
    if (held.size < MAX_HELD) held.set(key, new Date(now).toISOString());
    else heldOver++;
    return false;
  }
  held.delete(key);
  sent.set(key, now);
  return true;
}

/** Takes the held-back sign-ins for the email about to be sent (synchronously, so no two emails list the same one). */
function takeHeld(): { list: [string, string][]; over: number } {
  const taken = { list: [...held], over: heldOver };
  held.clear();
  heldOver = 0;
  return taken;
}

/** Puts them back when that email fails (with its own sign-in first), ahead of any held since, within MAX_HELD. */
function restoreHeld({ list, over }: { list: [string, string][]; over: number }) {
  const since = [...held];
  held.clear();
  for (const [address, at] of [...list, ...since]) {
    if (held.has(address)) continue;
    if (held.size < MAX_HELD) held.set(address, at);
    else heldOver++;
  }
  heldOver += over;
}

export function ndaNotifyConfigured(): boolean {
  return Boolean(process.env.RESEND_API_KEY?.trim() && process.env.NDA_NOTIFY_TO?.trim() && process.env.NDA_NOTIFY_FROM?.trim());
}

export async function notifyNdaSignIn(s: NdaSignIn): Promise<void> {
  if (!ndaNotifyConfigured()) return;
  const earlier = takeHeld();
  const n = earlier.list.length + earlier.over;
  const text = [
    `${s.email} declared the NDA and opened the presentation.`,
    "",
    `When: ${s.at}`,
    `Page: ${s.origin}${s.page}`,
    ...(n
      ? [
          "",
          `${n} more ${n === 1 ? "sign-in was" : "sign-ins were"} not emailed at the time, because the limit of ` +
            `${MAX_PER_HOUR} emails an hour and ${MAX_PER_DAY} a day was reached or an email failed` +
            (earlier.list.length ? ":" : "."),
          ...earlier.list.map(([address, at]) => `${address}, ${at}`),
          ...(earlier.list.length && earlier.over
            ? [`${earlier.over} more ${earlier.over === 1 ? "is" : "are"} counted but not listed.`]
            : []),
        ]
      : []),
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
    if (!res.ok) {
      restoreHeld({ list: [[s.email.toLowerCase(), s.at], ...earlier.list], over: earlier.over });
      console.warn(`[nda] sign-in email was not sent (${res.status})`);
    }
  } catch {
    restoreHeld({ list: [[s.email.toLowerCase(), s.at], ...earlier.list], over: earlier.over });
    console.warn("[nda] sign-in email was not sent");
  }
}
