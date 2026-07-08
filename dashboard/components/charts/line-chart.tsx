"use client";

import { ChartContainer } from "@/components/ui/chart-container";
import { cn } from "@/lib/utils";
import type { ChartPoint } from "@/lib/mock-data";

export interface LineChartProps {
  data: ChartPoint[];
  className?: string;
  strokeClassName?: string;
}

export function LineChart({
  data,
  className,
  strokeClassName,
}: LineChartProps) {
  const max = Math.max(...data.map((point) => point.value), 1);
  const points = data
    .map((point, index) => {
      const x = (index / Math.max(data.length - 1, 1)) * 100;
      const y = 100 - (point.value / max) * 100;
      return `${x},${y}`;
    })
    .join(" ");

  return (
    <ChartContainer className={cn("p-4", className)}>
      <div className="mb-4 flex items-end justify-between">
        <div>
          <p className="text-sm font-medium text-foreground">Line Chart</p>
          <p className="text-xs text-muted-foreground">Static SVG presentation component.</p>
        </div>
      </div>
      <div className="space-y-3">
        <svg viewBox="0 0 100 100" className="h-48 w-full overflow-visible">
          {[25, 50, 75].map((tick) => (
            <line key={tick} x1="0" y1={tick} x2="100" y2={tick} stroke="currentColor" className="text-border/60" strokeWidth="0.5" />
          ))}
          <polyline
            fill="none"
            points={points}
            className={cn("stroke-primary", strokeClassName)}
            strokeWidth="3"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          {data.map((point, index) => {
            const x = (index / Math.max(data.length - 1, 1)) * 100;
            const y = 100 - (point.value / max) * 100;
            return <circle key={point.label} cx={x} cy={y} r="2.8" className="fill-accent" />;
          })}
        </svg>
        <div className="grid grid-cols-2 gap-2 text-xs text-muted-foreground sm:grid-cols-4 lg:grid-cols-7">
          {data.map((point) => (
            <div key={point.label} className="rounded-lg bg-background/30 px-2 py-1.5 text-center">
              <p>{point.label}</p>
              <p className="font-medium text-foreground">{point.value}</p>
            </div>
          ))}
        </div>
      </div>
    </ChartContainer>
  );
}
