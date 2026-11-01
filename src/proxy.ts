import { NextResponse, type NextRequest } from "next/server";
import { FEEL_COOKIE_MAX_AGE, FEEL_PREFERENCE_KEY, isFeelId, type FeelId } from "@/content/site";
import { NDA_COOKIE, NDA_ROUTE, ndaCleared } from "@/lib/nda";

/**
 * The NDA gate (owner, 2026-10-22). Nothing confidential is served before a visitor has declared the NDA:
 * - page requests without a valid kq_nda cookie are rewritten to the gate (/nda), so the address bar keeps the
 *   URL as typed (/, /reserve?tier=limited) and the page opens there once the gate sets the cookie;
 * - asset and API requests without it (/stills/*, /CREDITS.md, /api/*, any file) get an empty 403;
 * - the gate's own POST /api/nda always passes, and /nda with a valid cookie redirects to /.
 * With a valid cookie everything else passes. Pages then get `Cache-Control: private, no-cache`: no shared cache (a
 * company proxy, a CDN in front of a self-hosted build) may store the presentation, and the browser revalidates before
 * reuse; not no-store, so the back button's page cache keeps working. Assets and APIs keep their own headers (stills:
 * next.config.ts). Redirects only ever go to /, never to a URL from the request.
 * A cleared request for /, /reserve or /reserved that carries the `kq-feel` cookie (the visitor's feel, lib/feel-store.ts)
 * is rewritten to the same page prerendered in that feel (app/feel/<feel>/), so a returning Pace visitor's hero is Pace
 * in the HTML and Command is never fetched; the URL stays as typed. No cache may reuse a page without asking (private,
 * no-cache below), so a changed choice always gets the page in the new feel. (A Vary: Cookie set here would be replaced
 * by Next's own Vary on rendered pages.)
 * /feel/* asked for directly is a 404: those pages exist only behind this rewrite.
 * Every cleared page response to a request carrying `kq-feel` sends it back with a fresh year (refreshFeel below): Safari's
 * Intelligent Tracking Prevention caps a cookie written by script (document.cookie) at 7 days, and one set by the
 * server's Set-Cookie at its own Max-Age, so a Pace visitor keeps the Pace page however rarely they choose.
 */
export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;
  if (pathname === "/api/nda" && request.method === "POST") return NextResponse.next();
  // The dev server's overlay endpoints (/__nextjs_original-stack-frames and the like) must load on the gate itself.
  // They do not exist in production, where these paths are gated like any other.
  if (process.env.NODE_ENV === "development" && pathname.startsWith("/__nextjs_")) return NextResponse.next();

  const cleared = ndaCleared(request.cookies.get(NDA_COOKIE)?.value);
  if (pathname === NDA_ROUTE) {
    return cleared ? NextResponse.redirect(new URL("/", request.url)) : gated(NextResponse.next());
  }
  if (cleared) {
    if (isAssetOrApi(pathname)) return NextResponse.next();
    const value = request.cookies.get(FEEL_PREFERENCE_KEY)?.value;
    const feel = isFeelId(value) ? value : null;
    if (pathname === FEEL_ROOT || pathname.startsWith(`${FEEL_ROOT}/`)) {
      return presentation(NextResponse.rewrite(new URL(FEEL_ROOT, request.url)), request, feel);
    }
    if (feel && FEEL_PAGES.has(pathname)) {
      const url = request.nextUrl.clone();
      url.pathname = `${FEEL_ROOT}/${feel}${pathname === "/" ? "" : pathname}`;
      return presentation(NextResponse.rewrite(url), request, feel);
    }
    return presentation(NextResponse.next(), request, feel);
  }

  if (isAssetOrApi(pathname)) return gated(new NextResponse(null, { status: 403 }));
  return gated(NextResponse.rewrite(new URL(NDA_ROUTE, request.url)));
}

/** The pages with a variant per feel (app/feel/<feel>/), and where those live (no page of its own: a 404). */
const FEEL_ROOT = "/feel";
const FEEL_PAGES = new Set(["/", "/reserve", "/reserved"]);

/**
 * /api/*, Next's own endpoints other than its static files (/_next/image and the like), and any path whose last
 * segment has a file extension (stills, og.jpg, CREDITS.md, robots.txt, favicon.ico).
 */
function isAssetOrApi(pathname: string) {
  if (pathname === "/api" || pathname.startsWith("/api/") || pathname.startsWith("/_next/")) return true;
  const last = pathname.slice(pathname.lastIndexOf("/") + 1);
  return /\.[A-Za-z0-9]+$/.test(last);
}

/**
 * A cleared page: kept out of shared caches and revalidated before reuse, and the visitor's feel cookie renewed (the
 * header comment above).
 */
function presentation(res: NextResponse, request: NextRequest, feel: FeelId | null) {
  res.headers.set("Cache-Control", "private, no-cache");
  if (feel) refreshFeel(res, request, feel);
  return res;
}

/**
 * Sends `kq-feel` back as the request carried it, with the attributes lib/feel-store.ts and the head script write
 * (Path=/, one year, SameSite=Lax, Secure on https, not HttpOnly so they can still change it): a server-set cookie is
 * not held to ITP's 7-day cap on script-written ones, so the cap restarts at one year on every visit.
 */
function refreshFeel(res: NextResponse, request: NextRequest, feel: FeelId) {
  res.cookies.set({
    name: FEEL_PREFERENCE_KEY,
    value: feel,
    path: "/",
    maxAge: FEEL_COOKIE_MAX_AGE,
    sameSite: "lax",
    secure: request.nextUrl.protocol === "https:" || request.headers.get("x-forwarded-proto") === "https",
  });
}

/** Gate responses depend on the cookie: never cached, never indexed. */
function gated(res: NextResponse) {
  res.headers.set("Cache-Control", "private, no-store");
  res.headers.set("Vary", "Cookie");
  res.headers.set("X-Robots-Tag", "noindex, nofollow");
  return res;
}

export const config = {
  matcher: [
    /*
     * Every path except what the gate itself needs to load, each anchored so nothing else can borrow the exemption:
     * Next's static files (JS, CSS, fonts; known limit: a chunk's URL, once known, is readable without the cookie,
     * CLAUDE.md "NDA gate"), the dev server's HMR socket, and the two icon files (src/app/icon.svg, apple-icon.png).
     * Everything else, pages, /stills/*, /CREDITS.md, /credits, /lab/*, /api/*, /_next/image and any unknown path,
     * goes through the proxy.
     */
    "/((?!_next/static/|_next/webpack-hmr$|icon\\.svg$|apple-icon\\.png$).*)",
  ],
};
