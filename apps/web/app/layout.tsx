import type { Metadata } from "next";
import type { ReactNode } from "react";
import "@/styles/globals.css";
import { Providers } from "@/app/providers";

export const metadata: Metadata = {
	title: "MAKPA — Multi-Agent Workspace",
	description: "Supervisor + RAG + GitHub MCP + Google Workspace MCP",
};

export default function RootLayout({ children }: { children: ReactNode }) {
	return (
		<html lang="en">
			<body>
				<Providers>{children}</Providers>
			</body>
		</html>
	);
}
