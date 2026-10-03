"use client";

import type { StructuredResult } from "@/lib/types";

interface Props {
	agent: string;
	structured?: StructuredResult;
}

function text(value: unknown): string | null {
	if (typeof value === "string" && value.length > 0) return value;
	if (typeof value === "number") return String(value);
	return null;
}

function rowsFor(
	agent: string,
	structured: StructuredResult,
): [string, string][] {
	const rows: [string, string][] = [];
	const list = (value: unknown): string[] =>
		Array.isArray(value)
			? value
					.filter(
						(v): v is string | number =>
							typeof v === "string" || typeof v === "number",
					)
					.map(String)
			: [];
	if (agent === "rag_agent") {
		const count = structured.chunk_count;
		if (typeof count === "number") rows.push(["chunks", String(count)]);
		return rows;
	}
	if (agent === "github_agent") {
		const prs = list(structured.pr_numbers);
		const issues = list(structured.issue_numbers);
		const shas = list(structured.commit_shas);
		if (prs.length > 0) rows.push(["pr_numbers", prs.join(", ")]);
		if (issues.length > 0) rows.push(["issue_numbers", issues.join(", ")]);
		if (shas.length > 0) rows.push(["commit_shas", shas.join(", ")]);
		const repo = text(structured.repo);
		if (repo !== null) rows.push(["repo", repo]);
		return rows;
	}
	const eventIds = list(structured.event_ids);
	const eventId = text(structured.event_id);
	const messageId = text(structured.message_id);
	const draftId = text(structured.draft_id);
	const status = text(structured.calendar_status);
	if (eventIds.length > 0) rows.push(["event_ids", eventIds.join(", ")]);
	else if (eventId !== null) rows.push(["event_id", eventId]);
	if (messageId !== null) rows.push(["message_id", messageId]);
	if (draftId !== null) rows.push(["draft_id", draftId]);
	if (status !== null) rows.push(["calendar_status", status]);
	const availability = structured.availability;
	if (
		availability !== undefined &&
		typeof availability === "object" &&
		availability !== null
	) {
		const free = (availability as { free?: unknown }).free;
		const partial = (availability as { partial?: unknown }).partial;
		if (typeof free === "boolean" || typeof partial === "boolean") {
			rows.push([
				"availability",
				`free=${String(free)} partial=${String(partial)}`,
			]);
		}
	}
	return rows;
}

/** Structured ids threaded from tool_results — never parsed from prose. */
export function StructuredResultTable({ agent, structured }: Props) {
	if (structured === undefined) {
		return (
			<p className="mt-2 text-xs text-[var(--muted-foreground)]">
				no structured result
			</p>
		);
	}
	const rows = rowsFor(agent, structured);
	if (rows.length === 0) {
		return (
			<p className="mt-2 text-xs text-[var(--muted-foreground)]">
				no structured result
			</p>
		);
	}
	return (
		<table className="mt-2 w-full text-xs" aria-label="Structured result">
			<tbody>
				{rows.map(([label, value]) => (
					<tr key={label} className="border-t border-[var(--border)]">
						<td className="py-1 pr-2 text-[var(--muted-foreground)]">
							{label}
						</td>
						<td className="py-1 font-mono tabular-nums">{value}</td>
					</tr>
				))}
			</tbody>
		</table>
	);
}
