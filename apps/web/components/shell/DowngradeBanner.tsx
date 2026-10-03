"use client";

import { TriangleAlert } from "lucide-react";
import Link from "next/link";

interface Props {
	mode: string;
	downgrades: string[];
}

/** Honest-mode banner — always rendered when downgrades exist, never hidden. */
export function DowngradeBanner({ mode, downgrades }: Props) {
	if (downgrades.length === 0) return null;
	return (
		<output
			aria-live="polite"
			className="block rounded-[10px] border border-[var(--warning)] bg-[var(--surface-elevated)] p-3 text-sm"
		>
			<div className="flex items-center gap-2 font-medium">
				<TriangleAlert size={16} aria-hidden />
				<span>Running in {mode.toUpperCase()} mode</span>
			</div>
			<ul className="mt-1 list-disc pl-6 text-[var(--muted-foreground)]">
				{downgrades.map((reason) => (
					<li key={reason}>{reason}</li>
				))}
			</ul>
			<Link
				href="/settings"
				className="mt-1 inline-block text-[var(--primary)] underline"
			>
				Configure credentials
			</Link>
		</output>
	);
}
