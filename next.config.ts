import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  cacheComponents: true,
  partialPrefetching: true,
  async redirects() {
    // The old checkout URL now lives at /reserve.
    return [{ source: "/checkout", destination: "/reserve", permanent: true }];
  },
  async headers() {
    // Exported stills carry a content hash in their names (scripts/stills.mjs), so they never change in place.
    // og.jpg keeps a fixed name and is left out. Only for requests with the NDA cookie (src/proxy.ts): without it a
    // still is an empty 403, which must never be cached as immutable. "private" keeps them in the cleared visitor's
    // own browser cache only: a shared cache (a corporate proxy, a CDN added later) must never store a still and
    // hand it to a visitor without the cookie, and Vary: Cookie says the answer depends on it.
    return [
      {
        source: "/stills/:file([^/]+\\.[0-9a-f]{10}\\.(?:avif|webp))",
        has: [{ type: "cookie", key: "kq_nda" }],
        headers: [
          { key: "Cache-Control", value: "private, max-age=31536000, immutable" },
          { key: "Vary", value: "Cookie" },
        ],
      },
    ];
  },
};

export default nextConfig;
