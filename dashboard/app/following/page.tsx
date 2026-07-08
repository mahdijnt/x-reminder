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

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

import { useSimulatedLoading } from "@/app/_components/use-simulated-loading";
import { PageTransition } from "@/app/_components/page-transition";

import type { FollowingRow, TableColumn } from "@/lib/mock-data";
import { followingRows } from "@/lib/mock-data";

function chipFromNotificationState(state: FollowingRow["notificationState"]): React.ComponentProps<typeof StatusChip>["status"] {
  if (state === "Enabled") return "info";
  if (state === "Pending") return "warning";
  return "neutral";
}

export default function FollowingPage() {
  const loading = useSimulatedLoading(750);
  const [query, setQuery] = React.useState("");
  const [actionMessage, setActionMessage] = React.useState<string | null>(null);

  const filteredRows = React.useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return followingRows;

    return followingRows.filter((row) => {
      return (
        row.name.toLowerCase().includes(q) ||
        row.handle.toLowerCase().includes(q) ||
        row.since.toLowerCase().includes(q) ||
        row.notificationState.toLowerCase().includes(q) ||
        row.engagement.toLowerCase().includes(q)
      );
    });
  }, [query]);

  const totals = React.useMemo(() => {
    const enabled = followingRows.filter((r) => r.notificationState === "Enabled").length;
    const pending = followingRows.filter((r) => r.notificationState === "Pending").length;
    const muted = followingRows.filter((r) => r.notificationState === "Muted").length;
    return { enabled, pending, muted, total: followingRows.length };
  }, []);

  const columns = React.useMemo<TableColumn<FollowingRow>[]>(
    () => [
      {
        key: "name",
        header: "Account",
        render: (row) => (
          <div className="space-y-1">
            <p className="font-medium text-foreground">{row.name}</p>
            <p className="text-xs text-muted-foreground">{row.handle}</p>
          </div>
        ),
      },
      {
        key: "since",
        header: "Since",
        render: (row) => <span className="text-muted-foreground">{row.since}</span>,
      },
      {
        key: "notificationState",
        header: "Notifications",
        render: (row) => (
          <StatusChip status={chipFromNotificationState(row.notificationState)}>
            {row.notificationState}
          </StatusChip>
        ),
      },
      {
        key: "engagement",
        header: "Engagement",
        render: (row) => <span className="font-medium">{row.engagement}</span>,
      },
      {
        key: "id",
        header: "Actions",
        align: "right",
        render: (row) => (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="outline"
                size="icon"
                type="button"
                aria-label={`Open actions for ${row.name}`}
              >
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-[17rem]">
              {row.notificationState === "Enabled" ? (
                <ActionDialog
                  title="Mute notifications"
                  description={`Mute engagement notifications for ${row.handle}. (Fake action)`}
                  cancelLabel="Cancel"
                  confirmLabel="Mute"
                  trigger={<DropdownMenuItem>Mute notifications</DropdownMenuItem>}
                  onConfirm={() => setActionMessage(`Muted notifications for ${row.handle}.`)}
                />
              ) : (
                <ActionDialog
                  title="Enable notifications"
                  description={`Enable engagement notifications for ${row.handle}. (Fake action)`}
                  cancelLabel="Cancel"
                  confirmLabel="Enable"
                  trigger={<DropdownMenuItem>Enable notifications</DropdownMenuItem>}
                  onConfirm={() => setActionMessage(`Enabled notifications for ${row.handle}.`)}
                />
              )}

              <ActionDialog
                title="Unfollow"
                description={`Stop following ${row.handle}. (Fake action)`}
                cancelLabel="Cancel"
                confirmLabel="Unfollow"
                trigger={<DropdownMenuItem>Unfollow</DropdownMenuItem>}
                onConfirm={() => setActionMessage(`Unfollowed ${row.handle}.`)}
              />

              <div className="px-2 py-1.5 text-xs text-muted-foreground">Actions only affect UI state.</div>
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
          <h1 className="text-2xl font-semibold tracking-tight">Following</h1>
          <p className="text-sm text-muted-foreground">Search followed accounts, tune notification behavior, and confirm actions.</p>
        </div>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          {[
            {
              title: "Total following",
              value: String(totals.total),
              change: "+1",
              trend: "up" as const,
              detail: "Accounts currently followed.",
            },
            {
              title: "Enabled notifications",
              value: String(totals.enabled),
              change: "+3",
              trend: "up" as const,
              detail: "Signals pushed to your feed.",
            },
            {
              title: "Muted accounts",
              value: String(totals.muted),
              change: "-1",
              trend: "neutral" as const,
              detail: "Quiet mode for lower-priority accounts.",
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
          title="Followed accounts"
          description="Pure UI: notifications + follow actions are simulated."
          action={
            <div className="w-full max-w-[22rem]">
              <SearchBar value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search by name, handle, engagement..." />
            </div>
          }
        >
          {loading ? (
            <div className="space-y-3">
              <LoadingSkeleton lines={6} />
              <LoadingSkeleton lines={6} />
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
                caption="Followed account records (no backend)."
              />

              <p className="text-xs text-muted-foreground">
                Showing {filteredRows.length} of {followingRows.length}.
              </p>
            </div>
          )}
        </SectionCard>
      </div>
    </PageTransition>
  );
}
