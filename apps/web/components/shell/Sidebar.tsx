"use client";

import { ModePill } from "@/components/shell/ModePill";
import { Button } from "@/components/ui/button";
import { useUIStore } from "@/lib/stores/ui";
import { MessageSquarePlus, PanelLeftClose, PanelLeftOpen } from "lucide-react";
import Link from "next/link";
import { useState } from "react";

interface ThreadItem {
	thread_id: string;
	created_at?: string;
}

interface Props {
	mode: string;
	threads: ThreadItem[];
	activeThreadId: string | null;
	onNewChat: () => void;
}

function groupLabel(createdAt: string | undefined): string {
	if (createdAt === undefined) return "Older";
	const created = new Date(createdAt).getTime();
	const now = Date.now();
	const day = 86_400_000;
	if (now - created < day) return "Today";
	if (now - created < 2 * day) return "Yesterday";
	if (now - created < 7 * day) return "This week";
	return "Older";
}

export function Sidebar({ mode, threads, activeThreadId, onNewChat }: Props) {
	const { sidebarCollapsed, toggleSidebar } = useUIStore();
	const [filter, setFilter] = useState("");
	const visible = threads.filter((t) =>
		t.thread_id.toLowerCase().includes(filter.toLowerCase()),
	);
	const groups = new Map<string, ThreadItem[]>();
	for (const t of visible) {
		const label = groupLabel(t.created_at);
		const list = groups.get(label) ?? [];
		list.push(t);
		groups.set(label, list);
	}

	return (
		<aside
			className={sidebarCollapsed ? "w-14" : "w-64"}
			aria-label="Threads sidebar"
		>
			<div className="flex h-full flex-col gap-2 border-r border-[var(--border)] bg-[var(--surface)] p-2">
				<div className="flex items-center justify-between gap-2">
					{!sidebarCollapsed && <ModePill mode={mode} />}
					<button
						type="button"
						onClick={toggleSidebar}
						aria-label={
							sidebarCollapsed ? "Expand sidebar" : "Collapse sidebar"
						}
						className="rounded p-1 text-[var(--muted-foreground)] hover:text-[var(--foreground)]"
					>
						{sidebarCollapsed ? (
							<PanelLeftOpen size={18} />
						) : (
							<PanelLeftClose size={18} />
						)}
					</button>
				</div>
				{!sidebarCollapsed && (
					<>
						<Button onClick={onNewChat}>
							<span className="inline-flex items-center gap-2">
								<MessageSquarePlus size={16} aria-hidden /> New chat
							</span>
						</Button>
						<input
							value={filter}
							onChange={(e) => setFilter(e.target.value)}
							placeholder="Search threads"
							aria-label="Search threads"
							className="rounded-[6px] border border-[var(--border)] bg-[var(--background)] px-2 py-1 text-sm"
						/>
						<nav className="flex-1 overflow-y-auto" aria-label="Thread list">
							{[...groups.entries()].map(([label, items]) => (
								<div key={label} className="mt-2">
									<div className="px-2 text-xs uppercase text-[var(--muted-foreground)]">
										{label}
									</div>
									{items.map((t) => (
										<Link
											key={t.thread_id}
											href={`/chat/${encodeURIComponent(t.thread_id)}`}
											aria-current={
												t.thread_id === activeThreadId ? "page" : undefined
											}
											className={
												t.thread_id === activeThreadId
													? "block rounded px-2 py-1 text-sm bg-[var(--surface-elevated)]"
													: "block rounded px-2 py-1 text-sm hover:bg-[var(--surface-elevated)]"
											}
										>
											{t.thread_id}
										</Link>
									))}
								</div>
							))}
							{visible.length === 0 && (
								<p className="px-2 text-sm text-[var(--muted-foreground)]">
									No threads yet.
								</p>
							)}
						</nav>
						<div className="border-t border-[var(--border)] pt-2 text-xs text-[var(--muted-foreground)]">
							<Link href="/settings" className="underline">
								Settings
							</Link>
							{" · "}
							<Link href="/health" className="underline">
								Health
							</Link>
						</div>
					</>
				)}
			</div>
		</aside>
	);
}
