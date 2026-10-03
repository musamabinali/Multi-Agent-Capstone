"use client";

import { Button } from "@/components/ui/button";
import type { InterruptPayload } from "@/lib/types";
import { useEffect, useRef, useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

const schema = z.object({ acknowledged: z.literal(true) });

interface Props {
	interrupt: InterruptPayload;
	busy: boolean;
	onConfirm: () => void;
	onCancel: () => void;
	onRollback: () => void;
}

/** Tool names from the interrupt's payload_preview plan (e.g. gmail_send_message). */
export function previewTools(interrupt: InterruptPayload): string[] {
	const raw = interrupt.payload.payload_preview;
	if (!Array.isArray(raw)) return [];
	const tools: string[] = [];
	for (const item of raw) {
		if (item !== null && typeof item === "object" && "tool" in item) {
			const tool = (item as { tool?: unknown }).tool;
			if (typeof tool === "string") tools.push(tool);
		}
	}
	return tools;
}

function isEmailGate(interrupt: InterruptPayload): boolean {
	const blob = previewTools(interrupt).join(" ");
	return (
		interrupt.kind.includes("email") ||
		interrupt.kind.includes("send") ||
		interrupt.agent.includes("gmail") ||
		blob.includes("gmail_send_message")
	);
}

function isCalendarGate(interrupt: InterruptPayload): boolean {
	const blob = previewTools(interrupt).join(" ");
	return (
		interrupt.kind.includes("calendar") ||
		interrupt.kind.includes("event") ||
		blob.includes("calendar_")
	);
}

function isGitHubGate(interrupt: InterruptPayload): boolean {
	const blob = previewTools(interrupt).join(" ");
	return interrupt.kind.includes("github") || blob.includes("github_");
}

export function ConfirmationModal({
	interrupt,
	busy,
	onConfirm,
	onCancel,
	onRollback,
}: Props) {
	const { register, watch } = useForm<{ acknowledged: boolean }>({
		defaultValues: { acknowledged: false },
	});
	const acknowledged = watch("acknowledged");
	const acknowledgedParsed = schema.safeParse({ acknowledged }).success;
	const dialogRef = useRef<HTMLDivElement>(null);
	const [entries] = useState<[string, unknown][]>(() =>
		Object.entries(interrupt.payload),
	);
	const showRollback =
		isEmailGate(interrupt) ||
		interrupt.kind === "2" ||
		interrupt.kind.includes("gate");

	useEffect(() => {
		const first =
			dialogRef.current?.querySelector<HTMLElement>("button, input");
		first?.focus();
		const onKey = (e: KeyboardEvent) => {
			if (e.key === "Escape") onCancel();
		};
		window.addEventListener("keydown", onKey);
		return () => window.removeEventListener("keydown", onKey);
	}, [onCancel]);

	const title = isCalendarGate(interrupt)
		? "Confirm calendar event"
		: isEmailGate(interrupt)
			? "Confirm email send"
			: isGitHubGate(interrupt)
				? "Confirm GitHub write"
				: "Confirm action";

	return (
		<div
			className="fixed inset-0 z-50 flex items-center justify-center bg-black/60"
			role="presentation"
		>
			<div
				ref={dialogRef}
				role="alertdialog"
				aria-modal="true"
				aria-label={title}
				className="w-full max-w-lg rounded-[14px] border border-[var(--border)] bg-[var(--surface)] p-5"
			>
				<div className="flex items-center justify-between">
					<h2 className="text-base font-medium">{title}</h2>
					<button
						type="button"
						onClick={onCancel}
						aria-label="Close confirmation"
						className="rounded p-1 text-[var(--muted-foreground)]"
					>
						✕
					</button>
				</div>
				<dl className="mt-3 space-y-1 text-sm">
					{entries.map(([key, value]) => (
						<div key={key} className="flex gap-2">
							<dt className="w-28 shrink-0 text-[var(--muted-foreground)]">
								{key}
							</dt>
							<dd className="min-w-0 flex-1 break-words font-mono text-xs">
								{typeof value === "string" ? value : JSON.stringify(value)}
							</dd>
						</div>
					))}
				</dl>
				<label className="mt-3 flex items-center gap-2 text-sm">
					<input type="checkbox" {...register("acknowledged")} />I reviewed the
					payload above
				</label>
				<div className="mt-4 flex justify-end gap-2">
					<Button variant="secondary" onClick={onCancel} disabled={busy}>
						Cancel
					</Button>
					{showRollback && (
						<Button
							variant="danger"
							onClick={onRollback}
							disabled={busy || !acknowledgedParsed}
						>
							Rollback event
						</Button>
					)}
					<Button onClick={onConfirm} disabled={busy || !acknowledgedParsed}>
						{busy
							? "Working…"
							: title.includes("email")
								? "Confirm & send"
								: "Confirm & create"}
					</Button>
				</div>
			</div>
		</div>
	);
}
