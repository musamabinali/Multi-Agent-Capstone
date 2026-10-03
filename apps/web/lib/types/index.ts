/** Shared frontend types — mirrors the FastAPI adapter contract (§9). No `any`. */

export type AgentName = "rag_agent" | "github_agent" | "google_agent";

export type AgentStatus =
	| "streaming"
	| "ok"
	| "partial"
	| "empty"
	| "error"
	| "cancelled"
	| "confirmation_required"
	| "rolled_back";

export type OverallStatus =
	| "ok"
	| "partial"
	| "error"
	| "cancelled"
	| "confirmation_required"
	| "empty";

export interface Citation {
	source: string;
	page: number;
	chunk_id?: number | string;
	doc_id?: string;
	score?: number;
}

export interface ToolCall {
	tool: string;
	status: string;
}

/** Typed ids threaded from tool_results — never parsed from prose. */
export interface StructuredResult {
	citations?: Citation[];
	chunk_count?: number;
	pr_numbers?: number[];
	issue_numbers?: number[];
	commit_shas?: string[];
	repo?: string;
	event_ids?: string[];
	event_id?: string;
	calendar_status?: string;
	message_id?: string;
	draft_id?: string;
	availability?: { free?: boolean; partial?: boolean };
}

export interface AgentOutput {
	agent: AgentName | string;
	status: string;
	answer: string;
	citations?: Citation[];
	tools?: ToolCall[];
	structured?: StructuredResult;
}

export interface ChatMessage {
	role: "user" | "assistant" | string;
	content: string;
}

export interface InterruptPayload {
	agent: string;
	kind: string;
	/** Raw gate preview — payload_preview is a plan list, so values are unknown. */
	payload: Record<string, unknown>;
}

export interface ThreadState {
	thread_id: string;
	agents: string[];
	agent_outputs: Record<string, AgentOutput>;
	status: string;
	messages: ChatMessage[];
	pending_interrupt: InterruptPayload | null;
	paused: boolean;
}

export type Mode = "demo" | "free" | "live";

export interface Health {
	mode: Mode | string;
	requested_mode: string;
	llm_provider: string;
	vector_store: string;
	embedding_provider: string;
	github_path: string;
	google_path: string;
	oauth_state: string;
	downgrades: string[];
	probe: {
		provider?: string;
		model?: string;
		ok?: boolean;
		warnings?: string[];
		error?: string;
	};
	time: string;
}

export type SSEEventKind =
	| "routing"
	| "agent_start"
	| "agent_token"
	| "agent_tool"
	| "agent_end"
	| "interrupt"
	| "aggregate"
	| "error"
	| "done";

export interface SSEEvent {
	kind: SSEEventKind | string;
	data: Record<
		string,
		string | number | boolean | null | Citation[] | string[] | StructuredResult
	>;
}
