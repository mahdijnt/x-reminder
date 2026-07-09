import { create } from "zustand";

export type ThemePreference = "dark" | "light" | "system";

type UiState = {
  sidebarCollapsedPreference: boolean;
  themePreference: ThemePreference;
  setSidebarCollapsedPreference: (value: boolean) => void;
  setThemePreference: (value: ThemePreference) => void;
};

/**
 * Zustand does not require a React provider.
 * Import `useUiStore` in client components for UI preferences.
 */
export const useUiStore = create<UiState>((set) => ({
  sidebarCollapsedPreference: false,
  themePreference: "dark",
  setSidebarCollapsedPreference: (value) => set({ sidebarCollapsedPreference: value }),
  setThemePreference: (value) => set({ themePreference: value }),
}));
