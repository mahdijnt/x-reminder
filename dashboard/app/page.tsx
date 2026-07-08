"use client";

import * as React from "react";

import { BarChart, DonutChart, LineChart } from "@/components/charts";
import { DataTable } from "@/components/data-display/data-table";
import { SearchBar } from "@/components/forms/search-bar";
import { StatCard } from "@/components/dashboard/stat-card";
import { ProgressCard } from "@/components/dashboard/progress-card";
import { SectionCard } from "@/components/dashboard/section-card";
import { LoadingSkeleton } from "@/components/feedback/loading-skeleton";
import { StatusChip } from "@/components/feedback/status-chip";
import { Button } from "@/components/ui/button";
import type { SampleRow, StatDatum, TableColumn } from "@/lib/mock-data";
import {
  sampleBarChartData,
  sampleDonutChartData,
  sampleLineChartData,
  sampleProgressItems,
  sampleStats,
  sampleTableRows,
} from "@/lib/mock-data";

import { useSimulatedLoading } from "@/app/_components/use-simulated-loading";
import { PageTransition } from "@/app/_components/page-transition";

function statusChipFromRowStatus(status: SampleRow["status"]): React.ComponentProps<typeof StatusChip>["status"] {
  if (status === "Active") return "success";
  if (status === "Draft") return "warning";
  return "neutral";
}

export default function DashboardPage() {
  const loading = useSimulatedLoading(700);
  const [query, setQuery] = React.useState("");

  const filteredRows = React.useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return sampleTableRows;

    return sampleTableRows.filter((row) => {
      return (
        row.name.toLowerCase().includes(q) ||
        row.owner.toLowerCase().includes(q) ||
        row.status.toLowerCase().includes(q)
      );
    });
  }, [query]);

  const columns = React.useMemo<TableColumn<SampleRow>[]>(
    () => [
      {
        key: "name",
        header: "Account",
        render: (row) => (
          <div className="space-y-1">
            <p className="font-medium text-foreground">{row.name}</p>
            <p className="text-xs text-muted-foreground">Campaign health snapshot</p>
          </div>
        ),
      },
      {
        key: "status",
        header: "State",
        render: (row) => (
          <StatusChip status={statusChipFromRowStatus(row.status)}>
            {row.status}
          </StatusChip>
        ),
      },
      {
        key: "owner",
        header: "Owner",
        render: (row) => (
          <div className="space-y-1">
            <p className="text-sm font-medium text-foreground">{row.owner}</p>
            <p className="text-xs text-muted-foreground">Team-managed</p>
          </div>
        ),
      },
      {
        key: "amount",
        header: "Budget",
        align: "right",
        render: (row) => <span className="font-medium">{row.amount}</span>,
      },
    ],
    []
  );

  return (
    <PageTransition>
      <div className="space-y-6">
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          {sampleStats.map((s: StatDatum) => (
            <div
              key={s.title}
              className="transform-gpu transition-transform duration-300 hover:-translate-y-0.5 active:translate-y-0"
            >
              <StatCard
                title={s.title}
                value={s.value}
                change={s.change}
                detail={s.detail}
                trend={s.trend}
              />
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
          <div className="lg:col-span-2">
            <SectionCard
              title="Signal trend"
              description="Premium, presentational analytics tiles."
              action={
                <Button variant="ghost" type="button">
                  View report
                </Button>
              }
              className="glass-surface"
            >
              <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                <LineChart data={sampleLineChartData} className="h-full" />
                <BarChart data={sampleBarChartData} className="h-full" />
              </div>
              <div className="mt-4">
                <DonutChart data={sampleDonutChartData} />
              </div>
            </SectionCard>
          </div>

          <div className="space-y-4">
            {sampleProgressItems.map((p) => (
              <div
                key={p.label}
                className="transform-gpu transition-transform duration-300 hover:-translate-y-0.5 active:translate-y-0"
              >
                <ProgressCard title={p.label} value={p.value} description={p.description} label="Progress" />
              </div>
            ))}
          </div>
        </div>

        <SectionCard
          title="Recent campaigns"
          description="Searchable table with premium interactions and skeleton loading."
          action={
            <div className="w-full max-w-[22rem]">
              <SearchBar value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search campaigns..." />
            </div>
          }
        >
          {loading ? (
            <div className="space-y-3">
              <LoadingSkeleton lines={2} />
              <LoadingSkeleton lines={2} />
              <LoadingSkeleton lines={2} />
            </div>
          ) : (
            <DataTable
              columns={columns}
              rows={filteredRows}
              caption="Fake campaign records (no backend)."
            />
          )}

          <div className="mt-4 flex flex-col items-start justify-between gap-3 sm:flex-row sm:items-center">
            <p className="text-xs text-muted-foreground">Tip: try searching by owner or status.</p>
            <Button variant="outline" type="button">
              Export snapshot
            </Button>
          </div>
        </SectionCard>
      </div>
    </PageTransition>
  );
}
