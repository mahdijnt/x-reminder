"use client";

import { Menu } from "lucide-react";
import { m } from "framer-motion";

import { SearchBar } from "@/components/forms/search-bar";
import { NotificationsMenu } from "@/components/navigation/notifications-menu";
import { UserMenu } from "@/components/navigation/user-menu";
import { Button } from "@/components/ui/button";
import type { NotificationItem, UserProfile } from "@/types";

export interface NavbarProps {
  title?: string;
  subtitle?: string;
  user: UserProfile;
  notifications: NotificationItem[];
  onMenuClick?: () => void;
  searchPlaceholder?: string;
  onMarkAllNotificationsRead?: () => void;
  mobileNavOpen?: boolean;
}

export function Navbar({
  title = "Dashboard",
  subtitle = "Reusable workspace shell",
  user,
  notifications,
  onMenuClick,
  searchPlaceholder,
  onMarkAllNotificationsRead,
  mobileNavOpen = false,
}: NavbarProps) {
  return (
    <m.header
      role="banner"
      initial={{ opacity: 0, y: -16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.36, ease: [0.22, 1, 0.36, 1] }}
      className="glass-panel relative z-sticky-header flex flex-col gap-4 rounded-[1.75rem] p-4 shadow-lg lg:flex-row lg:items-center lg:justify-between"
    >
      <div className="flex min-w-0 items-center gap-3">
        <Button
          variant="ghost"
          size="icon"
          type="button"
          className="shrink-0 lg:hidden max-sm:min-h-11 max-sm:min-w-11"
          onClick={onMenuClick}
          aria-label="Open navigation menu"
          aria-expanded={mobileNavOpen}
        >
          <Menu className="h-4 w-4" />
        </Button>
        <div className="min-w-0 flex-1">
          <p className="truncate text-lg font-semibold text-foreground">{title}</p>
          <p className="line-clamp-2 text-sm text-muted-foreground sm:line-clamp-1">{subtitle}</p>
        </div>
      </div>

      <div className="flex flex-1 flex-col gap-3 lg:max-w-xl lg:flex-row lg:items-center">
        <SearchBar placeholder={searchPlaceholder} containerClassName="flex-1" />
        <div className="flex items-center justify-end gap-2">
          <NotificationsMenu items={notifications} onMarkAllRead={onMarkAllNotificationsRead} />
          <UserMenu user={user} />
        </div>
      </div>
    </m.header>
  );
}
