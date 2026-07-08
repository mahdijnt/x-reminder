"use client";

import { ChartContainer } from "@/components/ui/chart-container";
import { cn } from "@/lib/utils";
import type { ChartPoint } from "@/lib/mock-data";

export interface BarChartProps {
  data: ChartPoint[];
  className?: string;
}

export function BarChart({ data, className }: BarChartProps) {
  const max = Math.max(...data.map((point) => point.value), 1);

  return (
    <ChartContainer className={cn("p-4", className)} variant="soft">
      <div className="mb-4">
        <p className="text-sm font-medium text-foreground">Bar Chart</p>
        <p className="text-xs text-muted-foreground">Token-based columns built with div elements.</p>
      </div>
      <div className="flex h-56 items-end gap-3">
        {data.map((point) => (
          <div key={point.label} className="flex flex-1 flex-col items-center gap-3">
            <div className="text-xs font-medium text-foreground">{point.value}</div>
            <div className="flex h-full w-full items-end rounded-xl bg-secondary/30 p-1">
              <div
                className="w-full rounded-lg bg-gradient-to-t from-primary via-primary to-accent"
                style={{ height: `${(point.value / max) * 100}%` }}
              />
            </div>
            <div className="text-xs text-muted-foreground">{point.label}</div>
          </div>
        ))}
      </div>
    </ChartContainer>
  );
}
