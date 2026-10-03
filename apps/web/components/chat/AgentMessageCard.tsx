"use client";

import { CitationChips } from "@/components/chat/CitationChips";
import { StructuredResultTable } from "@/components/chat/StructuredResultTable";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import type { AgentOutput } from "@/lib/types";
import { motion } from "framer-motion";
import { BookOpen, Calendar, Github, Mail } from "lucide-react";

interface Props {
	output: AgentOutput;
	streaming: boolean;
	durationMs?: number;
}

function accentFor(agent: string): "rag" | "github" | "calendar" | "gmail" {
	if (agent === "rag_agent") return "rag";
	if (agent === "github_agent") return "github";
	if (agent.includes("gmail")) return "gmail";
	return "calendar";
}

function iconFor(agent: string) {
	if (agent === "rag_agent") return <BookOpen size={16} aria-hidden />;
	if (agent === "github_agent") return <Github size={16} aria-hidden />;
	if (agent.includes("gmail")) return <Mail size={16} aria-hidden />;
	return <Calendar size={16} aria-hidden />;
}

function labelFor(agent: string): string {
	if (agent === "rag_agent") return "RAG agent";
	if (agent === "github_agent") return "GitHub agent";
	if (agent === "google_agent") return "Calendar / Gmail agent";
	return agent;
}

export function AgentMessageCard({ output, streaming, durationMs }: Props) {
	const accent = accentFor(output.agent);
	const status = streaming ? "streaming" : output.status;
	return (
		<motion.div
			initial={{ opacity: 0 }}
			animate={{ opacity: 1 }}
			transition={{ duration: 0.12 }}
		>
			<Card accent={accent}>
				<div className="flex items-center gap-2" aria-live="polite">
					{iconFor(output.agent)}
					<span className="font-medium">{labelFor(output.agent)}</span>
					<Badge
						tone={
							status === "ok"
								? "ok"
								: status === "error"
									? "error"
									: status === "partial"
										? "partial"
										: "muted"
						}
					>
						{status}
						{typeof durationMs === "number"
							? ` · ${(durationMs / 1000).toFixed(1)}s`
							: ""}
					</Badge>
				</div>
				<p className="mt-2 whitespace-pre-wrap text-sm">{output.answer}</p>
				{output.tools !== undefined && output.tools.length > 0 && (
					<p className="mt-1 text-xs text-[var(--muted-foreground)]">
						Tools:{" "}
						{output.tools.map((t) => `${t.tool} (${t.status})`).join(", ")}
					</p>
				)}
				<CitationChips citations={output.citations ?? []} />
				<StructuredResultTable
					agent={output.agent}
					structured={output.structured}
				/>
			</Card>
		</motion.div>
	);
}
