"use client";

import { TriangleAlert } from "lucide-react";

interface Props {
	answer: string;
	onVerify: () => void;
}

/** Partial availability is a warning state — never rendered as success. */
export function PartialAvailabilityNotice({ answer, onVerify }: Props) {
	const lowered = answer.toLowerCase();
	const isPartial =
		lowered.includes("partial") ||
		lowered.includes("could not be verified") ||
		lowered.includes("attendee");
	if (!isPartial) return null;
	return (
		<div
			role="alert"
			className="rounded-[10px] border border-[var(--warning)] bg-[var(--surface-elevated)] p-3 text-sm"
		>
			<div className="flex items-center gap-2 font-medium">
				<TriangleAlert size={16} aria-hidden />
				<span>Availability check is partial</span>
			</div>
			<p className="mt-1 text-[var(--muted-foreground)]">
				External attendee calendars could not be verified. Auto-create is
				refused.
			</p>
			<div className="mt-2 flex gap-2">
				<button
					type="button"
					onClick={onVerify}
					className="rounded-[6px] border border-[var(--border)] px-3 py-1 text-sm hover:border-[var(--primary)]"
				>
					Verify manually
				</button>
			</div>
		</div>
	);
}
