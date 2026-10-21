import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  cacheComponents: true,
  partialPrefetching: true,
  async redirects() {
    // The old checkout URL now lives at /reserve.
    return [{ source: "/checkout", destination: "/reserve", permanent: true }];
  },
};

export default nextConfig;
