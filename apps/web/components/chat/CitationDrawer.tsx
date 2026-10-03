"use client";

import { useUIStore } from "@/lib/stores/ui";

export function CitationDrawer() {
	const open = useUIStore((s) => s.citationDrawerOpen);
	const citation = useUIStore((s) => s.selectedCitation);
	const close = useUIStore((s) => s.closeCitation);
	if (!open || citation === null) return null;
	return (
		<aside
			aria-label="Citation source preview"
			className="fixed right-0 top-0 z-40 h-full w-80 border-l border-[var(--border)] bg-[var(--surface)] p-4"
		>
			<div className="flex items-center justify-between">
				<h2 className="font-medium">Source preview</h2>
				<button
					type="button"
					onClick={close}
					aria-label="Close citation drawer"
					className="rounded p-1"
				>
					✕
				</button>
			</div>
			<dl className="mt-3 space-y-1 text-sm">
				<div className="flex gap-2">
					<dt className="text-[var(--muted-foreground)]">Source</dt>
					<dd className="font-mono">{citation.source}</dd>
				</div>
				<div className="flex gap-2">
					<dt className="text-[var(--muted-foreground)]">Page</dt>
					<dd className="font-mono">{citation.page}</dd>
				</div>
				{citation.chunk_id !== undefined && (
					<div className="flex gap-2">
						<dt className="text-[var(--muted-foreground)]">Chunk</dt>
						<dd className="font-mono">{String(citation.chunk_id)}</dd>
					</div>
				)}
				{typeof citation.score === "number" && (
					<div className="flex gap-2">
						<dt className="text-[var(--muted-foreground)]">Score</dt>
						<dd className="font-mono tabular-nums">
							{citation.score.toFixed(3)}
						</dd>
					</div>
				)}
			</dl>
			<p className="mt-3 text-xs text-[var(--muted-foreground)]">
				Grounded answer — every citation is one click from its source.
			</p>
		</aside>
	);
}
