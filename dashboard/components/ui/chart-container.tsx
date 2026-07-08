"use client";

import * as React from "react";

import { cn } from "@/lib/utils";

export interface ChartContainerProps
  extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "glass" | "soft";
}

export function ChartContainer({
  className,
  variant = "glass",
  ...props
}: ChartContainerProps) {
  return (
    <div
      className={cn(
        "relative overflow-hidden rounded-lg border shadow-md",
        "border-glass-border bg-glass/30 backdrop-blur-sm",
        "before:pointer-events-none before:absolute before:inset-0 before:bg-gradient-to-b before:from-primary/20 before:to-transparent",
        variant === "soft" && "bg-secondary/10 before:from-accent/10",
        className
      )}
      {...props}
    />
  );
}
