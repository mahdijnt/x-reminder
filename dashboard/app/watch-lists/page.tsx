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
import type { TableColumn, WatchListRow } from "@/lib/mock-data";
import { watchListRows } from "@/lib/mock-data";

function statusChipFromWatchList(status: WatchListRow["status"]): React.ComponentProps<typeof StatusChip>["status"] {
  if (status === "Active") return "success";
  if (status === "Draft") return "warning";
  return "neutral";
}

export default function WatchListsPage() {
  const loading = useSimulatedLoading(750);
  const [query, setQuery] = React.useState("");
  const [actionMessage, setActionMessage] = React.useState<string | null>(null);

  const filteredRows = React.useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return watchListRows;

    return watchListRows.filter((row) => {
      return (
        row.name.toLowerCase().includes(q) ||
        row.handle.toLowerCase().includes(q) ||
        row.owner.toLowerCase().includes(q) ||
        row.status.toLowerCase().includes(q) ||
        row.signals.toLowerCase().includes(q)
      );
    });
  }, [query]);

  const totals = React.useMemo(() => {
    const active = watchListRows.filter((r) => r.status === "Active").length;
    const draft = watchListRows.filter((r) => r.status === "Draft").length;
    const paused = watchListRows.filter((r) => r.status === "Paused").length;
    return { active, draft, paused, total: watchListRows.length };
  }, []);

  const columns = React.useMemo<TableColumn<WatchListRow>[]>(
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
        key: "status",
        header: "State",
        render: (row) => (
          <StatusChip status={statusChipFromWatchList(row.status)}>
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
            <p className="text-xs text-muted-foreground">Managed</p>
          </div>
        ),
      },
      {
        key: "signals",
        header: "Signals",
        render: (row) => <span className="font-medium">{row.signals}</span>,
      },
      {
        key: "lastCheck",
        header: "Last check",
        align: "right",
        render: (row) => <span className="text-muted-foreground">{row.lastCheck}</span>,
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
                className="border-input bg-background/40 hover:bg-secondary/40"
              >
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-[16rem]">
              <ActionDialog
                title="Add to Following"
                description={`Queue a follow request for ${row.handle}. (Fake action)`}
                cancelLabel="Not now"
                confirmLabel="Add"
                trigger={<DropdownMenuItem>Add to Following</DropdownMenuItem>}
                onConfirm={() => setActionMessage(`Queued follow for ${row.handle}.`)}
              />

              {row.status === "Active" ? (
                <ActionDialog
                  title="Pause watch"
                  description={`Pause monitoring for ${row.handle}. (Fake action)`}
                  cancelLabel="Cancel"
                  confirmLabel="Pause"
                  trigger={<DropdownMenuItem>Pause</DropdownMenuItem>}
                  onConfirm={() => setActionMessage(`Paused monitoring for ${row.handle}.`)}
                />
              ) : (
                <ActionDialog
                  title="Resume watch"
                  description={`Resume monitoring for ${row.handle}. (Fake action)`}
                  cancelLabel="Cancel"
                  confirmLabel="Resume"
                  trigger={<DropdownMenuItem>Resume</DropdownMenuItem>}
                  onConfirm={() => setActionMessage(`Resumed monitoring for ${row.handle}.`)}
                />
              )}

              <ActionDialog
                title="Remove from list"
                description={`Remove ${row.handle} from your watch list. (Fake action)`}
                cancelLabel="Cancel"
                confirmLabel="Remove"
                trigger={<DropdownMenuItem className="text-danger">Remove</DropdownMenuItem>}
                onConfirm={() => setActionMessage(`Removed ${row.handle} from watch lists.`)}
              />

              <div className="px-2 py-1.5">
                <Badge variant="glass">No backend</Badge>
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
          <h1 className="text-2xl font-semibold tracking-tight">Watch Lists</h1>
          <p className="text-sm text-muted-foreground">
            Track accounts and simulate follow/paused workflows with premium UI states.
          </p>
        </div>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          {[
            {
              title: "Total watched",
              value: String(totals.total),
              change: "+2",
              trend: "up" as const,
              detail: "Accounts under monitoring.",
            },
            {
              title: "Active now",
              value: String(totals.active),
              change: "+1",
              trend: "up" as const,
              detail: "Optimized for highest signal quality.",
            },
            {
              title: "Paused",
              value: String(totals.paused),
              change: "-1",
              trend: "neutral" as const,
              detail: "Temporarily excluded from checks.",
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
          title="Watched accounts"
          description="Search, filter in-memory, and manage entries with fake dialogs."
          action={
            <div className="w-full max-w-[22rem]">
              <SearchBar value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search by name, handle, status..." />
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
                caption="Watch list records (pure UI; no network)."
              />

              <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                <p className="text-xs text-muted-foreground">
                  Showing {filteredRows.length} of {watchListRows.length}.
                </p>
                <Button variant="outline" type="button">
                  Add a new account
                </Button>
              </div>
            </div>
          )}
        </SectionCard>
      </div>
    </PageTransition>
  );
}
