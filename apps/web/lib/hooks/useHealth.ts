"use client";

import { fetchHealth } from "@/lib/api/client";
import { useQuery } from "@tanstack/react-query";

/** Backend + MCP reachability (refreshed every 15s). Mode is never hardcoded. */
export function useHealth(refetchInterval = 15_000) {
	return useQuery({
		queryKey: ["health"],
		queryFn: fetchHealth,
		refetchInterval,
	});
}
