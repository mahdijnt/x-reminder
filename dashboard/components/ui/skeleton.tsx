"use client";

import * as React from "react";

import { cn } from "@/lib/utils";

export const Skeleton = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, style, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("skeleton-shimmer rounded-md", className)}
    style={style}
    {...props}
  />
));
Skeleton.displayName = "Skeleton";
