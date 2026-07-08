"use client";

import { Bell, CheckCheck } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { cn } from "@/lib/utils";
import type { NotificationItem } from "@/lib/mock-data";

export interface NotificationsMenuProps {
  items: NotificationItem[];
  onMarkAllRead?: () => void;
}

const toneClasses: Record<NonNullable<NotificationItem["tone"]>, string> = {
  default: "bg-primary/20 text-primary",
  success: "bg-emerald-500/20 text-emerald-300",
  warning: "bg-amber-500/20 text-amber-300",
  danger: "bg-rose-500/20 text-rose-300",
};

export function NotificationsMenu({ items, onMarkAllRead }: NotificationsMenuProps) {
  const unreadCount = items.filter((item) => item.unread).length;

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" size="icon" type="button" className="relative rounded-full">
          <Bell className="h-4 w-4" />
          {unreadCount > 0 ? (
            <span className="absolute right-2 top-2 h-2 w-2 rounded-full bg-primary" />
          ) : null}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-[22rem]">
        <DropdownMenuLabel className="flex items-center justify-between gap-3">
          <span>Notifications</span>
          <button
            type="button"
            className="text-xs font-medium text-primary transition-colors hover:text-primary/80"
            onClick={onMarkAllRead}
          >
            <span className="inline-flex items-center gap-1">
              <CheckCheck className="h-3.5 w-3.5" />
              Mark all read
            </span>
          </button>
        </DropdownMenuLabel>
        <DropdownMenuSeparator />
        <div className="space-y-1">
          {items.map((item) => (
            <DropdownMenuItem key={item.id} className="items-start gap-3 whitespace-normal">
              <span className={cn("mt-1.5 h-2.5 w-2.5 shrink-0 rounded-full", toneClasses[item.tone ?? "default"])} />
              <div className="flex-1 space-y-1 text-left">
                <div className="flex items-center gap-2">
                  <p className="font-medium text-foreground">{item.title}</p>
                  {item.unread ? <Badge variant="glass">New</Badge> : null}
                </div>
                <p className="text-xs text-muted-foreground">{item.description}</p>
                <p className="text-xs text-muted-foreground/80">{item.time}</p>
              </div>
            </DropdownMenuItem>
          ))}
        </div>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
