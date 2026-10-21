import { invitesOpen } from "@/content/lineup";

// Checks an InviQtus invitation code as soon as the buyer has typed it, before any card details.
// The same check runs again in /api/reserve when the reservation is placed; this one only answers yes or no.

export async function POST(request: Request) {
  let code = "";
  try {
    const body = (await request.json()) as { code?: unknown };
    code = typeof body.code === "string" ? body.code.trim().slice(0, 40).toUpperCase() : "";
  } catch {
    return Response.json({ error: "Invalid request." }, { status: 400 });
  }
  if (!invitesOpen(process.env.INVITE_CODES)) {
    return Response.json({ error: "Invitations open soon." }, { status: 403 });
  }
  const codes = (process.env.INVITE_CODES ?? "").split(",").map((c) => c.trim().toUpperCase());
  if (!code || !codes.includes(code)) {
    return Response.json({ error: "That invitation code is not valid." }, { status: 403 });
  }
  return Response.json({ ok: true });
}
