import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactCompiler: true,
  // Expose the Python backend URL to server-side API routes.
  // Override with BACKEND_URL env var in production.
  env: {
    BACKEND_URL: process.env.BACKEND_URL ?? "http://localhost:8000",
  },
};

export default nextConfig;
