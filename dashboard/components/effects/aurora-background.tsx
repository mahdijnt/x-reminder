"use client";

import { cn } from "@/lib/utils";

export interface AuroraBackgroundProps {
  className?: string;
}

export function AuroraBackground({ className }: AuroraBackgroundProps) {
  return (
    <div
      aria-hidden="true"
      className={cn(
        "pointer-events-none absolute inset-0 overflow-hidden",
        className
      )}
    >
      <div className="aurora-blob aurora-blob-primary" />
      <div className="aurora-blob aurora-blob-secondary" />
      <div className="aurora-blob aurora-blob-tertiary" />
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,rgba(255,255,255,0.10),transparent_30%),radial-gradient(circle_at_bottom,rgba(59,130,246,0.12),transparent_28%)]" />
    </div>
  );
}
