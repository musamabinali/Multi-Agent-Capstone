import { AgentMessageCard } from "@/components/chat/AgentMessageCard";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

describe("<AgentMessageCard>", () => {
	it("renders streaming state", () => {
		render(
			<AgentMessageCard
				output={{ agent: "rag_agent", status: "ok", answer: "hello" }}
				streaming
			/>,
		);
		expect(screen.getByText("RAG agent")).toBeInTheDocument();
		expect(screen.getByText("streaming")).toBeInTheDocument();
	});

	it("renders ok with citations", () => {
		render(
			<AgentMessageCard
				output={{
					agent: "rag_agent",
					status: "ok",
					answer: "grounded",
					citations: [{ source: "sample.pdf", page: 7 }],
				}}
				streaming={false}
			/>,
		);
		expect(screen.getByText("grounded")).toBeInTheDocument();
		expect(
			screen.getByRole("button", { name: /sample\.pdf/ }),
		).toBeInTheDocument();
	});

	it("renders partial and error distinctly", () => {
		const { rerender } = render(
			<AgentMessageCard
				output={{ agent: "github_agent", status: "partial", answer: "p" }}
				streaming={false}
			/>,
		);
		expect(screen.getByText("partial")).toBeInTheDocument();
		rerender(
			<AgentMessageCard
				output={{ agent: "github_agent", status: "error", answer: "e" }}
				streaming={false}
			/>,
		);
		expect(screen.getByText("error")).toBeInTheDocument();
	});
});
