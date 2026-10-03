import { clsx } from "clsx";

interface Props {
	tone:
		| "demo"
		| "free"
		| "live"
		| "ok"
		| "partial"
		| "error"
		| "muted"
		| "rag"
		| "github"
		| "calendar"
		| "gmail";
	children: React.ReactNode;
}

/* Solid pills use darkened (*-strong) backgrounds so white text passes
   WCAG AA; agent pills use surface backgrounds with accent text so the
   bright accents never carry text. Verified with the axe suite. */
const tones: Record<Props["tone"], string> = {
	demo: "bg-zinc-700 text-white",
	free: "bg-[var(--info-strong)] text-white",
	live: "bg-[var(--success-strong)] text-white",
	ok: "bg-[var(--success-strong)] text-white",
	partial: "bg-[var(--warning)] text-black",
	error: "bg-[var(--error)] text-white",
	muted: "bg-[var(--surface-elevated)] text-[var(--muted-foreground)]",
	rag: "border border-[var(--accent-rag)] bg-[var(--surface-elevated)] text-[var(--accent-rag)]",
	github:
		"border border-[var(--accent-github)] bg-[var(--surface-elevated)] text-[var(--accent-github)]",
	calendar:
		"border border-[var(--accent-calendar)] bg-[var(--surface-elevated)] text-[var(--accent-calendar)]",
	gmail:
		"border border-[var(--accent-gmail)] bg-[var(--surface-elevated)] text-[var(--accent-gmail)]",
};

export function Badge({ tone, children }: Props) {
	return (
		<span
			className={clsx(
				"inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium",
				tones[tone],
			)}
		>
			{children}
		</span>
	);
}
