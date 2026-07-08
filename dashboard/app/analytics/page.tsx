"use client";

import * as React from "react";
import { Calendar, Sparkles } from "lucide-react";

import { BarChart, DonutChart, LineChart } from "@/components/charts";
import { DataTable } from "@/components/data-display/data-table";
import { SearchBar } from "@/components/forms/search-bar";
import { LoadingSkeleton } from "@/components/feedback/loading-skeleton";
import { StatusChip } from "@/components/feedback/status-chip";
import { StatCard } from "@/components/dashboard/stat-card";
import { SectionCard } from "@/components/dashboard/section-card";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

import { useSimulatedLoading } from "@/app/_components/use-simulated-loading";
import { PageTransition } from "@/app/_components/page-transition";

import type { AnalyticsTweetRow, TableColumn } from "@/lib/mock-data";
import {
  analyticsTopTweetRows,
  sampleBarChartData,
  sampleDonutChartData,
  sampleLineChartData,
  sampleStats,
} from "@/lib/mock-data";

function chipFromTweetState(state: AnalyticsTweetRow["state"]): React.ComponentProps<typeof StatusChip>["status"] {
  if (state === "High") return "success";
  if (state === "Medium") return "warning";
  return "neutral";
}

export default function AnalyticsPage() {
  const loading = useSimulatedLoading(750);
  const [query, setQuery] = React.useState("");
  const [range, setRange] = React.useState<"7d" | "30d" | "90d">("30d");

  const filteredTweets = React.useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return analyticsTopTweetRows;

    return analyticsTopTweetRows.filter((row) => {
      return (
        row.tweet.toLowerCase().includes(q) ||
        row.metric.toLowerCase().includes(q) ||
        row.impact.toLowerCase().includes(q) ||
        row.state.toLowerCase().includes(q)
      );
    });
  }, [query]);

  const columns = React.useMemo<TableColumn<AnalyticsTweetRow>[]>(
    () => [
      {
        key: "tweet",
        header: "Post",
        render: (row) => (
          <div className="space-y-1">
            <p className="font-medium text-foreground">{row.tweet}</p>
            <p className="text-xs text-muted-foreground">{range} snapshot</p>
          </div>
        ),
      },
      {
        key: "metric",
        header: "Metric",
        render: (row) => <span className="font-medium">{row.metric}</span>,
      },
      {
        key: "impact",
        header: "Impact",
        render: (row) => <span className="text-muted-foreground">{row.impact}</span>,
      },
      {
        key: "state",
        header: "Priority",
        render: (row) => <StatusChip status={chipFromTweetState(row.state)}>{row.state}</StatusChip>,
      },
    ],
    [range]
  );

  return (
    <PageTransition>
      <div className="space-y-6">
        <div className="space-y-2">
          <h1 className="text-2xl font-semibold tracking-tight">Analytics</h1>
          <p className="text-sm text-muted-foreground">Premium chart tiles and a searchable “top posts” table.</p>
        </div>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          {sampleStats.map((s) => (
            <div
              key={s.title}
              className="transform-gpu transition-transform duration-300 hover:-translate-y-0.5 active:translate-y-0"
            >
              <StatCard title={s.title} value={s.value} change={s.change} detail={s.detail} trend={s.trend} />
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
          <SectionCard
            title="Trend line"
            description="Smooth, presentational SVG chart."
            action={
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline" type="button">
                    <Calendar className="h-4 w-4" />
                    {range}
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  {(["7d", "30d", "90d"] as const).map((r) => (
                    <DropdownMenuItem key={r} onClick={() => setRange(r)}>
                      {r}
                    </DropdownMenuItem>
                  ))}
                </DropdownMenuContent>
              </DropdownMenu>
            }
            className="lg:col-span-2"
          >
            <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
              <LineChart data={sampleLineChartData} />
              <BarChart data={sampleBarChartData} />
            </div>
          </SectionCard>

          <SectionCard title="Mix" description="Distribution visualization." className="lg:col-span-1">
            <div className="flex h-full flex-col justify-between gap-4">
              <DonutChart data={sampleDonutChartData} />
              <div className="rounded-2xl border border-glass-border bg-background/30 p-4">
                <div className="flex items-center justify-between gap-3">
                  <div className="space-y-1">
                    <p className="text-sm font-medium text-foreground">AI insight</p>
                    <p className="text-xs text-muted-foreground">Simulated recommendation engine.</p>
                  </div>
                  <Sparkles className="h-4 w-4 text-primary" />
                </div>
                <div className="mt-3 flex flex-wrap gap-2">
                  <Badge variant="glass">Reduce noise</Badge>
                  <Badge variant="outline">Boost winners</Badge>
                </div>
              </div>
            </div>
          </SectionCard>
        </div>

        <SectionCard
          title="Top posts"
          description="Search, prioritize, and simulate filtering (no backend)."
          action={
            <div className="w-full max-w-[22rem]">
              <SearchBar value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search by tweet text, metric, impact..." />
            </div>
          }
        >
          {loading ? (
            <div className="space-y-3">
              <LoadingSkeleton lines={8} />
              <LoadingSkeleton lines={8} />
            </div>
          ) : (
            <div className="space-y-4">
              <DataTable
                columns={columns}
                rows={filteredTweets}
                caption="Top posts (fake)."
              />
              <p className="text-xs text-muted-foreground">
                Showing {filteredTweets.length} of {analyticsTopTweetRows.length}.
              </p>
            </div>
          )}
        </SectionCard>
      </div>
    </PageTransition>
  );
}
