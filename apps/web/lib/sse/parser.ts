import type { SSEEvent } from "@/lib/types";

/** Parse one SSE `field: value` block. Unknown event types are kept — the caller ignores them. */
export function parseSSEBlock(block: string): SSEEvent | null {
	let event: string | null = null;
	const dataLines: string[] = [];
	for (const line of block.split("\n")) {
		if (line.startsWith("event:")) {
			event = line.slice("event:".length).trim();
		} else if (line.startsWith("data:")) {
			dataLines.push(line.slice("data:".length).trimStart());
		}
	}
	if (event === null) return null;
	const raw = dataLines.join("\n");
	let data: SSEEvent["data"] = {};
	if (raw.length > 0) {
		try {
			const parsed: unknown = JSON.parse(raw);
			if (
				parsed !== null &&
				typeof parsed === "object" &&
				!Array.isArray(parsed)
			) {
				data = parsed as SSEEvent["data"];
			}
		} catch {
			data = {};
		}
	}
	return { kind: event, data };
}

/** Split a stream buffer into complete blocks; returns [events, remainder]. */
export function splitSSEBuffer(buffer: string): [SSEEvent[], string] {
	const parts = buffer.split("\n\n");
	const remainder = parts.pop() ?? "";
	const events: SSEEvent[] = [];
	for (const part of parts) {
		const trimmed = part.trim();
		if (trimmed.length === 0) continue;
		const evt = parseSSEBlock(trimmed);
		if (evt !== null) events.push(evt);
	}
	return [events, remainder];
}

export const KNOWN_SSE_EVENTS: ReadonlySet<string> = new Set([
	"routing",
	"agent_start",
	"agent_token",
	"agent_tool",
	"agent_end",
	"interrupt",
	"aggregate",
	"error",
	"done",
]);

export function isKnownSSEEvent(kind: string): boolean {
	return KNOWN_SSE_EVENTS.has(kind);
}
