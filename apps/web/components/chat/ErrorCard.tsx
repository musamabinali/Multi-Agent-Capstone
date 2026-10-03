"use client";

import { Button } from "@/components/ui/button";
import { CircleX } from "lucide-react";

interface Props {
	message: string;
	retryable: boolean;
	onRetry: () => void;
	onContinue: () => void;
}

export function ErrorCard({ message, retryable, onRetry, onContinue }: Props) {
	return (
		<div
			role="alert"
			className="rounded-[10px] border border-[var(--error)] bg-[var(--surface)] p-4"
		>
			<div className="flex items-center gap-2 font-medium">
				<CircleX size={16} aria-hidden />
				<span>Supervisor error</span>
			</div>
			<p className="mt-1 text-sm text-[var(--muted-foreground)]">{message}</p>
			<div className="mt-2 flex gap-2">
				{retryable && <Button onClick={onRetry}>Retry</Button>}
				<Button variant="secondary" onClick={onContinue}>
					Continue without
				</Button>
			</div>
		</div>
	);
}
