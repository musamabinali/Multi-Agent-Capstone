import { useThreadStore } from "@/lib/stores/thread";
import { beforeEach, describe, expect, it } from "vitest";

describe("useThreadStore", () => {
	beforeEach(() => {
		useThreadStore.getState().setThread("t-0001");
	});

	it("appends tokens in place without losing scroll state", () => {
		const s = useThreadStore.getState();
		s.startAgents(["rag_agent"]);
		s.appendToken("rag_agent", "hello ");
		s.appendToken("rag_agent", "world");
		expect(useThreadStore.getState().agentViews.rag_agent?.answer).toBe(
			"hello world",
		);
	});

	it("sets and resolves interrupts", () => {
		useThreadStore.getState().setInterrupt({
			agent: "google_agent",
			kind: "calendar_create",
			payload: { summary: "Sync" },
		});
		expect(useThreadStore.getState().pendingInterrupt?.kind).toBe(
			"calendar_create",
		);
		useThreadStore.getState().setInterrupt(null);
		expect(useThreadStore.getState().pendingInterrupt).toBeNull();
	});

	it("applies authoritative outputs over streamed partials", () => {
		const s = useThreadStore.getState();
		s.startAgents(["github_agent"]);
		s.appendToken("github_agent", "partial…");
		s.applyOutputs({
			github_agent: {
				agent: "github_agent",
				status: "ok",
				answer: "final",
				tools: [],
			},
		});
		expect(useThreadStore.getState().agentViews.github_agent?.answer).toBe(
			"final",
		);
	});
});
