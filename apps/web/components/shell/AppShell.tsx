"use client";

import { Sidebar } from "@/components/shell/Sidebar";

interface Props {
	mode: string;
	threads: { thread_id: string; created_at?: string }[];
	activeThreadId: string | null;
	onNewChat: () => void;
	children: React.ReactNode;
}

export function AppShell({
	mode,
	threads,
	activeThreadId,
	onNewChat,
	children,
}: Props) {
	return (
		<div className="flex h-screen">
			<Sidebar
				mode={mode}
				threads={threads}
				activeThreadId={activeThreadId}
				onNewChat={onNewChat}
			/>
			<main className="flex min-w-0 flex-1 flex-col">{children}</main>
		</div>
	);
}
