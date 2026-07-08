"use client";

import Link from "next/link";
import { m } from "framer-motion";

import { cn } from "@/lib/utils";
import type { NavigationItem } from "@/lib/mock-data";

export interface TopNavigationProps {
  items: NavigationItem[];
  className?: string;
}

export function TopNavigation({ items, className }: TopNavigationProps) {
  return (
    <m.nav
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.36, delay: 0.08, ease: [0.22, 1, 0.36, 1] }}
      className={cn("overflow-x-auto", className)}
      aria-label="Section navigation"
    >
      <div className="glass-panel inline-flex min-w-full gap-2 rounded-2xl p-1.5">
        {items.map((item) => (
          <Link
            key={item.title}
            href={item.href}
            className={cn(
              "rounded-xl px-4 py-2 text-sm font-medium transition-all duration-300",
              item.active
                ? "bg-primary text-primary-foreground shadow-[0_12px_28px_-20px_rgba(124,58,237,0.95)]"
                : "text-muted-foreground hover:bg-white/8 hover:text-foreground"
            )}
          >
            {item.title}
          </Link>
        ))}
      </div>
    </m.nav>
  );
}
