"use client";

import { Button } from "@/components/ui/button";
import { triggerIngest } from "@/lib/api/client";
import { useHealth } from "@/lib/hooks/useHealth";
import { useSettingsStore } from "@/lib/stores/settings";
import { useState } from "react";

export default function SettingsPage() {
	const health = useHealth(0);
	const { compactMode, showReasoning, toggleCompact, toggleReasoning } =
		useSettingsStore();
	const [ingestPath, setIngestPath] = useState("");
	const [ingestResult, setIngestResult] = useState<string>("");

	const rows: [string, string][] = [
		["Mode", String(health.data?.mode ?? "—")],
		["Requested mode", String(health.data?.requested_mode ?? "—")],
		["LLM provider", String(health.data?.llm_provider ?? "—")],
		["Vector store", String(health.data?.vector_store ?? "—")],
		["GitHub MCP", String(health.data?.github_path ?? "—")],
		["Google MCP", String(health.data?.google_path ?? "—")],
		["Google OAuth", String(health.data?.oauth_state ?? "—")],
	];

	return (
		<main className="mx-auto max-w-2xl space-y-4 p-6">
			<h1 className="text-xl font-medium">Settings</h1>
			<section className="rounded-[10px] border border-[var(--border)] bg-[var(--surface)] p-4">
				<h2 className="font-medium">Backend status</h2>
				<table className="mt-2 w-full text-sm">
					<tbody>
						{rows.map(([k, v]) => (
							<tr key={k} className="border-t border-[var(--border)]">
								<td className="py-1 pr-2 text-[var(--muted-foreground)]">
									{k}
								</td>
								<td className="py-1 font-mono">{v}</td>
							</tr>
						))}
					</tbody>
				</table>
				{(health.data?.downgrades ?? []).length > 0 && (
					<ul className="mt-2 list-disc pl-5 text-sm text-[var(--muted-foreground)]">
						{(health.data?.downgrades ?? []).map((d) => (
							<li key={d}>{d}</li>
						))}
					</ul>
				)}
			</section>
			<section className="rounded-[10px] border border-[var(--border)] bg-[var(--surface)] p-4">
				<h2 className="font-medium">Preferences</h2>
				<label className="mt-2 flex items-center gap-2 text-sm">
					<input
						type="checkbox"
						checked={compactMode}
						onChange={toggleCompact}
					/>{" "}
					Compact mode
				</label>
				<label className="mt-2 flex items-center gap-2 text-sm">
					<input
						type="checkbox"
						checked={showReasoning}
						onChange={toggleReasoning}
					/>{" "}
					Show routing reasoning
				</label>
			</section>
			<section className="rounded-[10px] border border-[var(--border)] bg-[var(--surface)] p-4">
				<h2 className="font-medium">PDF ingestion</h2>
				<div className="mt-2 flex gap-2">
					<input
						value={ingestPath}
						onChange={(e) => setIngestPath(e.target.value)}
						placeholder="./data/sample.pdf"
						aria-label="PDF path"
						className="flex-1 rounded-[6px] border border-[var(--border)] bg-[var(--background)] px-2 py-1 text-sm"
					/>
					<Button
						onClick={() =>
							triggerIngest(ingestPath || undefined)
								.then((r) =>
									setIngestResult(`${r.chunks_created} chunks → ${r.backend}`),
								)
								.catch((e: unknown) =>
									setIngestResult(e instanceof Error ? e.message : "failed"),
								)
						}
					>
						Ingest
					</Button>
				</div>
				{ingestResult && <p className="mt-2 text-sm">{ingestResult}</p>}
			</section>
		</main>
	);
}
