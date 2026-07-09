"use client";

import * as React from "react";
import { MoreHorizontal } from "lucide-react";

import { DataTable } from "@/components/data-display/data-table";
import { SearchBar } from "@/components/forms/search-bar";
import { LoadingSkeleton } from "@/components/feedback/loading-skeleton";
import { ActionDialog } from "@/components/feedback/action-dialog";
import { StatusChip } from "@/components/feedback/status-chip";
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
import { PageTransition } from "@/components/motion/page-transition";

import type { NotificationItem, TableColumn } from "@/types";
import { useNotificationsQuery } from "@/hooks/use-api-data";

function chipFromTone(tone: NonNullable<NotificationItem["tone"]>): React.ComponentProps<typeof StatusChip>["status"] {
  if (tone === "success") return "success";
  if (tone === "warning") return "warning";
  if (tone === "danger") return "danger";
  return "neutral";
}

export default function NotificationsPage() {
  const { data: seedNotifications } = useNotificationsQuery();
  const loading = useSimulatedLoading(650);
  const [items, setItems] = React.useState<NotificationItem[]>(() =>
    seedNotifications.map((n) => ({ ...n }))
  );
  const [filter, setFilter] = React.useState<"all" | "unread">("unread");
  const [query, setQuery] = React.useState("");
  const [actionMessage, setActionMessage] = React.useState<string | null>(null);

  const filtered = React.useMemo(() => {
    const q = query.trim().toLowerCase();
    return items.filter((n) => {
      const matchesFilter = filter === "all" ? true : Boolean(n.unread);
      const matchesQuery = !q
        ? true
        : `${n.title} ${n.description}`.toLowerCase().includes(q);

      return matchesFilter && matchesQuery;
    });
  }, [items, filter, query]);

  const unreadCount = React.useMemo(() => items.filter((n) => n.unread).length, [items]);

  const columns = React.useMemo<TableColumn<NotificationItem>[]>(
    () => [
      {
        key: "title",
        header: "Notification",
        render: (row) => (
          <div className="space-y-1">
            <div className="flex flex-wrap items-center gap-2">
              <p className="font-medium text-foreground">{row.title}</p>
              {row.unread ? <Badge variant="glass">New</Badge> : null}
            </div>
            <p className="text-xs text-muted-foreground">{row.description}</p>
          </div>
        ),
      },
      {
        key: "time",
        header: "Time",
        render: (row) => <span className="text-muted-foreground">{row.time}</span>,
      },
      {
        key: "tone",
        header: "Tone",
        render: (row) => (
          <StatusChip status={chipFromTone(row.tone ?? "default")}>{row.tone ?? "default"}</StatusChip>
        ),
      },
      {
        key: "id",
        header: "Actions",
        align: "right",
        render: (row) => (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="icon" type="button" aria-label={`Open actions for ${row.title}`}>
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-[16rem]">
              {row.unread ? (
                <ActionDialog
                  title="Mark as read"
                  description={`Mark “${row.title}” as read. (Fake action)`}
                  cancelLabel="Cancel"
                  confirmLabel="Read"
                  trigger={<DropdownMenuItem>Mark as read</DropdownMenuItem>}
                  onConfirm={() => {
                    setItems((prev) => prev.map((n) => (n.id === row.id ? { ...n, unread: false } : n)));
                    setActionMessage(`Marked read: ${row.title}`);
                  }}
                />
              ) : (
                <ActionDialog
                  title="Mark as unread"
                  description={`Mark “${row.title}” as unread. (Fake action)`}
                  cancelLabel="Cancel"
                  confirmLabel="Unread"
                  trigger={<DropdownMenuItem>Mark as unread</DropdownMenuItem>}
                  onConfirm={() => {
                    setItems((prev) => prev.map((n) => (n.id === row.id ? { ...n, unread: true } : n)));
                    setActionMessage(`Marked unread: ${row.title}`);
                  }}
                />
              )}

              <ActionDialog
                title="Dismiss"
                description={`Dismiss “${row.title}”. (Fake action)`}
                cancelLabel="Cancel"
                confirmLabel="Dismiss"
                trigger={<DropdownMenuItem>Dismiss</DropdownMenuItem>}
                onConfirm={() => {
                  setItems((prev) => prev.filter((n) => n.id !== row.id));
                  setActionMessage(`Dismissed: ${row.title}`);
                }}
              />
            </DropdownMenuContent>
          </DropdownMenu>
        ),
      },
    ],
    []
  );

  const markAllRead = () => {
    setItems((prev) => prev.map((n) => ({ ...n, unread: false })));
    setActionMessage("All notifications marked read.");
  };

  return (
    <PageTransition>
      <div className="space-y-6">
        <div className="space-y-2">
          <h1 className="text-2xl font-semibold tracking-tight">Notifications</h1>
          <p className="text-sm text-muted-foreground">Filter by unread, search content, and simulate actions.</p>
        </div>

        <SectionCard
          title="Inbox"
          description="UI-only notification center with skeleton loading."
          action={
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-end">
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline" type="button">
                    Filter: {filter === "unread" ? `Unread (${unreadCount})` : "All"}
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuItem onClick={() => setFilter("unread")}>Unread</DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setFilter("all")}>All</DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>

              <ActionDialog
                title="Mark all as read"
                description="Simulate marking all notifications read. (Fake action)"
                cancelLabel="Cancel"
                confirmLabel="Mark read"
                trigger={<Button type="button" variant="glass">Mark all read</Button>}
                onConfirm={markAllRead}
              />
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

              <div className="flex w-full flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div className="w-full max-w-[22rem]">
                  <SearchBar value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search notifications..." />
                </div>
                <div className="text-xs text-muted-foreground">
                  Showing {filtered.length} items
                </div>
              </div>

              <DataTable columns={columns} rows={filtered} caption="Notification list (fake)." />
            </div>
          )}
        </SectionCard>
      </div>
    </PageTransition>
  );
}
