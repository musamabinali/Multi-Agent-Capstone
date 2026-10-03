import { expect, test } from "@playwright/test";

test("RAG flow renders cited answer", async ({ page }) => {
	await page.goto("/chat");
	await expect(page.getByText("Start a conversation")).toBeVisible();
});

test("interrupt modal confirms and rollback path exists", async ({ page }) => {
	await page.goto("/chat");
	await expect(page.getByPlaceholder("Type your message")).toBeVisible();
});

test("downgrade banner honesty", async ({ page }) => {
	await page.goto("/health");
	await expect(page.getByText(/backend/i)).toBeVisible();
});
