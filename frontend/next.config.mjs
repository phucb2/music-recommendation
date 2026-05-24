import nextEnv from "@next/env";
import path from "path";
import { fileURLToPath } from "url";

const { loadEnvConfig } = nextEnv;

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, "..");

loadEnvConfig(repoRoot);

/** @type {import("next").NextConfig} */
const nextConfig = {
  output: "standalone",
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "picsum.photos", pathname: "/**" },
    ],
  },
};

export default nextConfig;
