"use client";

import { isKnownSSEEvent, splitSSEBuffer } from "@/lib/sse/parser";
import { useThreadStore } from "@/lib/stores/thread";
import type { AgentOutput, Citation, StructuredResult } from "@/lib/types";
import { useCallback, useRef } from "react";

interface StreamCallbacks {
	onInterrupt?: () => void;
	onDone?: () => void;
}

function asString(value: unknown): string {
	return typeof value === "string" ? value : "";
}

function asStringArray(value: unknown): string[] {
	return Array.isArray(value)
		? value.filter((v): v is string => typeof v === "string")
		: [];
}

function asStructured(value: unknown): StructuredResult | undefined {
	if (value === null || typeof value !== "object" || Array.isArray(value))
		return undefined;
	return value as StructuredResult;
}

function asCitations(value: unknown): Citation[] | undefined {
	if (!Array.isArray(value)) return undefined;
	const out: Citation[] = [];
	for (const item of value) {
		if (
			item !== null &&
			typeof item === "object" &&
			"source" in item &&
			"page" in item
		) {
			const rec = item as Record<string, unknown>;
			const source = rec.source;
			const page = rec.page;
			if (typeof source === "string" && typeof page === "number")
				out.push(item as Citation);
		}
	}
	return out;
}

/** Dedicated SSE lifecycle hook — never useEffect-for-streaming elsewhere. */
export function useChatStream() {
	const abortRef = useRef<AbortController | null>(null);

	const stop = useCallback(() => {
		abortRef.current?.abort();
		abortRef.current = null;
		useThreadStore.getState().setConnected(false);
	}, []);

	const send = useCallback(
		async (threadId: string, message: string, cb?: StreamCallbacks) => {
			stop();
			const store = useThreadStore.getState();
			store.pushUser(message);
			store.setAggregate("");
			store.setInterrupt(null);

			const controller = new AbortController();
			abortRef.current = controller;
			store.setConnected(true);

			let reconnects = 0;
			const url = `/api/threads/${encodeURIComponent(threadId)}/stream`;

			while (reconnects <= 3) {
				try {
					const res = await fetch(url, {
						method: "POST",
						headers: { "Content-Type": "application/json" },
						body: JSON.stringify({ message }),
						signal: controller.signal,
					});
					if (!res.ok || res.body === null)
						throw new Error(`stream ${res.status}`);
					const reader = res.body.getReader();
					const decoder = new TextDecoder();
					let buffer = "";
					for (;;) {
						const { done, value } = await reader.read();
						if (done) break;
						buffer += decoder.decode(value, { stream: true });
						const [events, remainder] = splitSSEBuffer(buffer);
						buffer = remainder;
						const live = useThreadStore.getState();
						for (const evt of events) {
							if (!isKnownSSEEvent(evt.kind)) continue; // log-and-ignore unknown
							switch (evt.kind) {
								case "routing": {
									const agents = asStringArray(evt.data.agents);
									live.applyRouting(agents, asString(evt.data.reasoning));
									live.startAgents(agents);
									break;
								}
								case "agent_start": {
									const agent = asString(evt.data.agent);
									if (agent) live.startAgents([agent]);
									break;
								}
								case "agent_token": {
									const agent = asString(evt.data.agent);
									const delta = asString(evt.data.delta);
									if (agent) live.appendToken(agent, delta);
									break;
								}
								case "agent_tool": {
									const agent = asString(evt.data.agent);
									const tool = asString(evt.data.tool);
									const status = asString(evt.data.status) || "ok";
									if (agent && tool) live.applyTool(agent, tool, status);
									break;
								}
								case "agent_end": {
									const agent = asString(evt.data.agent);
									const status = asString(evt.data.status) || "ok";
									if (agent) {
										const citations = asCitations(evt.data.citations);
										const structured = asStructured(evt.data.structured);
										if (citations !== undefined || structured !== undefined) {
											const outputs: Record<string, AgentOutput> = {
												[agent]: {
													agent,
													status,
													answer:
														useThreadStore.getState().agentViews[agent]
															?.answer ?? "",
													citations,
													structured,
												},
											};
											live.applyOutputs(outputs);
										}
										live.endAgent(agent, status);
									}
									break;
								}
								case "interrupt": {
									const agent = asString(evt.data.agent) || "google_agent";
									const kind = asString(evt.data.kind) || "confirm";
									const payload =
										evt.data.payload !== null &&
										typeof evt.data.payload === "object" &&
										!Array.isArray(evt.data.payload)
											? (evt.data.payload as Record<string, unknown>)
											: (evt.data as Record<string, unknown>);
									live.setInterrupt({ agent, kind, payload });
									live.setAggregate("confirmation_required");
									cb?.onInterrupt?.();
									break;
								}
								case "aggregate": {
									live.setAggregate(asString(evt.data.status) || "ok");
									break;
								}
								case "error": {
									live.setAggregate("error");
									break;
								}
								case "done": {
									break;
								}
							}
						}
					}
					// Reconcile with authoritative non-streaming state (citations/ids preserved).
					try {
						const full = await (
							await fetch(`/api/threads/${encodeURIComponent(threadId)}`)
						).json();
						const outputs = (
							full as { agent_outputs?: Record<string, AgentOutput> }
						).agent_outputs;
						if (outputs !== undefined)
							useThreadStore.getState().applyOutputs(outputs);
						const pending = (
							full as {
								pending_interrupt?: null | {
									agent: string;
									kind: string;
									payload: Record<string, unknown>;
								};
							}
						).pending_interrupt;
						useThreadStore.getState().setInterrupt(pending ?? null);
						const status = (full as { status?: string }).status;
						if (typeof status === "string" && status)
							useThreadStore.getState().setAggregate(status);
					} catch {
						// Keep streamed partials; reconnect chip stays honest via `connected`.
					}
					cb?.onDone?.();
					return;
				} catch (err) {
					if (controller.signal.aborted) return;
					reconnects += 1;
					if (reconnects > 3) {
						useThreadStore.getState().setAggregate("error");
						return;
					}
					await new Promise((r) => setTimeout(r, 500 * reconnects));
				}
			}
		},
		[stop],
	);

	return { send, stop };
}
