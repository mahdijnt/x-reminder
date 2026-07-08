"use client";

import * as React from "react";

import { AuroraBackground } from "@/components/effects/aurora-background";
import { GradientMesh } from "@/components/effects/gradient-mesh";
import { cn } from "@/lib/utils";

export function AuthLayoutShell({
  children,
  title,
  subtitle,
  className,
}: {
  children: React.ReactNode;
  title: string;
  subtitle?: string;
  className?: string;
}) {
  return (
    <div className={cn("relative isolate min-h-screen overflow-x-hidden", className)}>
      <AuroraBackground className="z-aurora" />
      <GradientMesh className="z-aurora opacity-60" />
      <div className="pointer-events-none absolute inset-0 z-aurora bg-[radial-gradient(circle_at_top,rgba(8,12,28,0.2),transparent_30%),linear-gradient(180deg,rgba(7,10,20,0.2),rgba(7,10,20,0.55))]" />
      <div className="relative z-page-content mx-auto flex min-h-screen w-full max-w-md flex-col justify-center px-4 py-10">
        <div className="mb-8 space-y-2 text-center">
          <p className="text-sm font-medium uppercase tracking-[0.2em] text-primary/80">X Reminder</p>
          <h1 className="text-2xl font-semibold text-foreground">{title}</h1>
          {subtitle ? <p className="text-sm text-muted-foreground">{subtitle}</p> : null}
        </div>
        <div className="card-premium rounded-[1.5rem] p-6 shadow-glow">{children}</div>
      </div>
    </div>
  );
}
