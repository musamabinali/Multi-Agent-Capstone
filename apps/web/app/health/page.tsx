"use client";

import { Badge } from "@/components/ui/badge";
import { fetchHealth } from "@/lib/api/client";
import { useQuery } from "@tanstack/react-query";

export default function HealthPage() {
	const health = useQuery({
		queryKey: ["health"],
		queryFn: fetchHealth,
		refetchInterval: 15_000,
	});
	const d = health.data;
	return (
		<main className="mx-auto max-w-2xl space-y-4 p-6">
			<h1 className="text-xl font-medium">Backend + MCP reachability</h1>
			{d === undefined ? (
				<p>Loading…</p>
			) : (
				<div className="space-y-2 rounded-[10px] border border-[var(--border)] bg-[var(--surface)] p-4 text-sm">
					<div className="flex gap-2">
						<Badge
							tone={
								d.mode === "live" ? "live" : d.mode === "free" ? "free" : "demo"
							}
						>
							{String(d.mode)}
						</Badge>
						<Badge tone="muted">LLM: {String(d.llm_provider)}</Badge>
						<Badge tone="muted">Vector: {String(d.vector_store)}</Badge>
					</div>
					<p>
						GitHub MCP:{" "}
						<span className="font-mono">{String(d.github_path)}</span>
					</p>
					<p>
						Google MCP:{" "}
						<span className="font-mono">{String(d.google_path)}</span>
					</p>
					<p>
						OAuth: <span className="font-mono">{String(d.oauth_state)}</span>
					</p>
					<p>
						Probe: <span className="font-mono">{JSON.stringify(d.probe)}</span>
					</p>
					{(d.downgrades ?? []).length > 0 && (
						<ul className="list-disc pl-5 text-[var(--muted-foreground)]">
							{(d.downgrades ?? []).map((r) => (
								<li key={r}>{r}</li>
							))}
						</ul>
					)}
				</div>
			)}
		</main>
	);
}
