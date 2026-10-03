"use client";

import { Badge } from "@/components/ui/badge";

interface Props {
	mode: string;
}

export function ModePill({ mode }: Props) {
	const tone = mode === "live" ? "live" : mode === "free" ? "free" : "demo";
	return (
		<span aria-label={`Mode: ${mode}`}>
			<Badge tone={tone}>Mode: {mode}</Badge>
		</span>
	);
}
