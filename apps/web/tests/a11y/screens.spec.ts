import AxeBuilder from "@axe-core/playwright";
import { type Page, expect, test } from "@playwright/test";

const HEALTH = {
	mode: "free",
	requested_mode: "free",
	llm_provider: "groq",
	vector_store: "chroma_local",
	embedding_provider: "huggingface",
	github_path: "mock",
	google_path: "mock",
	oauth_state: "missing",
	downgrades: ["GitHub PAT missing; using mock GitHub MCP server"],
	probe: { provider: "groq", model: "qwen", ok: true, warnings: [] },
	time: "2026-10-03T00:00:00+00:00",
};

const THREAD_RAG = {
	thread_id: "makpa-web-0001",
	agents: ["rag_agent"],
	agent_outputs: {
		rag_agent: {
			agent: "rag_agent",
			status: "ok",
			answer: "The document covers implementation details.",
			citations: [{ source: "sample.pdf", page: 7, chunk_id: 36 }],
			tools: [],
			structured: {
				citations: [{ source: "sample.pdf", page: 7, chunk_id: 36 }],
				chunk_count: 1,
			},
		},
	},
	status: "ok",
	messages: [{ role: "user", content: "Summarize the sample PDF" }],
	pending_interrupt: null,
	paused: false,
};

const THREAD_GATE1 = {
	...THREAD_RAG,
	thread_id: "makpa-web-0002",
	status: "confirmation_required",
	pending_interrupt: {
		agent: "google_agent",
		kind: "1",
		payload: {
			gate: 1,
			payload_preview: [
				{ tool: "calendar_create_event", args: { summary: "Sync" } },
			],
			question: "Schedule a meeting",
		},
	},
	paused: true,
};

async function mockShell(page: Page) {
	await page.route("**/api/health", (route) => route.fulfill({ json: HEALTH }));
	await page.route("**/api/threads", (route) =>
		route.fulfill({ json: { threads: [] } }),
	);
}

async function assertNoCriticalOrSerious(page: Page) {
	const results = await new AxeBuilder({ page })
		.withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"])
		.analyze();
	const blocking = results.violations.filter(
		(v) => v.impact === "critical" || v.impact === "serious",
	);
	expect(
		blocking.map((v) => `${v.id}: ${v.description}`),
		"axe critical/serious violations",
	).toEqual([]);
}

test("axe: empty chat", async ({ page }) => {
	await mockShell(page);
	await page.goto("/chat");
	await expect(page.getByText("Start a conversation")).toBeVisible();
	await assertNoCriticalOrSerious(page);
});

test("axe: thread with RAG answer", async ({ page }) => {
	await mockShell(page);
	await page.route("**/api/threads/makpa-web-0001", (route) =>
		route.fulfill({ json: THREAD_RAG }),
	);
	await page.goto("/chat/makpa-web-0001");
	await expect(page.getByText("RAG agent")).toBeVisible();
	await assertNoCriticalOrSerious(page);
});

test("axe: confirmation modal open", async ({ page }) => {
	await mockShell(page);
	await page.route("**/api/threads/makpa-web-0002", (route) =>
		route.fulfill({ json: THREAD_GATE1 }),
	);
	await page.goto("/chat/makpa-web-0002");
	await expect(page.getByRole("alertdialog")).toBeVisible();
	await assertNoCriticalOrSerious(page);
});

test("axe: settings", async ({ page }) => {
	await mockShell(page);
	await page.goto("/settings");
	await expect(page.getByText("Backend status")).toBeVisible();
	await assertNoCriticalOrSerious(page);
});
