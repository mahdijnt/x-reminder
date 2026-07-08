"use client";

import * as React from "react";

import { cn } from "@/lib/utils";

export interface StatusChipProps extends React.HTMLAttributes<HTMLSpanElement> {
  status: "success" | "warning" | "danger" | "info" | "neutral";
}

const statusStyles: Record<StatusChipProps["status"], string> = {
  success: "bg-emerald-500/15 text-emerald-300 border-emerald-500/30",
  warning: "bg-amber-500/15 text-amber-300 border-amber-500/30",
  danger: "bg-rose-500/15 text-rose-300 border-rose-500/30",
  info: "bg-sky-500/15 text-sky-300 border-sky-500/30",
  neutral: "bg-secondary/70 text-muted-foreground border-border/70",
};

export function StatusChip({ status, className, children, ...props }: StatusChipProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-2 rounded-full border px-2.5 py-1 text-xs font-medium",
        "before:h-1.5 before:w-1.5 before:rounded-full before:bg-current",
        statusStyles[status],
        className
      )}
      {...props}
    >
      {children}
    </span>
  );
}
