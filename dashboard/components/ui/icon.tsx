"use client";

import * as React from "react";

import { cn } from "@/lib/utils";

export type IconSize = "sm" | "md" | "lg" | "xl";

const sizeClasses: Record<IconSize, string> = {
  sm: "h-4 w-4",
  md: "h-5 w-5",
  lg: "h-6 w-6",
  xl: "h-7 w-7",
};

export interface IconProps extends React.HTMLAttributes<HTMLSpanElement> {
  size?: IconSize;
}

export function Icon({ size = "md", className, ...props }: IconProps) {
  return (
    <span
      aria-hidden="true"
      className={cn(
        "inline-flex items-center justify-center text-muted-foreground",
        sizeClasses[size],
        className
      )}
      {...props}
    />
  );
}
