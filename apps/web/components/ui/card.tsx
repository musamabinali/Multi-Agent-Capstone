import { clsx } from "clsx";

interface Props {
	accent?: "rag" | "github" | "calendar" | "gmail" | "none";
	children: React.ReactNode;
	className?: string;
}

const borders: Record<NonNullable<Props["accent"]>, string> = {
	rag: "border-l-4 border-l-[var(--accent-rag)]",
	github: "border-l-4 border-l-[var(--accent-github)]",
	calendar: "border-l-4 border-l-[var(--accent-calendar)]",
	gmail: "border-l-4 border-l-[var(--accent-gmail)]",
	none: "",
};

export function Card({ accent = "none", children, className }: Props) {
	return (
		<div
			className={clsx(
				"rounded-[10px] border border-[var(--border)] bg-[var(--surface)] p-4",
				borders[accent],
				className,
			)}
		>
			{children}
		</div>
	);
}
