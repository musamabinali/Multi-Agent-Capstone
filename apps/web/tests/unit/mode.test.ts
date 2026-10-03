import { describe, expect, it } from "vitest";

function toneForMode(mode: string): string {
	return mode === "live" ? "live" : mode === "free" ? "free" : "demo";
}

describe("mode resolver", () => {
	it("maps demo/free/live to pill tones", () => {
		expect(toneForMode("demo")).toBe("demo");
		expect(toneForMode("free")).toBe("free");
		expect(toneForMode("live")).toBe("live");
	});

	it("falls back to demo for unknown modes", () => {
		expect(toneForMode("whatever")).toBe("demo");
	});
});
