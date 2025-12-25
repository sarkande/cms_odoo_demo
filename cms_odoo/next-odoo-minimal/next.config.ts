import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  reactStrictMode: true,
  output: 'export', // active le build statique 
  images: {
    unoptimized: true,
  },
};

export default nextConfig;
