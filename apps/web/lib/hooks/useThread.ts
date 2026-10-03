"use client";

import { loadThread } from "@/lib/api/client";
import { useQuery } from "@tanstack/react-query";

/** Authoritative thread snapshot (history, outputs, pending interrupt). */
export function useThread(threadId: string | null) {
	return useQuery({
		queryKey: ["thread", threadId],
		queryFn: () => {
			if (threadId === null) throw new Error("no thread selected");
			return loadThread(threadId);
		},
		enabled: threadId !== null,
	});
}
