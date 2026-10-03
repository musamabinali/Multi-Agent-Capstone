/** Optional docs hub — pointers to the repo docs, never a second source of truth. */
export default function DocsPage() {
	const docs: [string, string][] = [
		["README.md", "Setup, modes, CLI usage, OAuth guide"],
		["docs/ARCHITECTURE.md", "Hub-and-spoke diagram and schemas"],
		["docs/DEMO_TRANSCRIPT.md", "Demo + free transcripts"],
		["docs/SPEC_RECONCILIATION.md", "Spec-vs-delivered drift log"],
		["apps/web/docs/BUILD.md", "Frontend design artifacts 1–7"],
		["apps/web/docs/Frontend Build.md", "Frontend build spec"],
	];
	return (
		<main className="mx-auto max-w-2xl space-y-4 p-6">
			<h1 className="text-xl font-medium">Docs</h1>
			<ul className="space-y-2 text-sm">
				{docs.map(([file, blurb]) => (
					<li
						key={file}
						className="rounded-[10px] border border-[var(--border)] bg-[var(--surface)] p-3"
					>
						<span className="font-mono">{file}</span>
						<span className="text-[var(--muted-foreground)]"> — {blurb}</span>
					</li>
				))}
			</ul>
		</main>
	);
}
