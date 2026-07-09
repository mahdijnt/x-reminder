"use client";

import * as React from "react";
import { useNotificationsQuery } from "@/hooks/use-api-data";
import { useNotificationUiStore } from "@/stores/notification-store";

type NotificationProviderProps = {
  children: React.ReactNode;
};

const NotificationContext = React.createContext<{
  markAllReadInMenu: () => void;
} | null>(null);

export function useNotificationActions() {
  const ctx = React.useContext(NotificationContext);
  if (!ctx) {
    throw new Error("useNotificationActions must be used within NotificationProvider");
  }
  return ctx;
}

export function NotificationProvider({ children }: NotificationProviderProps) {
  const { data } = useNotificationsQuery();
  const setMenuItems = useNotificationUiStore((s) => s.setMenuItems);
  const markAllReadInMenu = useNotificationUiStore((s) => s.markAllReadInMenu);

  React.useEffect(() => {
    if (data) setMenuItems(data);
  }, [data, setMenuItems]);

  const value = React.useMemo(() => ({ markAllReadInMenu }), [markAllReadInMenu]);

  return <NotificationContext.Provider value={value}>{children}</NotificationContext.Provider>;
}
