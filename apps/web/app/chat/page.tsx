"use client";

import { ChatView } from "@/components/chat/ChatView";
import { AppShell } from "@/components/shell/AppShell";
import { DowngradeBanner } from "@/components/shell/DowngradeBanner";
import { createThread, listThreads } from "@/lib/api/client";
import { useChatStream } from "@/lib/hooks/useChatStream";
import { useHealth } from "@/lib/hooks/useHealth";
import { useThreadStore } from "@/lib/stores/thread";
import { useQuery } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useState } from "react";

export default function NewChatPage() {
	const router = useRouter();
	const health = useHealth();
	const threads = useQuery({ queryKey: ["threads"], queryFn: listThreads });
	const { send } = useChatStream();
	const [sending, setSending] = useState(false);
	const mode =
		typeof health.data?.mode === "string" ? health.data.mode : "demo";

	const start = async (message: string) => {
		setSending(true);
		try {
			const created = await createThread();
			useThreadStore.getState().setThread(created.thread_id);
			threads.refetch().catch(() => undefined);
			router.push(`/chat/${encodeURIComponent(created.thread_id)}`);
			await send(created.thread_id, message);
		} finally {
			setSending(false);
		}
	};

	return (
		<AppShell
			mode={mode}
			threads={threads.data?.threads ?? []}
			activeThreadId={null}
			onNewChat={() => useThreadStore.getState().reset()}
		>
			<div className="flex items-center justify-between border-b border-[var(--border)] p-3">
				<h1 className="font-medium">MAKPA</h1>
			</div>
			<div className="p-3">
				<DowngradeBanner
					mode={mode}
					downgrades={health.data?.downgrades ?? []}
				/>
			</div>
			<ChatView
				mode={mode}
				sending={sending}
				onSend={start}
				onVerifyPartial={() => undefined}
			/>
		</AppShell>
	);
}
