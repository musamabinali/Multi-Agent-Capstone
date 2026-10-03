"use client";

import { Send } from "lucide-react";
import { useState } from "react";

interface Props {
	mode: string;
	disabled: boolean;
	onSend: (message: string) => void;
}

export function Composer({ mode, disabled, onSend }: Props) {
	const [value, setValue] = useState("");
	const submit = () => {
		const trimmed = value.trim();
		if (trimmed.length === 0 || disabled) return;
		setValue("");
		onSend(trimmed);
	};
	return (
		<div className="border-t border-[var(--border)] bg-[var(--surface)] p-3">
			<div className="flex items-end gap-2">
				<textarea
					value={value}
					onChange={(e) => setValue(e.target.value)}
					onKeyDown={(e) => {
						if (e.key === "Enter" && !e.shiftKey) {
							e.preventDefault();
							submit();
						}
					}}
					placeholder="Type your message..."
					aria-label="Type your message"
					rows={2}
					disabled={disabled}
					className="min-h-11 flex-1 resize-none rounded-[10px] border border-[var(--border)] bg-[var(--background)] px-3 py-2 text-sm"
				/>
				<button
					type="button"
					onClick={submit}
					disabled={disabled || value.trim().length === 0}
					aria-label="Send message"
					className="rounded-[10px] bg-[var(--primary-solid)] p-2.5 text-white disabled:opacity-50"
				>
					<Send size={18} aria-hidden />
				</button>
			</div>
			<div className="mt-1 text-xs text-[var(--muted-foreground)]">
				Mode: {mode}
			</div>
		</div>
	);
}
