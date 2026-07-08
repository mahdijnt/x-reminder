"use client";

import * as React from "react";
import { MoreHorizontal } from "lucide-react";

import { DataTable } from "@/components/data-display/data-table";
import { SearchBar } from "@/components/forms/search-bar";
import { LoadingSkeleton } from "@/components/feedback/loading-skeleton";
import { ActionDialog } from "@/components/feedback/action-dialog";
import { StatusChip } from "@/components/feedback/status-chip";
import { StatCard } from "@/components/dashboard/stat-card";
import { SectionCard } from "@/components/dashboard/section-card";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

import { useSimulatedLoading } from "@/app/_components/use-simulated-loading";
import { PageTransition } from "@/app/_components/page-transition";

import type { TargetAchievedRow, TableColumn } from "@/lib/mock-data";
import { targetAchievedRows } from "@/lib/mock-data";

function chipFromStatus(status: TargetAchievedRow["status"]): React.ComponentProps<typeof StatusChip>["status"] {
  if (status === "Achieved") return "success";
  return "neutral";
}

export default function TargetAchievedPage() {
  const loading = useSimulatedLoading(800);
  const [query, setQuery] = React.useState("");
  const [actionMessage, setActionMessage] = React.useState<string | null>(null);

  const filteredRows = React.useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return targetAchievedRows;

    return targetAchievedRows.filter((row) => {
      return (
        row.targetName.toLowerCase().includes(q) ||
        row.handle.toLowerCase().includes(q) ||
        row.metric.toLowerCase().includes(q) ||
        row.status.toLowerCase().includes(q)
      );
    });
  }, [query]);

  const totals = React.useMemo(() => {
    const achieved = targetAchievedRows.filter((r) => r.status === "Achieved").length;
    const archived = targetAchievedRows.filter((r) => r.status === "Archived").length;
    return { achieved, archived, total: targetAchievedRows.length };
  }, []);

  const columns = React.useMemo<TableColumn<TargetAchievedRow>[]>(
    () => [
      {
        key: "targetName",
        header: "Target",
        render: (row) => (
          <div className="space-y-1">
            <p className="font-medium text-foreground">{row.targetName}</p>
            <p className="text-xs text-muted-foreground">{row.handle}</p>
          </div>
        ),
      },
      {
        key: "achievedAt",
        header: "Achieved",
        render: (row) => <span className="text-muted-foreground">{row.achievedAt}</span>,
      },
      {
        key: "metric",
        header: "Metric",
        render: (row) => (
          <span className="font-medium">
            {row.metric}
          </span>
        ),
      },
      {
        key: "status",
        header: "State",
        render: (row) => <StatusChip status={chipFromStatus(row.status)}>{row.status}</StatusChip>,
      },
      {
        key: "id",
        header: "Actions",
        align: "right",
        render: (row) => (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="icon" type="button" aria-label={`Open actions for ${row.targetName}`}>
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-[18rem]">
              {row.status === "Achieved" ? (
                <ActionDialog
                  title="Archive target"
                  description={`Archive ${row.targetName}. (Fake action)`}
                  cancelLabel="Cancel"
                  confirmLabel="Archive"
                  trigger={<DropdownMenuItem>Archive</DropdownMenuItem>}
                  onConfirm={() => setActionMessage(`Archived ${row.targetName}.`)}
                />
              ) : (
                <ActionDialog
                  title="Re-open target"
                  description={`Re-open ${row.targetName} for tracking. (Fake action)`}
                  cancelLabel="Cancel"
                  confirmLabel="Re-open"
                  trigger={<DropdownMenuItem>Re-open</DropdownMenuItem>}
                  onConfirm={() => setActionMessage(`Re-opened ${row.targetName}.`)}
                />
              )}

              <ActionDialog
                title="Mark as reviewed"
                description={`Simulate review acknowledgement for ${row.targetName}. (Fake action)`}
                cancelLabel="Cancel"
                confirmLabel="Reviewed"
                trigger={<DropdownMenuItem>Mark reviewed</DropdownMenuItem>}
                onConfirm={() => setActionMessage(`Marked reviewed: ${row.targetName}.`)}
              />

              <div className="px-2 py-1.5 text-xs text-muted-foreground">
                <Badge variant="glass">UI-only</Badge>
              </div>
            </DropdownMenuContent>
          </DropdownMenu>
        ),
      },
    ],
    []
  );

  return (
    <PageTransition>
      <div className="space-y-6">
        <div className="space-y-2">
          <h1 className="text-2xl font-semibold tracking-tight">Target Achieved</h1>
          <p className="text-sm text-muted-foreground">Review accomplishments and simulate archive/re-open actions.</p>
        </div>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          {[
            {
              title: "Achieved",
              value: String(totals.achieved),
              change: "+1",
              trend: "up" as const,
              detail: "Targets crossed threshold.",
            },
            {
              title: "Archived",
              value: String(totals.archived),
              change: "0",
              trend: "neutral" as const,
              detail: "No longer tracked.",
            },
            {
              title: "Total",
              value: String(totals.total),
              change: "+2",
              trend: "up" as const,
              detail: "All target records.",
            },
          ].map((s) => (
            <div key={s.title} className="transform-gpu transition-transform duration-300 hover:-translate-y-0.5 active:translate-y-0">
              <StatCard {...s} />
            </div>
          ))}
        </div>

        <SectionCard
          title="Achievements"
          description="Search records and manage them through dropdown dialogs."
          action={
            <div className="w-full max-w-[22rem]">
              <SearchBar value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search by target, handle, metric..." />
            </div>
          }
        >
          {loading ? (
            <div className="space-y-3">
              <LoadingSkeleton lines={7} />
              <LoadingSkeleton lines={7} />
            </div>
          ) : (
            <div className="space-y-4">
              {actionMessage ? (
                <Alert className="glass-surface">
                  <AlertTitle>Action queued</AlertTitle>
                  <AlertDescription>{actionMessage}</AlertDescription>
                </Alert>
              ) : null}

              <DataTable columns={columns} rows={filteredRows} caption="Target achievement records (fake)." />

              <p className="text-xs text-muted-foreground">
                Showing {filteredRows.length} of {targetAchievedRows.length}.
              </p>
            </div>
          )}
        </SectionCard>
      </div>
    </PageTransition>
  );
}
