import { defineConfig } from "@playwright/test";

const baseURL = process.env.PLAYWRIGHT_BASE_URL ?? "http://localhost:3000";

export default defineConfig({
	testDir: "./tests/e2e",
	use: { baseURL },
	globalSetup: "./tests/e2e/global-setup.ts",
	timeout: 30_000,
	workers: process.env.CI ? 1 : undefined,
	webServer: {
		command: "pnpm dev",
		port: 3000,
		reuseExistingServer: true,
	},
});
