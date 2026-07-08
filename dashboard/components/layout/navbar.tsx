"use client";

import { Menu } from "lucide-react";

import { SearchBar } from "@/components/forms/search-bar";
import { NotificationsMenu } from "@/components/navigation/notifications-menu";
import { UserMenu } from "@/components/navigation/user-menu";
import { Button } from "@/components/ui/button";
import type { NotificationItem, UserProfile } from "@/lib/mock-data";

export interface NavbarProps {
  title?: string;
  subtitle?: string;
  user: UserProfile;
  notifications: NotificationItem[];
  onMenuClick?: () => void;
  searchPlaceholder?: string;
}

export function Navbar({
  title = "Dashboard",
  subtitle = "Reusable workspace shell",
  user,
  notifications,
  onMenuClick,
  searchPlaceholder,
}: NavbarProps) {
  return (
    <header className="flex flex-col gap-4 rounded-2xl border border-glass-border glass-surface p-4 shadow-md lg:flex-row lg:items-center lg:justify-between">
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="icon" type="button" className="lg:hidden" onClick={onMenuClick}>
          <Menu className="h-4 w-4" />
        </Button>
        <div>
          <p className="text-lg font-semibold text-foreground">{title}</p>
          <p className="text-sm text-muted-foreground">{subtitle}</p>
        </div>
      </div>

      <div className="flex flex-1 flex-col gap-3 lg:max-w-xl lg:flex-row lg:items-center">
        <SearchBar placeholder={searchPlaceholder} containerClassName="flex-1" />
        <div className="flex items-center justify-end gap-2">
          <NotificationsMenu items={notifications} />
          <UserMenu user={user} />
        </div>
      </div>
    </header>
  );
}
