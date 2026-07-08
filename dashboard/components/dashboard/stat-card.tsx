"use client";

import * as React from "react";
import { ArrowDownRight, ArrowUpRight, Minus } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { cn } from "@/lib/utils";

export interface StatCardProps {
  title: string;
  value: string;
  change?: string;
  detail?: string;
  trend?: "up" | "down" | "neutral";
  icon?: React.ReactNode;
}

const trendMap = {
  up: { icon: ArrowUpRight, className: "text-emerald-300 bg-emerald-500/15" },
  down: { icon: ArrowDownRight, className: "text-rose-300 bg-rose-500/15" },
  neutral: { icon: Minus, className: "text-muted-foreground bg-secondary/70" },
};

export function StatCard({
  title,
  value,
  change,
  detail,
  trend = "neutral",
  icon,
}: StatCardProps) {
  const trendConfig = trendMap[trend];
  const TrendIcon = trendConfig.icon;

  return (
    <Card className="ai-gradient overflow-hidden">
      <CardHeader className="flex flex-row items-start justify-between gap-3 space-y-0">
        <div>
          <CardDescription>{title}</CardDescription>
          <CardTitle className="mt-2 text-3xl">{value}</CardTitle>
        </div>
        <div className="rounded-xl border border-glass-border bg-background/50 p-2 text-muted-foreground">
          {icon ?? <TrendIcon className="h-5 w-5" />}
        </div>
      </CardHeader>
      <CardContent className="flex items-end justify-between gap-4">
        <div>
          {detail ? <p className="text-sm text-muted-foreground">{detail}</p> : null}
        </div>
        {change ? (
          <Badge variant="glass" className={cn("gap-1 px-2 py-1", trendConfig.className)}>
            <TrendIcon className="h-3.5 w-3.5" />
            {change}
          </Badge>
        ) : null}
      </CardContent>
    </Card>
  );
}
