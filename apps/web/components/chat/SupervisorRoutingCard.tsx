"use client";

import { Network } from "lucide-react";

interface Props {
	agents: string[];
	reasoning: string;
	showReasoning: boolean;
}

export function SupervisorRoutingCard({
	agents,
	reasoning,
	showReasoning,
}: Props) {
	if (agents.length === 0) return null;
	return (
		<div
			className="rounded-[10px] border border-[var(--border)] bg-[var(--surface-elevated)] p-3 text-sm"
			aria-live="polite"
		>
			<div className="flex items-center gap-2">
				<Network size={16} aria-hidden />
				<span>
					Supervisor routed to {agents.length} agent
					{agents.length === 1 ? "" : "s"} in parallel:
				</span>
				<span className="font-medium">{agents.join(" · ")}</span>
			</div>
			{showReasoning && reasoning && (
				<p className="mt-1 text-xs text-[var(--muted-foreground)]">
					{reasoning}
				</p>
			)}
		</div>
	);
}
