import { NextResponse, type NextRequest } from "next/server";
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
  if (cleared) return isAssetOrApi(pathname) ? NextResponse.next() : presentation(NextResponse.next());

  if (isAssetOrApi(pathname)) return gated(new NextResponse(null, { status: 403 }));
  return gated(NextResponse.rewrite(new URL(NDA_ROUTE, request.url)));
}

/**
 * /api/*, Next's own endpoints other than its static files (/_next/image and the like), and any path whose last
 * segment has a file extension (stills, og.jpg, CREDITS.md, robots.txt, favicon.ico).
 */
function isAssetOrApi(pathname: string) {
  if (pathname === "/api" || pathname.startsWith("/api/") || pathname.startsWith("/_next/")) return true;
  const last = pathname.slice(pathname.lastIndexOf("/") + 1);
  return /\.[A-Za-z0-9]+$/.test(last);
}

/** A cleared page: kept out of shared caches and revalidated before reuse (the header comment above). */
function presentation(res: NextResponse) {
  res.headers.set("Cache-Control", "private, no-cache");
  return res;
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
