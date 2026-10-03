import { CitationChips } from "@/components/chat/CitationChips";
import { useUIStore } from "@/lib/stores/ui";
import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

describe("<CitationChips>", () => {
	it("opens the drawer with the correct source and page", () => {
		render(<CitationChips citations={[{ source: "sample.pdf", page: 7 }]} />);
		fireEvent.click(screen.getByRole("button", { name: /sample\.pdf/ }));
		const state = useUIStore.getState();
		expect(state.citationDrawerOpen).toBe(true);
		expect(state.selectedCitation?.page).toBe(7);
		state.closeCitation();
	});

	it("renders nothing without citations", () => {
		const { container } = render(<CitationChips citations={[]} />);
		expect(container.textContent).toBe("");
	});
});
