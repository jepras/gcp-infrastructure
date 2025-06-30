import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  env: {
    NEXT_PUBLIC_BACKEND_URL: process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8080",
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*', // Match requests to /api/*
        destination: `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/:path*`, // Proxy to backend
      },
    ];
  },
  /* config options here */
};

export default nextConfig;
