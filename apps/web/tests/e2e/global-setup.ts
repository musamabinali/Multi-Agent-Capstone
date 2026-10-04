/** Live-server gate: fail fast unless both servers answer; warm RAG embeddings. */
export default async function globalSetup(): Promise<void> {
	const api = process.env.PLAYWRIGHT_API_URL ?? "http://127.0.0.1:8001";
	const web = process.env.PLAYWRIGHT_BASE_URL ?? "http://localhost:3000";

	// /api/health runs a live LLM probe per call, so latency varies under
	// load (browsers starting, Turbopack compiling). Retry generously here;
	// the 30s budget in Section 5 applies to tests, not setup.
	const get = async (url: string, timeoutMs = 45_000): Promise<Response> => {
		const controller = new AbortController();
		const timer = setTimeout(() => controller.abort(), timeoutMs);
		try {
			return await fetch(url, { signal: controller.signal });
		} finally {
			clearTimeout(timer);
		}
	};

	let health: Response | null = null;
	let lastError = "";
	for (let attempt = 1; attempt <= 3; attempt++) {
		try {
			health = await get(`${api}/api/health`);
			break;
		} catch (error) {
			lastError = String(error);
			console.log(`web gate: health attempt ${attempt}/3 slow, retrying…`);
		}
	}
	if (health === null) {
		throw new Error(
			`web gate: backend unreachable at ${api} — start it first ` +
				`(PYTHONPATH=src python -m uvicorn makpa.api.server:app --port 8001). Cause: ${lastError}`,
		);
	}
	if (!health.ok)
		throw new Error(`web gate: backend health ${health.status} at ${api}`);
	const body = (await health.json()) as { mode?: string };
	console.log(`web gate: backend ${api} ok (mode=${body.mode ?? "?"})`);

	const chat = await get(`${web}/chat`).catch((error: unknown) => {
		throw new Error(
			`web gate: frontend unreachable at ${web} — start it first (pnpm dev). Cause: ${String(error)}`,
		);
	});
	if (!chat.ok)
		throw new Error(`web gate: frontend /chat ${chat.status} at ${web}`);
	console.log(`web gate: frontend ${web} ok`);

	// Warm the embedding model + retrieval path so the 30s per-test budget
	// covers the RAG flow instead of the first HF load.
	const thread = await (
		await fetch(`${api}/api/threads`, { method: "POST" })
	).json();
	const threadId = (thread as { thread_id: string }).thread_id;
	await fetch(`${api}/api/threads/${encodeURIComponent(threadId)}/invoke`, {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify({ message: "What does the sample PDF say?" }),
	});
	await fetch(`${api}/api/threads/${encodeURIComponent(threadId)}`, {
		method: "DELETE",
	});
	console.log("web gate: RAG warmup done");
}
