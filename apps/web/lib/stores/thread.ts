"use client";

import type { AgentOutput, ChatMessage, InterruptPayload } from "@/lib/types";
import { create } from "zustand";

export interface AgentView {
	status: string;
	answer: string;
	citations: AgentOutput["citations"];
	tools: AgentOutput["tools"];
	structured?: AgentOutput["structured"];
	streaming: boolean;
}

interface ThreadStore {
	threadId: string | null;
	messages: ChatMessage[];
	agents: string[];
	agentViews: Record<string, AgentView>;
	pendingInterrupt: InterruptPayload | null;
	overallStatus: string;
	reasoning: string;
	connected: boolean;
	setThread: (threadId: string) => void;
	reset: () => void;
	pushUser: (content: string) => void;
	applyRouting: (agents: string[], reasoning: string) => void;
	startAgents: (agents: string[]) => void;
	appendToken: (agent: string, delta: string) => void;
	applyTool: (agent: string, tool: string, status: string) => void;
	endAgent: (agent: string, status: string) => void;
	applyOutputs: (outputs: Record<string, AgentOutput>) => void;
	setInterrupt: (payload: InterruptPayload | null) => void;
	setAggregate: (status: string) => void;
	setConnected: (connected: boolean) => void;
}

const emptyView = (): AgentView => ({
	status: "streaming",
	answer: "",
	citations: [],
	tools: [],
	streaming: true,
});

export const useThreadStore = create<ThreadStore>()((set) => ({
	threadId: null,
	messages: [],
	agents: [],
	agentViews: {},
	pendingInterrupt: null,
	overallStatus: "",
	reasoning: "",
	connected: false,
	setThread: (threadId) =>
		set({
			threadId,
			messages: [],
			agents: [],
			agentViews: {},
			pendingInterrupt: null,
			overallStatus: "",
			reasoning: "",
		}),
	reset: () =>
		set({
			messages: [],
			agents: [],
			agentViews: {},
			pendingInterrupt: null,
			overallStatus: "",
			reasoning: "",
		}),
	pushUser: (content) =>
		set((s) => ({ messages: [...s.messages, { role: "user", content }] })),
	applyRouting: (agents, reasoning) => set({ agents, reasoning }),
	startAgents: (agents) =>
		set((s) => {
			const views: Record<string, AgentView> = { ...s.agentViews };
			for (const a of agents) views[a] = emptyView();
			return { agentViews: views };
		}),
	appendToken: (agent, delta) =>
		set((s) => {
			const prev = s.agentViews[agent] ?? emptyView();
			return {
				agentViews: {
					...s.agentViews,
					[agent]: { ...prev, answer: prev.answer + delta },
				},
			};
		}),
	applyTool: (agent, tool, status) =>
		set((s) => {
			const prev = s.agentViews[agent] ?? emptyView();
			const tools = [...(prev.tools ?? []), { tool, status }];
			return { agentViews: { ...s.agentViews, [agent]: { ...prev, tools } } };
		}),
	endAgent: (agent, status) =>
		set((s) => {
			const prev = s.agentViews[agent] ?? emptyView();
			return {
				agentViews: {
					...s.agentViews,
					[agent]: { ...prev, status, streaming: false },
				},
			};
		}),
	applyOutputs: (outputs) =>
		set((s) => {
			const views: Record<string, AgentView> = { ...s.agentViews };
			for (const [name, out] of Object.entries(outputs)) {
				views[name] = {
					status: out.status,
					answer: out.answer,
					citations: out.citations ?? [],
					tools: out.tools ?? [],
					structured: out.structured,
					streaming: false,
				};
			}
			const order = Object.keys(outputs);
			const messages: ChatMessage[] = [...s.messages];
			return {
				agentViews: views,
				agents: order.length > 0 ? order : s.agents,
				messages,
			};
		}),
	setInterrupt: (pendingInterrupt) => set({ pendingInterrupt }),
	setAggregate: (overallStatus) => set({ overallStatus }),
	setConnected: (connected) => set({ connected }),
}));
