"use client";

import * as React from "react";
import Link from "next/link";
import { PanelLeftClose, PanelLeftOpen } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import type { NavigationItem } from "@/lib/mock-data";

export interface SidebarProps {
  items: NavigationItem[];
  title?: string;
  subtitle?: string;
  collapsed?: boolean;
  onToggleCollapse?: () => void;
  footer?: React.ReactNode;
  className?: string;
}

export function Sidebar({
  items,
  title = "Workspace",
  subtitle = "Reusable dashboard navigation",
  collapsed = false,
  onToggleCollapse,
  footer,
  className,
}: SidebarProps) {
  return (
    <aside
      className={cn(
        "flex h-full min-h-[32rem] flex-col rounded-2xl border border-glass-border glass-surface p-4 shadow-md",
        collapsed ? "w-20" : "w-72",
        className
      )}
    >
      <div className="mb-6 flex items-center justify-between gap-3">
        <div className={cn("space-y-1", collapsed && "hidden")}>
          <p className="text-sm font-semibold text-foreground">{title}</p>
          <p className="text-xs text-muted-foreground">{subtitle}</p>
        </div>
        <Button
          variant="ghost"
          size="icon"
          type="button"
          onClick={onToggleCollapse}
          aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {collapsed ? <PanelLeftOpen className="h-4 w-4" /> : <PanelLeftClose className="h-4 w-4" />}
        </Button>
      </div>

      <nav className="flex-1 space-y-2">
        {items.map((item) => (
          <Link
            key={item.title}
            href={item.href}
            className={cn(
              "flex items-center justify-between rounded-xl px-3 py-2.5 text-sm transition-colors",
              item.active
                ? "bg-primary/15 text-foreground shadow-sm"
                : "text-muted-foreground hover:bg-secondary/40 hover:text-foreground"
            )}
          >
            <span className={cn("truncate", collapsed && "sr-only")}>{item.title}</span>
            {item.badge && !collapsed ? <Badge variant="glass">{item.badge}</Badge> : null}
            {collapsed ? <span className="text-xs font-semibold">{item.title.slice(0, 1)}</span> : null}
          </Link>
        ))}
      </nav>

      {footer ? <div className="mt-6">{footer}</div> : null}
    </aside>
  );
}
