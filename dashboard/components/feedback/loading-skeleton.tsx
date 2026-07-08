"use client";

import { m } from "framer-motion";

import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";

export interface LoadingSkeletonProps {
  lines?: number;
  showAvatar?: boolean;
  className?: string;
}

export function LoadingSkeleton({
  lines = 3,
  showAvatar = false,
  className,
}: LoadingSkeletonProps) {
  return (
    <m.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={cn("card-premium space-y-4 rounded-2xl p-4", className)}
    >
      <div className="flex items-center gap-3">
        {showAvatar ? <Skeleton className="h-10 w-10 rounded-full" /> : null}
        <div className="flex-1 space-y-2">
          <Skeleton className="h-4 w-1/3" />
          <Skeleton className="h-3 w-1/4" />
        </div>
      </div>
      <div className="space-y-2">
        {Array.from({ length: lines }).map((_, index) => (
          <Skeleton key={index} className={cn("h-3", index == lines - 1 ? "w-2/3" : "w-full")} style={{ animationDelay: `${index * 120}ms` }} />
        ))}
      </div>
    </m.div>
  );
}
