"use client";

import * as React from "react";
import { Calendar, Download, Sparkles } from "lucide-react";

import { BarChart, DonutChart, LineChart } from "@/components/charts";
import { DataTable } from "@/components/data-display/data-table";
import { SearchBar } from "@/components/forms/search-bar";
import { LoadingSkeleton } from "@/components/feedback/loading-skeleton";
import { StatCard } from "@/components/dashboard/stat-card";
import { SectionCard } from "@/components/dashboard/section-card";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

import { useSimulatedLoading } from "@/app/_components/use-simulated-loading";
import { PageTransition } from "@/components/motion/page-transition";

import type { ActiveAccountMetric, AnalyticsFilters, TableColumn, ValuableAccountMetric } from "@/types";
import { mapKpisToStats, useAnalyticsDashboard } from "@/hooks/use-api-data";
import { analyticsService } from "@/services";

function downloadPayload(filename: string, content: string, contentType: string) {
  const blob = new Blob([content], { type: contentType });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

export default function AnalyticsPage() {
  const loading = useSimulatedLoading(750);
  const [query, setQuery] = React.useState("");
  const [dateStart, setDateStart] = React.useState(() => new Date(Date.now() - 1000 * 60 * 60 * 24 * 30).toISOString().slice(0, 10));
  const [dateEnd, setDateEnd] = React.useState(() => new Date().toISOString().slice(0, 10));
  const [listType, setListType] = React.useState("");
  const [accountFilter, setAccountFilter] = React.useState("");
  const [granularity, setGranularity] = React.useState<"daily" | "weekly" | "monthly">("daily");

  const filters = React.useMemo<AnalyticsFilters>(() => ({
    start_date: dateStart,
    end_date: dateEnd,
    list_type: listType || undefined,
    account: accountFilter || undefined,
    granularity,
  }), [dateStart, dateEnd, listType, accountFilter, granularity]);

  const { data: analytics } = useAnalyticsDashboard(filters);
  const stats = mapKpisToStats(analytics.kpis);

  const activeRows = React.useMemo(() => {
    const needle = query.trim().toLowerCase();
    if (!needle) return analytics.mostActive;
    return analytics.mostActive.filter((row) => row.account.toLowerCase().includes(needle));
  }, [analytics.mostActive, query]);

  const valuableRows = React.useMemo(() => {
    const needle = query.trim().toLowerCase();
    if (!needle) return analytics.mostValuable;
    return analytics.mostValuable.filter((row) => row.account.toLowerCase().includes(needle));
  }, [analytics.mostValuable, query]);

  const activeColumns = React.useMemo<TableColumn<ActiveAccountMetric>[]>(() => [
    { key: "account", header: "Account", render: (row) => <span className="font-medium">@{row.account}</span> },
    { key: "list_type", header: "List", render: (row) => <span className="text-muted-foreground">{row.list_type}</span> },
    { key: "follows", header: "Follows" },
    { key: "follow_backs", header: "Follow backs" },
    { key: "engagements", header: "Engagements" },
  ], []);

  const valuableColumns = React.useMemo<TableColumn<ValuableAccountMetric>[]>(() => [
    { key: "account", header: "Account", render: (row) => <span className="font-medium">@{row.account}</span> },
    { key: "value_score", header: "Value score", render: (row) => row.value_score.toFixed(2) },
    { key: "avg_follow_back_time_hours", header: "Avg follow back", render: (row) => `${row.avg_follow_back_time_hours.toFixed(1)}h` },
    { key: "engagement_score", header: "Engagement score", render: (row) => row.engagement_score.toFixed(2) },
  ], []);

  async function onExport(format: "csv" | "json") {
    const payload = await analyticsService.exportReport("summary", format, filters);
    downloadPayload(payload.filename, payload.content, payload.content_type);
  }

  return (
    <PageTransition>
      <div className="space-y-6">
        <div className="space-y-2">
          <h1 className="text-2xl font-semibold tracking-tight">Analytics</h1>
          <p className="text-sm text-muted-foreground">Operational analytics powered by backend reports with mock fallback.</p>
        </div>

        <SectionCard title="Filters" description="Date range, granularity, list, and account filters.">
          <div className="grid grid-cols-1 gap-3 md:grid-cols-2 lg:grid-cols-6">
            <Input type="date" value={dateStart} onChange={(e) => setDateStart(e.target.value)} />
            <Input type="date" value={dateEnd} onChange={(e) => setDateEnd(e.target.value)} />
            <Input placeholder="List type" value={listType} onChange={(e) => setListType(e.target.value)} />
            <Input placeholder="Account" value={accountFilter} onChange={(e) => setAccountFilter(e.target.value)} />
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" type="button"><Calendar className="h-4 w-4" />{granularity}</Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                {(["daily", "weekly", "monthly"] as const).map((g) => (
                  <DropdownMenuItem key={g} onClick={() => setGranularity(g)}>{g}</DropdownMenuItem>
                ))}
              </DropdownMenuContent>
            </DropdownMenu>
            <div className="flex gap-2">
              <Button variant="outline" onClick={() => void onExport("json")}><Download className="h-4 w-4" />JSON</Button>
              <Button variant="outline" onClick={() => void onExport("csv")}><Download className="h-4 w-4" />CSV</Button>
            </div>
          </div>
        </SectionCard>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          {stats.map((s) => (
            <div key={s.title} className="transform-gpu transition-transform duration-300 hover:-translate-y-0.5 active:translate-y-0">
              <StatCard title={s.title} value={s.value} change={s.change} detail={s.detail} trend={s.trend} />
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
          <SectionCard title="Follower Growth" description="Growth series for selected filters." className="lg:col-span-2">
            <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
              <LineChart data={analytics.followerGrowth} />
              <BarChart data={analytics.engagementTimeline} />
            </div>
          </SectionCard>

          <SectionCard title="Report Mix" description="Daily / weekly / monthly report health." className="lg:col-span-1">
            <div className="flex h-full flex-col justify-between gap-4">
              <DonutChart
                data={[
                  { label: "Daily", value: analytics.reports.daily.follower_growth.length },
                  { label: "Weekly", value: analytics.reports.weekly.follower_growth.length },
                  { label: "Monthly", value: analytics.reports.monthly.follower_growth.length },
                ]}
              />
              <div className="rounded-2xl border border-glass-border bg-background/30 p-4">
                <div className="flex items-center justify-between gap-3">
                  <div className="space-y-1">
                    <p className="text-sm font-medium text-foreground">AI insight</p>
                    <p className="text-xs text-muted-foreground">Cross-period reports generated with deterministic data fallback.</p>
                  </div>
                  <Sparkles className="h-4 w-4 text-primary" />
                </div>
                <div className="mt-3 flex flex-wrap gap-2">
                  <Badge variant="glass">Follow-back trends</Badge>
                  <Badge variant="outline">Engagement shifts</Badge>
                </div>
              </div>
            </div>
          </SectionCard>
        </div>

        <SectionCard
          title="Account Rankings"
          description="Most active and most valuable accounts."
          action={<div className="w-full max-w-[22rem]"><SearchBar value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search account" /></div>}
        >
          {loading ? (
            <div className="space-y-3"><LoadingSkeleton lines={8} /><LoadingSkeleton lines={8} /></div>
          ) : (
            <div className="space-y-4">
              <DataTable columns={activeColumns} rows={activeRows} caption="Most active accounts" />
              <DataTable columns={valuableColumns} rows={valuableRows} caption="Most valuable accounts" />
            </div>
          )}
        </SectionCard>
      </div>
    </PageTransition>
  );
}
