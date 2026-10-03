"use client";

import { useUIStore } from "@/lib/stores/ui";
import type { Citation } from "@/lib/types";

interface Props {
	citations: Citation[];
}

export function CitationChips({ citations }: Props) {
	const openCitation = useUIStore((s) => s.openCitation);
	if (citations.length === 0) return null;
	return (
		<div className="mt-2 flex flex-wrap gap-1" aria-label="Citations">
			{citations.map((c, i) => (
				<button
					type="button"
					key={`${c.source}-${c.page}-${i}`}
					onClick={() => openCitation(c)}
					className="rounded-[6px] border border-[var(--border)] bg-[var(--surface-elevated)] px-2 py-0.5 text-xs hover:border-[var(--primary)]"
					aria-label={`Open source ${c.source} page ${c.page}`}
				>
					[{c.source} · p.{c.page}]
				</button>
			))}
		</div>
	);
}
