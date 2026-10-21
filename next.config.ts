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
    // og.jpg keeps a fixed name and is left out.
    return [
      {
        source: "/stills/:file([^/]+\\.[0-9a-f]{10}\\.(?:avif|webp))",
        headers: [{ key: "Cache-Control", value: "public, max-age=31536000, immutable" }],
      },
    ];
  },
};

export default nextConfig;
