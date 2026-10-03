"use client";

import type { Citation } from "@/lib/types";
import { create } from "zustand";

interface UIStore {
	sidebarCollapsed: boolean;
	citationDrawerOpen: boolean;
	selectedCitation: Citation | null;
	toggleSidebar: () => void;
	openCitation: (citation: Citation) => void;
	closeCitation: () => void;
}

export const useUIStore = create<UIStore>()((set) => ({
	sidebarCollapsed: false,
	citationDrawerOpen: false,
	selectedCitation: null,
	toggleSidebar: () => set((s) => ({ sidebarCollapsed: !s.sidebarCollapsed })),
	openCitation: (selectedCitation) =>
		set({ selectedCitation, citationDrawerOpen: true }),
	closeCitation: () =>
		set({ citationDrawerOpen: false, selectedCitation: null }),
}));
