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
        "card-premium relative overflow-hidden rounded-[1.25rem] border border-white/8 p-0 shadow-md",
        "before:pointer-events-none before:absolute before:inset-0 before:bg-gradient-to-b before:from-primary/18 before:to-transparent",
        variant === "soft" && "bg-secondary/10 before:from-accent/10",
        className
      )}
      {...props}
    />
  );
}
