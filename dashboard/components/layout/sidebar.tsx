"use client";

import * as React from "react";
import Link from "next/link";
import { PanelLeftClose, PanelLeftOpen } from "lucide-react";
import { m } from "framer-motion";

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
    <m.aside
      layout
      transition={{ type: "spring", stiffness: 240, damping: 26, mass: 0.8 }}
      className={cn(
        "glass-panel flex h-full min-h-[32rem] flex-col overflow-hidden rounded-[1.75rem] p-4 shadow-lg",
        collapsed ? "w-20" : "w-full",
        className
      )}
    >
      <div className="mb-6 flex items-center justify-between gap-3">
        <m.div
          animate={{ opacity: collapsed ? 0 : 1, y: collapsed ? -4 : 0 }}
          transition={{ duration: 0.2 }}
          className={cn("space-y-1", collapsed && "pointer-events-none")}
        >
          <p className={cn("text-sm font-semibold text-foreground", collapsed && "sr-only")}>{title}</p>
          <p className={cn("text-xs text-muted-foreground", collapsed && "sr-only")}>{subtitle}</p>
        </m.div>
        <Button
          variant="ghost"
          size="icon"
          type="button"
          onClick={onToggleCollapse}
          aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
          className="border border-white/8 bg-white/5 transition-all duration-300 hover:bg-white/10"
        >
          <m.span
            animate={{ rotate: collapsed ? 180 : 0 }}
            transition={{ duration: 0.28, ease: "easeOut" }}
            className="inline-flex"
          >
            {collapsed ? <PanelLeftOpen className="h-4 w-4" /> : <PanelLeftClose className="h-4 w-4" />}
          </m.span>
        </Button>
      </div>

      <nav className="flex-1 space-y-2">
        {items.map((item, index) => (
          <m.div
            key={item.title}
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.04 * index, duration: 0.28 }}
          >
            <Link
              href={item.href}
              className={cn(
                "group relative flex items-center justify-between overflow-hidden rounded-xl px-3 py-2.5 text-sm transition-all duration-300",
                item.active
                  ? "bg-primary/16 text-foreground shadow-[inset_0_1px_0_rgba(255,255,255,0.12),0_14px_30px_-24px_rgba(59,130,246,0.9)]"
                  : "text-muted-foreground hover:bg-white/7 hover:text-foreground"
              )}
            >
              <span className="pointer-events-none absolute inset-y-0 left-0 w-10 bg-gradient-to-r from-white/10 to-transparent opacity-0 transition-opacity duration-300 group-hover:opacity-100" />
              <span className={cn("truncate", collapsed && "sr-only")}>{item.title}</span>
              {item.badge && !collapsed ? <Badge variant="glass">{item.badge}</Badge> : null}
              {collapsed ? <span className="text-xs font-semibold text-primary-foreground/90">{item.title.slice(0, 1)}</span> : null}
            </Link>
          </m.div>
        ))}
      </nav>

      {footer ? <div className="mt-6">{footer}</div> : null}
    </m.aside>
  );
}
