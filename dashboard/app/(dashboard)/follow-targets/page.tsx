"use client";

import * as React from "react";
import { MoreHorizontal } from "lucide-react";

import { DataTable } from "@/components/data-display/data-table";
import { SearchBar } from "@/components/forms/search-bar";
import { LoadingSkeleton } from "@/components/feedback/loading-skeleton";
import { StatusChip } from "@/components/feedback/status-chip";
import { ActionDialog } from "@/components/feedback/action-dialog";
import { StatCard } from "@/components/dashboard/stat-card";
import { SectionCard } from "@/components/dashboard/section-card";

import { Progress } from "@/components/ui/progress";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

import { useSimulatedLoading } from "@/app/_components/use-simulated-loading";
import { PageTransition } from "@/components/motion/page-transition";

import type { FollowTargetRow, TableColumn } from "@/types";
import { useFollowTargets } from "@/hooks/use-api-data";

function chipFromTargetStatus(status: FollowTargetRow["status"]): React.ComponentProps<typeof StatusChip>["status"] {
  if (status === "Qualified") return "success";
  if (status === "Review") return "warning";
  return "neutral";
}

export default function FollowTargetsPage() {
  const { data: followTargetRows } = useFollowTargets();
  const loading = useSimulatedLoading(750);
  const [query, setQuery] = React.useState("");
  const [actionMessage, setActionMessage] = React.useState<string | null>(null);

  const filteredRows = React.useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return followTargetRows;

    return followTargetRows.filter((row) => {
      return (
        row.name.toLowerCase().includes(q) ||
        row.handle.toLowerCase().includes(q) ||
        row.strategy.toLowerCase().includes(q) ||
        row.status.toLowerCase().includes(q)
      );
    });
  }, [query, followTargetRows]);

  const totals = React.useMemo(() => {
    const qualified = followTargetRows.filter((r) => r.status === "Qualified").length;
    const review = followTargetRows.filter((r) => r.status === "Review").length;
    const scheduled = followTargetRows.filter((r) => r.status === "Scheduled").length;
    return { qualified, review, scheduled, total: followTargetRows.length };
  }, []);

  const columns = React.useMemo<TableColumn<FollowTargetRow>[]>(
    () => [
      {
        key: "name",
        header: "Target",
        render: (row) => (
          <div className="space-y-1">
            <p className="font-medium text-foreground">{row.name}</p>
            <p className="text-xs text-muted-foreground">{row.handle}</p>
          </div>
        ),
      },
      {
        key: "matchScore",
        header: "Match",
        render: (row) => (
          <div className="space-y-2">
            <Progress value={row.matchScore} max={100} showLabel className="py-0" />
          </div>
        ),
      },
      {
        key: "strategy",
        header: "Strategy",
        render: (row) => (
          <span className="inline-flex items-center rounded-full border border-border/70 bg-background/30 px-2.5 py-1 text-xs font-medium text-foreground">
            {row.strategy}
          </span>
        ),
      },
      {
        key: "status",
        header: "State",
        render: (row) => (
          <StatusChip status={chipFromTargetStatus(row.status)}>{row.status}</StatusChip>
        ),
      },
      {
        key: "id",
        header: "Actions",
        align: "right",
        render: (row) => (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="icon" type="button" aria-label={`Open actions for ${row.name}`}>
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-[18rem]">
              <ActionDialog
                title={row.status === "Scheduled" ? "Run scheduled follow" : "Start following"}
                description={`Simulate a follow action for ${row.handle}. (Fake action)`}
                cancelLabel="Cancel"
                confirmLabel={row.status === "Scheduled" ? "Run now" : "Follow"}
                trigger={<DropdownMenuItem>Start following</DropdownMenuItem>}
                onConfirm={() => setActionMessage(`Queued follow for ${row.handle}.`)}
              />

              {row.status !== "Scheduled" ? (
                <ActionDialog
                  title="Schedule follow"
                  description={`Schedule ${row.handle} for follow on the next run. (Fake action)`}
                  cancelLabel="Cancel"
                  confirmLabel="Schedule"
                  trigger={<DropdownMenuItem>Schedule follow</DropdownMenuItem>}
                  onConfirm={() => setActionMessage(`Scheduled follow for ${row.handle}.`)}
                />
              ) : null}

              <ActionDialog
                title="Remove target"
                description={`Remove ${row.handle} from follow targets. (Fake action)`}
                cancelLabel="Cancel"
                confirmLabel="Remove"
                trigger={<DropdownMenuItem>Remove</DropdownMenuItem>}
                onConfirm={() => setActionMessage(`Removed ${row.handle} from follow targets.`)}
              />

              <div className="px-2 py-1.5 text-xs text-muted-foreground">Simulated follow workflows.</div>
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
          <h1 className="text-2xl font-semibold tracking-tight">Follow Targets</h1>
          <p className="text-sm text-muted-foreground">Manage qualified accounts and simulate follow execution.</p>
        </div>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          {[
            {
              title: "Total targets",
              value: String(totals.total),
              change: "+5",
              trend: "up" as const,
              detail: "Accounts available for follow workflows.",
            },
            {
              title: "Qualified",
              value: String(totals.qualified),
              change: "+2",
              trend: "up" as const,
              detail: "High match score candidates.",
            },
            {
              title: "Scheduled",
              value: String(totals.scheduled),
              change: "0",
              trend: "neutral" as const,
              detail: "Queued for the next follow run.",
            },
          ].map((s) => (
            <div
              key={s.title}
              className="transform-gpu transition-transform duration-300 hover:-translate-y-0.5 active:translate-y-0"
            >
              <StatCard {...s} />
            </div>
          ))}
        </div>

        <SectionCard
          title="Targets queue"
          description="Search in-memory targets and open action dialogs from the dropdown menu."
          action={
            <div className="w-full max-w-[22rem]">
              <SearchBar value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search by name, handle, strategy, status..." />
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

              <DataTable
                columns={columns}
                rows={filteredRows}
                caption="Follow targets (fake data)."
              />

              <p className="text-xs text-muted-foreground">
                Showing {filteredRows.length} of {followTargetRows.length}.
              </p>
            </div>
          )}
        </SectionCard>
      </div>
    </PageTransition>
  );
}
