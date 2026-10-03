"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";

interface SettingsStore {
	compactMode: boolean;
	showReasoning: boolean;
	toggleCompact: () => void;
	toggleReasoning: () => void;
}

export const useSettingsStore = create<SettingsStore>()(
	persist(
		(set) => ({
			compactMode: false,
			showReasoning: true,
			toggleCompact: () => set((s) => ({ compactMode: !s.compactMode })),
			toggleReasoning: () => set((s) => ({ showReasoning: !s.showReasoning })),
		}),
		{ name: "makpa-settings" },
	),
);
