import { DowngradeBanner } from "@/components/shell/DowngradeBanner";
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

describe("<DowngradeBanner>", () => {
	it("renders every downgrade combination", () => {
		render(
			<DowngradeBanner
				mode="free"
				downgrades={[
					"GitHub PAT missing — using mock GitHub MCP server",
					"Google OAuth missing — using mock Google MCP server",
				]}
			/>,
		);
		expect(screen.getByText(/running in free mode/i)).toBeInTheDocument();
		expect(screen.getByText(/mock github/i)).toBeInTheDocument();
		expect(screen.getByText(/mock google/i)).toBeInTheDocument();
	});

	it("renders nothing when clean", () => {
		const { container } = render(
			<DowngradeBanner mode="live" downgrades={[]} />,
		);
		expect(container.textContent).toBe("");
	});
});
