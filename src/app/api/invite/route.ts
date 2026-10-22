import { invitesOpen } from "@/content/lineup";
import { cleanCode, inviteCodes, inviteUses } from "@/lib/stripe-server";

// Checks an InviQtus invitation code: a valid one unlocks InviQtus on /reserve ("Have an invitation?" or
// ?invite=CODE). The same checks run again in /api/reserve when the reservation is placed; this one only
// answers yes or no. A wrong or used code is an answer, not a failure: 200 with ok: false (no console error).
// A code reserves one set: once Stripe holds a paid reservation with it, it no longer unlocks InviQtus.

export async function POST(request: Request) {
  let code = "";
  try {
    const body = (await request.json()) as { code?: unknown };
    code = cleanCode(body.code);
  } catch {
    return Response.json({ error: "Invalid request." }, { status: 400 });
  }
  if (!invitesOpen(process.env.INVITE_CODES)) {
    return Response.json({ ok: false, error: "Invitations open soon." });
  }
  if (!code || !inviteCodes().includes(code)) {
    return Response.json({ ok: false, error: "That invitation code is not valid." });
  }
  // Unknown (no key, or Stripe cannot count) unlocks: /api/reserve checks again and refuses if still unknown.
  const key = process.env.STRIPE_SECRET_KEY;
  if (key && ((await inviteUses(key, code)) ?? 0) > 0) {
    return Response.json({ ok: false, error: "This invitation has already been used." });
  }
  return Response.json({ ok: true });
}
