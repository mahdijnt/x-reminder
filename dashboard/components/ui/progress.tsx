"use client";

import * as React from "react";
import { m } from "framer-motion";

import { cn } from "@/lib/utils";

export interface ProgressProps extends React.HTMLAttributes<HTMLDivElement> {
  value?: number;
  max?: number;
  showLabel?: boolean;
}

export const Progress = React.forwardRef<HTMLDivElement, ProgressProps>(
  ({ className, value = 0, max = 100, showLabel = false, ...props }, ref) => {
    const clampedMax = Math.max(max, 1);
    const clampedValue = Math.min(Math.max(value, 0), clampedMax);
    const percentage = Math.round((clampedValue / clampedMax) * 100);

    return (
      <div ref={ref} className={cn("space-y-2", className)} {...props}>
        {showLabel ? (
          <div className="flex items-center justify-between text-xs text-muted-foreground">
            <span>Progress</span>
            <span>{percentage}%</span>
          </div>
        ) : null}
        <div className="relative h-2.5 overflow-hidden rounded-full bg-secondary/70">
          <div className="pointer-events-none absolute inset-0 bg-[linear-gradient(90deg,transparent,rgba(255,255,255,0.18),transparent)] opacity-60" />
          <m.div
            className="h-full rounded-full bg-gradient-to-r from-primary via-violet-400 to-accent will-change-transform"
            initial={{ scaleX: 0.2, opacity: 0.5 }}
            animate={{ scaleX: percentage / 100 || 0, opacity: 1 }}
            transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
            style={{ transformOrigin: "left center" }}
          />
        </div>
      </div>
    );
  }
);
Progress.displayName = "Progress";
