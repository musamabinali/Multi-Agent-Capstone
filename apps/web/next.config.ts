import type { NextConfig } from "next";

const BACKEND_URL = process.env.MAKPA_BACKEND_URL ?? "http://127.0.0.1:8001";

const nextConfig: NextConfig = {
	// Biome is the enforced lint gate (eslint-config-next flat patch is broken
	// under pnpm on Node 22); type errors still fail the build below.
	eslint: { ignoreDuringBuilds: true },
	async rewrites() {
		return [
			{
				source: "/api/:path*",
				destination: `${BACKEND_URL}/api/:path*`,
			},
		];
	},
};

export default nextConfig;
