import { ConfirmationModal } from "@/components/modals/ConfirmationModal";
import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

const base = {
	agent: "google_agent",
	kind: "calendar_create",
	payload: { summary: "Sync", start: "2026-10-06T15:00:00Z" },
};

describe("<ConfirmationModal>", () => {
	it("traps focus in alertdialog and disables Confirm until acknowledged", () => {
		const onConfirm = vi.fn();
		render(
			<ConfirmationModal
				interrupt={base}
				busy={false}
				onConfirm={onConfirm}
				onCancel={() => undefined}
				onRollback={() => undefined}
			/>,
		);
		expect(screen.getByRole("alertdialog")).toBeInTheDocument();
		const confirm = screen.getByRole("button", { name: /confirm &/i });
		expect(confirm).toBeDisabled();
		fireEvent.click(screen.getByRole("checkbox"));
		expect(
			screen.getByRole("button", { name: /confirm &/i }),
		).not.toBeDisabled();
	});

	it("calls resume with rollback on email gate", () => {
		const onRollback = vi.fn();
		render(
			<ConfirmationModal
				interrupt={{
					agent: "google_agent",
					kind: "email_send",
					payload: { to: "a@x.com" },
				}}
				busy={false}
				onConfirm={() => undefined}
				onCancel={() => undefined}
				onRollback={onRollback}
			/>,
		);
		fireEvent.click(screen.getByRole("checkbox"));
		fireEvent.click(screen.getByRole("button", { name: /rollback/i }));
		expect(onRollback).toHaveBeenCalledOnce();
	});

	it("escapes on Cancel via Escape key", () => {
		const onCancel = vi.fn();
		render(
			<ConfirmationModal
				interrupt={base}
				busy={false}
				onConfirm={() => undefined}
				onCancel={onCancel}
				onRollback={() => undefined}
			/>,
		);
		fireEvent.keyDown(window, { key: "Escape" });
		expect(onCancel).toHaveBeenCalled();
	});
});
