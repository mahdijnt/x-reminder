"use client";

import { cn } from "@/lib/utils";

export interface GradientMeshProps {
  className?: string;
}

export function GradientMesh({ className }: GradientMeshProps) {
  return (
    <div
      aria-hidden="true"
      className={cn(
        "pointer-events-none absolute inset-0 opacity-70",
        className
      )}
    >
      <div className="absolute inset-0 gradient-mesh" />
      <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.03)_1px,transparent_1px)] bg-[size:7rem_7rem] [mask-image:radial-gradient(circle_at_center,black,transparent_90%)]" />
    </div>
  );
}
