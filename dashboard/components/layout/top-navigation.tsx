"use client";

import Link from "next/link";

import { cn } from "@/lib/utils";
import type { NavigationItem } from "@/lib/mock-data";

export interface TopNavigationProps {
  items: NavigationItem[];
  className?: string;
}

export function TopNavigation({ items, className }: TopNavigationProps) {
  return (
    <nav className={cn("overflow-x-auto", className)} aria-label="Section navigation">
      <div className="inline-flex min-w-full gap-2 rounded-xl border border-glass-border bg-background/40 p-1 backdrop-blur-sm">
        {items.map((item) => (
          <Link
            key={item.title}
            href={item.href}
            className={cn(
              "rounded-lg px-4 py-2 text-sm font-medium transition-colors",
              item.active
                ? "bg-primary text-primary-foreground shadow-sm"
                : "text-muted-foreground hover:bg-secondary/60 hover:text-foreground"
            )}
          >
            {item.title}
          </Link>
        ))}
      </div>
    </nav>
  );
}
