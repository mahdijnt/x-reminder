"use client";

import * as React from "react";

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
        <div className="h-2.5 overflow-hidden rounded-full bg-secondary/70">
          <div
            className="h-full rounded-full bg-gradient-to-r from-primary to-accent transition-[width] duration-300"
            style={{ width: `${percentage}%` }}
          />
        </div>
      </div>
    );
  }
);
Progress.displayName = "Progress";
