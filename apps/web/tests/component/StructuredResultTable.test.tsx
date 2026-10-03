import { StructuredResultTable } from "@/components/chat/StructuredResultTable";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

describe("<StructuredResultTable>", () => {
	it("renders github ids from structured with no prose input", () => {
		render(
			<StructuredResultTable
				agent="github_agent"
				structured={{
					pr_numbers: [7],
					issue_numbers: [],
					commit_shas: ["a1b2c3d"],
					repo: "octo-demo/hello-world",
				}}
			/>,
		);
		expect(screen.getByText("pr_numbers")).toBeInTheDocument();
		expect(screen.getByText("7")).toBeInTheDocument();
		expect(screen.getByText("octo-demo/hello-world")).toBeInTheDocument();
		expect(screen.getByText("a1b2c3d")).toBeInTheDocument();
	});

	it("renders google ids from structured with no prose input", () => {
		render(
			<StructuredResultTable
				agent="google_agent"
				structured={{
					event_id: "evt-mock-100",
					event_ids: ["evt-mock-100"],
					calendar_status: "confirmed",
					message_id: "msg-from-draft-mock-100",
					draft_id: "draft-mock-100",
				}}
			/>,
		);
		expect(screen.getByText("evt-mock-100")).toBeInTheDocument();
		expect(screen.getByText("msg-from-draft-mock-100")).toBeInTheDocument();
		expect(screen.getByText("confirmed")).toBeInTheDocument();
	});

	it("renders the defensive fallback when structured is missing", () => {
		render(<StructuredResultTable agent="rag_agent" structured={undefined} />);
		expect(screen.getByText("no structured result")).toBeInTheDocument();
	});

	it("renders the defensive fallback when structured is empty", () => {
		render(<StructuredResultTable agent="github_agent" structured={{}} />);
		expect(screen.getByText("no structured result")).toBeInTheDocument();
	});
});
