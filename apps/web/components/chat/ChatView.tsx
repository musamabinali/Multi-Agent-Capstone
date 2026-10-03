"use client";

import { AgentMessageCard } from "@/components/chat/AgentMessageCard";
import { Composer } from "@/components/chat/Composer";
import { PartialAvailabilityNotice } from "@/components/chat/PartialAvailabilityNotice";
import { SupervisorRoutingCard } from "@/components/chat/SupervisorRoutingCard";
import { useSettingsStore } from "@/lib/stores/settings";
import { useThreadStore } from "@/lib/stores/thread";

interface Props {
	mode: string;
	sending: boolean;
	onSend: (message: string) => void;
	onVerifyPartial: () => void;
}

export function ChatView({ mode, sending, onSend, onVerifyPartial }: Props) {
	const messages = useThreadStore((s) => s.messages);
	const agents = useThreadStore((s) => s.agents);
	const agentViews = useThreadStore((s) => s.agentViews);
	const reasoning = useThreadStore((s) => s.reasoning);
	const overallStatus = useThreadStore((s) => s.overallStatus);
	const showReasoning = useSettingsStore((s) => s.showReasoning);

	return (
		<div className="flex min-h-0 flex-1 flex-col">
			<div
				className="min-h-0 flex-1 space-y-3 overflow-y-auto p-4"
				aria-live="polite"
			>
				{messages
					.filter((m) => m.role === "user")
					.map((m) => (
						<div
							key={`u-${m.role}-${m.content}`}
							className="rounded-[10px] bg-[var(--surface-elevated)] p-3 text-sm"
						>
							<span className="font-medium">You: </span>
							{m.content}
						</div>
					))}
				<SupervisorRoutingCard
					agents={agents}
					reasoning={reasoning}
					showReasoning={showReasoning}
				/>
				{agents.map((agent) => {
					const view = agentViews[agent];
					if (view === undefined) return null;
					return (
						<div key={agent}>
							<AgentMessageCard
								output={{
									agent,
									status: view.status,
									answer: view.answer,
									citations: view.citations ?? [],
									tools: view.tools ?? [],
									structured: view.structured,
								}}
								streaming={view.streaming}
							/>
							<PartialAvailabilityNotice
								answer={view.answer}
								onVerify={onVerifyPartial}
							/>
						</div>
					);
				})}
				{overallStatus && (
					<p className="text-xs text-[var(--muted-foreground)]">
						Overall status: {overallStatus}
					</p>
				)}
				{messages.length === 0 && agents.length === 0 && (
					<div className="py-16 text-center">
						<div className="text-2xl" aria-hidden>
							🎯
						</div>
						<h2 className="mt-2 text-lg font-medium">Start a conversation</h2>
						<ul className="mt-3 space-y-1 text-sm text-[var(--muted-foreground)]">
							<li>“Summarize the sample PDF”</li>
							<li>“List open PRs in octo-demo/hello-world”</li>
							<li>“Schedule a meeting with a@x.com tomorrow”</li>
						</ul>
					</div>
				)}
			</div>
			<Composer mode={mode} disabled={sending} onSend={onSend} />
		</div>
	);
}
