import { expect, test, type Page } from "@playwright/test";

/**
 * Live-server flows: real backend (:8001) + real frontend (:3000),
 * no mocked routes. Backend runs mock MCP servers (see global-setup).
 */

async function ask(page: Page, message: string): Promise<void> {
	await page.goto("/chat");
	await page.getByLabel("Type your message").fill(message);
	await page.getByRole("button", { name: "Send message" }).click();
	await expect(page).toHaveURL(/\/chat\/.+/, { timeout: 15_000 });
}

async function confirmModal(page: Page, name: RegExp): Promise<void> {
	const dialog = page.getByRole("alertdialog");
	await expect(dialog).toBeVisible({ timeout: 20_000 });
	await expect(dialog.getByRole("checkbox")).toBeVisible({ timeout: 20_000 });
	await dialog.getByRole("checkbox").check();
	await dialog.getByRole("button", { name }).click();
}

test("live RAG flow renders cited answer", async ({ page }) => {
	await ask(page, "What does the sample PDF say about implementation details?");
	await expect(page.getByText("RAG agent")).toBeVisible({ timeout: 20_000 });
	await expect(page.getByText("Overall status: ok")).toBeVisible({ timeout: 20_000 });
	const chip = page.getByRole("button", { name: /sample\.pdf/ }).first();
	await expect(chip).toBeVisible({ timeout: 20_000 });
	await chip.click();
	const drawer = page.getByLabel("Citation source preview");
	await expect(drawer).toBeVisible();
	await expect(drawer.getByText("sample.pdf")).toBeVisible();
	await expect(drawer.getByText("7", { exact: true })).toBeVisible();
});

test("live GitHub flow shows PR 7 in the id table", async ({ page }) => {
	await ask(page, "List open pull requests in octo-demo/hello-world.");
	await expect(page.getByText("GitHub agent")).toBeVisible({ timeout: 20_000 });
	const table = page.getByRole("table", { name: "Structured result" });
	await expect(table).toBeVisible({ timeout: 20_000 });
	await expect(table.getByText("pr_numbers")).toBeVisible();
	await expect(table.getByText("7", { exact: true })).toBeVisible();
	await expect(table.getByText("octo-demo/hello-world")).toBeVisible();
});

test("live composite flow confirms two gates and shows ids", async ({ page }) => {
	await ask(
		page,
		"Schedule a meeting with a@example.com from 2026-10-06T15:00:00Z " +
			"to 2026-10-06T16:00:00Z and email them the agenda.",
	);
	const gate1 = page.getByRole("alertdialog");
	await expect(gate1).toBeVisible({ timeout: 20_000 });
	await expect(gate1.getByText("Confirm calendar event")).toBeVisible();
	await gate1.getByRole("checkbox").check();
	await gate1.getByRole("button", { name: /confirm & create/i }).click();

	const gate2 = page.getByRole("alertdialog");
	await expect(gate2).toBeVisible({ timeout: 20_000 });
	await expect(gate2.getByText("Confirm email send")).toBeVisible({
		timeout: 20_000,
	});
	await gate2.getByRole("checkbox").check();
	await gate2.getByRole("button", { name: /confirm & send/i }).click();

	await expect(page.getByText("evt-mock-100").first()).toBeVisible({
		timeout: 20_000,
	});
	await expect(page.getByText("msg-from-draft-mock-100").first()).toBeVisible({
		timeout: 20_000,
	});
});

test("live rollback at gate 2 cancels the event", async ({ page }) => {
	await ask(
		page,
		"Schedule a meeting with b@example.com from 2026-10-07T15:00:00Z " +
			"to 2026-10-07T16:00:00Z and email them the agenda.",
	);
	await confirmModal(page, /confirm & create/i);
	const gate2 = page.getByRole("alertdialog");
	await expect(gate2).toBeVisible({ timeout: 20_000 });
	await gate2.getByRole("checkbox").check();
	await gate2.getByRole("button", { name: /rollback/i }).click();
	await expect(page.getByText(/rolled back|cancelled/i).first()).toBeVisible({
		timeout: 20_000,
	});
});
