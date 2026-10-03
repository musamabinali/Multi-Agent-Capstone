"use client";

import { ChatView } from "@/components/chat/ChatView";
import { CitationDrawer } from "@/components/chat/CitationDrawer";
import { ErrorCard } from "@/components/chat/ErrorCard";
import { ConfirmationModal } from "@/components/modals/ConfirmationModal";
import { AppShell } from "@/components/shell/AppShell";
import { DowngradeBanner } from "@/components/shell/DowngradeBanner";
import {
	createThread,
	fetchHealth,
	listThreads,
	loadThread,
	resumeThread,
} from "@/lib/api/client";
import { useChatStream } from "@/lib/hooks/useChatStream";
import { useHealth } from "@/lib/hooks/useHealth";
import { useThreadStore } from "@/lib/stores/thread";
import { useQuery } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

export default function ThreadPage() {
	const params = useParams<{ threadId: string }>();
	const threadId = decodeURIComponent(params.threadId);
	const router = useRouter();
	const health = useHealth();
	const threads = useQuery({ queryKey: ["threads"], queryFn: listThreads });
	const { send, stop } = useChatStream();
	const [sending, setSending] = useState(false);
	const [resuming, setResuming] = useState(false);
	const pendingInterrupt = useThreadStore((s) => s.pendingInterrupt);
	const overallStatus = useThreadStore((s) => s.overallStatus);
	const storeMessages = useThreadStore((s) => s.messages);
	const mode =
		typeof health.data?.mode === "string" ? health.data.mode : "demo";
	const lastUserMessage = [...storeMessages]
		.reverse()
		.find((m) => m.role === "user")?.content;

	// Mount-time hydration must never clobber a live stream: the backend
	// answers fresh threads with an empty "ok" snapshot, which can resolve
	// after stream events and wipe cards. Apply only while still pristine.
	useEffect(() => {
		let cancelled = false;
		const store = useThreadStore.getState();
		if (store.threadId !== threadId) store.setThread(threadId);
		loadThread(threadId)
			.then((full) => {
				if (cancelled) return;
				const live = useThreadStore.getState();
				if (live.threadId !== threadId) return;
				if (live.messages.length > 0) return;
				live.applyRouting(full.agents, "");
				live.applyOutputs(full.agent_outputs);
				live.setInterrupt(full.pending_interrupt);
				live.setAggregate(full.status);
			})
			.catch(() => undefined);
		return () => {
			cancelled = true;
			stop();
		};
	}, [threadId, stop]);

	const onSend = async (message: string) => {
		setSending(true);
		try {
			await send(threadId, message);
		} finally {
			setSending(false);
		}
	};

	const doResume = async (body: { confirm?: boolean; rollback?: boolean }) => {
		setResuming(true);
		try {
			const full = await resumeThread(threadId, body);
			const store = useThreadStore.getState();
			store.applyOutputs(full.agent_outputs);
			store.setInterrupt(full.pending_interrupt);
			store.setAggregate(full.status);
		} finally {
			setResuming(false);
		}
	};

	const onNewChat = async () => {
		const created = await createThread();
		router.push(`/chat/${encodeURIComponent(created.thread_id)}`);
	};

	return (
		<AppShell
			mode={mode}
			threads={threads.data?.threads ?? []}
			activeThreadId={threadId}
			onNewChat={onNewChat}
		>
			<div className="flex items-center justify-between border-b border-[var(--border)] p-3">
				<h1 className="font-mono text-sm">{threadId}</h1>
			</div>
			<div className="p-3">
				<DowngradeBanner
					mode={mode}
					downgrades={health.data?.downgrades ?? []}
				/>
			</div>
			{overallStatus === "error" && (
				<div className="px-3">
					<ErrorCard
						message="The supervisor hit an error. Completed agents are preserved above."
						retryable
						onRetry={() => {
							if (lastUserMessage !== undefined) onSend(lastUserMessage);
						}}
						onContinue={() => useThreadStore.getState().setAggregate("partial")}
					/>
				</div>
			)}
			<ChatView
				mode={mode}
				sending={sending || resuming}
				onSend={onSend}
				onVerifyPartial={() => undefined}
			/>
			{pendingInterrupt !== null && (
				<ConfirmationModal
					interrupt={pendingInterrupt}
					busy={resuming}
					onConfirm={() => doResume({ confirm: true })}
					onCancel={() => doResume({ confirm: false })}
					onRollback={() => doResume({ rollback: true })}
				/>
			)}
			<CitationDrawer />
		</AppShell>
	);
}
