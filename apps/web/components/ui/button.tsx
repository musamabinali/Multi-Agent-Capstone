import { clsx } from "clsx";
import type { ButtonHTMLAttributes } from "react";

interface Props extends ButtonHTMLAttributes<HTMLButtonElement> {
	variant?: "primary" | "secondary" | "danger" | "ghost";
}

export function Button({ variant = "primary", className, ...rest }: Props) {
	const styles: Record<NonNullable<Props["variant"]>, string> = {
		primary:
			"bg-[var(--primary-solid)] text-[var(--primary-foreground)] hover:opacity-90",
		secondary:
			"bg-[var(--surface-elevated)] text-[var(--foreground)] hover:opacity-90",
		danger: "bg-[var(--error)] text-white hover:opacity-90",
		ghost:
			"bg-transparent text-[var(--muted-foreground)] hover:text-[var(--foreground)]",
	};
	return (
		<button
			className={clsx(
				"rounded-[10px] px-4 py-2 text-sm font-medium disabled:cursor-not-allowed disabled:opacity-50",
				styles[variant],
				className,
			)}
			{...rest}
		/>
	);
}
