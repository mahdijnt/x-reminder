"use client";

import * as React from "react";
import { MoreHorizontal } from "lucide-react";

import { DataTable } from "@/components/data-display/data-table";
import { SearchBar } from "@/components/forms/search-bar";
import { LoadingSkeleton } from "@/components/feedback/loading-skeleton";
import { ActionDialog } from "@/components/feedback/action-dialog";
import { StatCard } from "@/components/dashboard/stat-card";
import { SectionCard } from "@/components/dashboard/section-card";

import { Badge } from "@/components/ui/badge";
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

import type { MutualFollowerRow, TableColumn } from "@/lib/mock-data";
import { mutualFollowerRows } from "@/lib/mock-data";

export default function MutualFollowersPage() {
  const loading = useSimulatedLoading(750);
  const [query, setQuery] = React.useState("");
  const [actionMessage, setActionMessage] = React.useState<string | null>(null);

  const filteredRows = React.useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return mutualFollowerRows;

    return mutualFollowerRows.filter((row) => {
      return (
        row.name.toLowerCase().includes(q) ||
        row.handle.toLowerCase().includes(q) ||
        row.tier.toLowerCase().includes(q) ||
        row.lastMention.toLowerCase().includes(q)
      );
    });
  }, [query]);

  const totals = React.useMemo(() => {
    const gold = mutualFollowerRows.filter((r) => r.tier === "Gold").length;
    const standard = mutualFollowerRows.filter((r) => r.tier === "Standard").length;
    return { gold, standard, total: mutualFollowerRows.length };
  }, []);

  const columns = React.useMemo<TableColumn<MutualFollowerRow>[]>(
    () => [
      {
        key: "name",
        header: "Mutual",
        render: (row) => (
          <div className="space-y-1">
            <p className="font-medium text-foreground">{row.name}</p>
            <p className="text-xs text-muted-foreground">{row.handle}</p>
          </div>
        ),
      },
      {
        key: "mutualSince",
        header: "Mutual since",
        render: (row) => <span className="text-muted-foreground">{row.mutualSince}</span>,
      },
      {
        key: "lastMention",
        header: "Last mention",
        render: (row) => <span className="text-muted-foreground">{row.lastMention}</span>,
      },
      {
        key: "tier",
        header: "Tier",
        render: (row) => (
          <Badge variant={row.tier === "Gold" ? "glass" : "outline"}>{row.tier}</Badge>
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
            <DropdownMenuContent align="end" className="w-[17rem]">
              <ActionDialog
                title="Follow back"
                description={`Simulate following back ${row.handle}. (Fake action)`}
                cancelLabel="Cancel"
                confirmLabel="Follow back"
                trigger={<DropdownMenuItem>Follow back</DropdownMenuItem>}
                onConfirm={() => setActionMessage(`Follow back queued for ${row.handle}.`)}
              />

              <ActionDialog
                title="Send message"
                description={`Simulate sending a DM to ${row.handle}. (Fake action)`}
                cancelLabel="Cancel"
                confirmLabel="Send"
                trigger={<DropdownMenuItem>Send message</DropdownMenuItem>}
                onConfirm={() => setActionMessage(`Message queued for ${row.handle}.`)}
              />

              <ActionDialog
                title="Remove mutual"
                description={`Stop tracking mutual relationship for ${row.handle}. (Fake action)`}
                cancelLabel="Cancel"
                confirmLabel="Remove"
                trigger={<DropdownMenuItem>Remove</DropdownMenuItem>}
                onConfirm={() => setActionMessage(`Removed ${row.handle} from mutual tracking.`)}
              />
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
          <h1 className="text-2xl font-semibold tracking-tight">Mutual Followers</h1>
          <p className="text-sm text-muted-foreground">Identify mutually following accounts and simulate follow-back actions.</p>
        </div>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          {[
            {
              title: "Mutuals",
              value: String(totals.total),
              change: "+2",
              trend: "up" as const,
              detail: "Accounts that follow you back.",
            },
            {
              title: "Gold tier",
              value: String(totals.gold),
              change: "+1",
              trend: "up" as const,
              detail: "High-quality mutual relationships.",
            },
            {
              title: "Standard tier",
              value: String(totals.standard),
              change: "0",
              trend: "neutral" as const,
              detail: "Lower priority but still relevant.",
            },
          ].map((s) => (
            <div key={s.title} className="transform-gpu transition-transform duration-300 hover:-translate-y-0.5 active:translate-y-0">
              <StatCard {...s} />
            </div>
          ))}
        </div>

        <SectionCard
          title="Mutual list"
          description="Search and open dialogs using the row actions dropdown."
          action={
            <div className="w-full max-w-[22rem]">
              <SearchBar value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search by name, handle, tier..." />
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

              <DataTable columns={columns} rows={filteredRows} caption="Mutual follower records (fake data)." />

              <p className="text-xs text-muted-foreground">
                Showing {filteredRows.length} of {mutualFollowerRows.length}.
              </p>
            </div>
          )}
        </SectionCard>
      </div>
    </PageTransition>
  );
}
