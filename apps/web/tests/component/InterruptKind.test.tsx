import { ConfirmationModal } from "@/components/modals/ConfirmationModal";
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

const noop = vi.fn();

function payloadFor(tool: string) {
	return {
		agent: "google_agent",
		kind: tool,
		payload: { payload_preview: [{ tool, args: {} }], question: "q" },
	};
}

describe("interrupt kind titles", () => {
	it("titles calendar gates from payload tools", () => {
		render(
			<ConfirmationModal
				interrupt={payloadFor("calendar_create_event")}
				busy={false}
				onConfirm={noop}
				onCancel={noop}
				onRollback={noop}
			/>,
		);
		expect(screen.getByText("Confirm calendar event")).toBeInTheDocument();
	});

	it("titles email gates from payload tools", () => {
		render(
			<ConfirmationModal
				interrupt={payloadFor("gmail_send_message")}
				busy={false}
				onConfirm={noop}
				onCancel={noop}
				onRollback={noop}
			/>,
		);
		expect(screen.getByText("Confirm email send")).toBeInTheDocument();
	});

	it("titles github gates from payload tools", () => {
		render(
			<ConfirmationModal
				interrupt={{
					agent: "github_agent",
					kind: "github_create_issue",
					payload: {
						payload_preview: [{ tool: "github_create_issue", args: {} }],
						question: "q",
					},
				}}
				busy={false}
				onConfirm={noop}
				onCancel={noop}
				onRollback={noop}
			/>,
		);
		expect(screen.getByText("Confirm GitHub write")).toBeInTheDocument();
	});
});
