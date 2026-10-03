import { defineConfig } from "@playwright/test";

export default defineConfig({
	testDir: "./tests/a11y",
	use: { baseURL: "http://localhost:3000" },
	webServer: {
		command: "pnpm dev",
		port: 3000,
		reuseExistingServer: true,
	},
});
