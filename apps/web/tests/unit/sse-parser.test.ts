import {
	isKnownSSEEvent,
	parseSSEBlock,
	splitSSEBuffer,
} from "@/lib/sse/parser";
import { describe, expect, it } from "vitest";

describe("SSE parser", () => {
	it("parses every event type", () => {
		const kinds = [
			"routing",
			"agent_start",
			"agent_token",
			"agent_tool",
			"agent_end",
			"interrupt",
			"aggregate",
			"error",
			"done",
		];
		for (const kind of kinds) {
			const evt = parseSSEBlock(`event: ${kind}\ndata: {"a":1}`);
			expect(evt?.kind).toBe(kind);
			expect(isKnownSSEEvent(kind)).toBe(true);
		}
	});

	it("handles unknown events gracefully", () => {
		const evt = parseSSEBlock("event: future_thing\ndata: {}");
		expect(evt?.kind).toBe("future_thing");
		expect(isKnownSSEEvent("future_thing")).toBe(false);
	});

	it("splits buffered streams with remainder", () => {
		const [events, rest] = splitSSEBuffer(
			'event: routing\ndata: {"agents":["rag_agent"]}\n\nevent: agent_st',
		);
		expect(events).toHaveLength(1);
		expect(rest).toContain("agent_st");
	});

	it("returns null without event field", () => {
		expect(parseSSEBlock('data: {"a":1}')).toBeNull();
	});
});
