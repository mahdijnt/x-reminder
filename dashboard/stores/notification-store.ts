import { create } from "zustand";

type NotificationUiState = {
  menuItems: import("@/types").NotificationItem[] | null;
  setMenuItems: (items: import("@/types").NotificationItem[]) => void;
  markAllReadInMenu: () => void;
};

export const useNotificationUiStore = create<NotificationUiState>((set) => ({
  menuItems: null,
  setMenuItems: (items) => set({ menuItems: items.map((n) => ({ ...n })) }),
  markAllReadInMenu: () =>
    set((state) => ({
      menuItems: state.menuItems?.map((n) => ({ ...n, unread: false })) ?? null,
    })),
}));
