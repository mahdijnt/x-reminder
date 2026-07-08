"use client";

import { ChartContainer } from "@/components/ui/chart-container";
import { cn } from "@/lib/utils";
import type { ChartPoint } from "@/lib/mock-data";

export interface DonutChartProps {
  data: ChartPoint[];
  className?: string;
}

const segmentColors = ["#8b5cf6", "#06b6d4", "#22c55e", "#f59e0b", "#f43f5e"];

export function DonutChart({ data, className }: DonutChartProps) {
  const total = data.reduce((sum, item) => sum + item.value, 0) || 1;
  let offset = 0;
  const background = `conic-gradient(${data
    .map((item, index) => {
      const start = offset;
      const size = (item.value / total) * 100;
      offset += size;
      return `${segmentColors[index % segmentColors.length]} ${start}% ${offset}%`;
    })
    .join(", ")})`;

  return (
    <ChartContainer className={cn("p-4", className)}>
      <div className="mb-4">
        <p className="text-sm font-medium text-foreground">Donut Chart</p>
        <p className="text-xs text-muted-foreground">CSS conic-gradient visualization without external chart packages.</p>
      </div>
      <div className="flex flex-col items-center gap-6 lg:flex-row lg:items-center lg:justify-between">
        <div className="relative flex h-44 w-44 items-center justify-center rounded-full" style={{ background }}>
          <div className="flex h-24 w-24 items-center justify-center rounded-full bg-background/95 text-center shadow-inner">
            <div>
              <p className="text-xs text-muted-foreground">Total</p>
              <p className="text-lg font-semibold text-foreground">{total}</p>
            </div>
          </div>
        </div>
        <div className="grid w-full gap-3 lg:max-w-[14rem]">
          {data.map((item, index) => (
            <div key={item.label} className="flex items-center justify-between gap-3 rounded-xl bg-background/30 px-3 py-2">
              <div className="flex items-center gap-2">
                <span className="h-3 w-3 rounded-full" style={{ backgroundColor: segmentColors[index % segmentColors.length] }} />
                <span className="text-sm text-foreground">{item.label}</span>
              </div>
              <span className="text-sm text-muted-foreground">{item.value}%</span>
            </div>
          ))}
        </div>
      </div>
    </ChartContainer>
  );
}
