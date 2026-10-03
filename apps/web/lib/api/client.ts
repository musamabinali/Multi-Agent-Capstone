import type { Health, ThreadState } from "@/lib/types";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
	const res = await fetch(path, {
		...init,
		headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
	});
	if (!res.ok) {
		const body = await res.text().catch(() => "");
		throw new Error(
			`${init?.method ?? "GET"} ${path} → ${res.status}: ${body}`,
		);
	}
	return (await res.json()) as T;
}

export function fetchHealth(): Promise<Health> {
	return request<Health>("/api/health");
}

export function createThread(): Promise<{ thread_id: string }> {
	return request<{ thread_id: string }>("/api/threads", { method: "POST" });
}

export function listThreads(): Promise<{
	threads: { thread_id: string; created_at?: string }[];
}> {
	return request<{ threads: { thread_id: string; created_at?: string }[] }>(
		"/api/threads",
	);
}

export function loadThread(threadId: string): Promise<ThreadState> {
	return request<ThreadState>(`/api/threads/${encodeURIComponent(threadId)}`);
}

export function invokeThread(
	threadId: string,
	message: string,
): Promise<ThreadState> {
	return request<ThreadState>(
		`/api/threads/${encodeURIComponent(threadId)}/invoke`,
		{
			method: "POST",
			body: JSON.stringify({ message }),
		},
	);
}

export interface ResumeBody {
	confirm?: boolean;
	rollback?: boolean;
}

export function resumeThread(
	threadId: string,
	body: ResumeBody,
): Promise<ThreadState> {
	return request<ThreadState>(
		`/api/threads/${encodeURIComponent(threadId)}/resume`,
		{
			method: "POST",
			body: JSON.stringify(body),
		},
	);
}

export function triggerIngest(path?: string): Promise<{
	path: string;
	chunks_created: number;
	chunks_skipped: number;
	backend: string;
	duration_ms: number;
}> {
	return request("/api/ingest", {
		method: "POST",
		body: JSON.stringify(path ? { path } : {}),
	});
}
