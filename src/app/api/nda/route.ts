import { NextResponse, after, type NextRequest } from "next/server";
import { tierById } from "@/content/lineup";
import { NDA_COOKIE, NDA_MAX_AGE, encodeNda, isEmail, normaliseEmail } from "@/lib/nda";
import { mayNotify, ndaNotifyConfigured, notifyNdaSignIn } from "@/lib/nda-notify";

// The NDA gate's one endpoint (src/proxy.ts lets it through without the cookie). It checks the email, sets the
// kq_nda cookie (src/lib/nda.ts) and, after the response, emails the owner (src/lib/nda-notify.ts): for a same-origin
// request only, once per address a day and at most 20 an hour. No database and no log line with the address. A
// malformed address is an answer, not a failure: 200 with ok: false (no console error), as in /api/invite. Malformed
// or cross-site requests get 400 / 403.

const MAX_BODY = 2048;

export async function POST(request: NextRequest) {
  if (request.headers.get("sec-fetch-site") === "cross-site") {
    return new NextResponse(null, { status: 403 });
  }
  if (!request.headers.get("content-type")?.toLowerCase().startsWith("application/json")) {
    return Response.json({ ok: false, reason: "request" }, { status: 400 });
  }
  let email = "";
  try {
    const raw = await request.text();
    if (raw.length > MAX_BODY) throw new Error("too large");
    const body = JSON.parse(raw) as { email?: unknown };
    email = normaliseEmail(body?.email);
  } catch {
    return Response.json({ ok: false, reason: "request" }, { status: 400 });
  }
  if (!isEmail(email)) return Response.json({ ok: false, reason: "email" }, { headers: { "Cache-Control": "no-store" } });

  const forwarded = request.headers.get("x-forwarded-proto")?.split(",")[0]?.trim();
  const res = NextResponse.json({ ok: true }, { headers: { "Cache-Control": "no-store" } });
  res.cookies.set({
    name: NDA_COOKIE,
    value: encodeNda(email),
    httpOnly: true,
    sameSite: "lax",
    secure: request.nextUrl.protocol === "https:" || forwarded === "https",
    path: "/",
    maxAge: NDA_MAX_AGE,
  });
  const origin = request.nextUrl.origin;
  // The gate's own form, from this site (browsers without Sec-Fetch-Site send Origin). A script can forge both:
  // mayNotify is what bounds the emails. With emails off, no address is held even in memory.
  const site = request.headers.get("sec-fetch-site");
  const sameOrigin = site ? site === "same-origin" : request.headers.get("origin") === origin;
  if (!sameOrigin || !ndaNotifyConfigured() || !mayNotify(email)) return res;
  // The page's path and its edition only: never an invitation code, a payment's client secret or any other parameter.
  let page = "/";
  try {
    const ref = new URL(request.headers.get("referer") ?? "", origin);
    if (ref.origin === origin) {
      const tier = tierById(ref.searchParams.get("tier"));
      page = `${ref.pathname.slice(0, 100)}${tier ? `?tier=${tier.id}` : ""}`;
    }
  } catch {}
  const signIn = { email, at: new Date().toISOString(), page, origin };
  after(() => notifyNdaSignIn(signIn));
  return res;
}
