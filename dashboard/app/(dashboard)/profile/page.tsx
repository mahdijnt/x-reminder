"use client";

import * as React from "react";
import { Edit3, MoreHorizontal } from "lucide-react";

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { DataTable } from "@/components/data-display/data-table";
import { SearchBar } from "@/components/forms/search-bar";
import { LoadingSkeleton } from "@/components/feedback/loading-skeleton";
import { StatusChip } from "@/components/feedback/status-chip";
import { ActionDialog } from "@/components/feedback/action-dialog";
import { StatCard } from "@/components/dashboard/stat-card";
import { SectionCard } from "@/components/dashboard/section-card";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

import { useSimulatedLoading } from "@/app/_components/use-simulated-loading";
import { PageTransition } from "@/app/_components/page-transition";

import type { TableColumn } from "@/types";
import { useCurrentUser } from "@/hooks/use-api-data";

type ActivityRow = {
  id: string;
  action: string;
  time: string;
  state: "Success" | "Warning" | "Info";
};

const activityRows: ActivityRow[] = [
  { id: "ap-1", action: "Follow target executed", time: "12m ago", state: "Success" },
  { id: "ap-2", action: "Muted a low-signal account", time: "38m ago", state: "Info" },
  { id: "ap-3", action: "Paused a watch workflow", time: "1h ago", state: "Warning" },
  { id: "ap-4", action: "Archived an achieved target", time: "3h ago", state: "Success" },
  { id: "ap-5", action: "Resumed watch monitoring", time: "6h ago", state: "Info" },
];

function chipFromActivityState(state: ActivityRow["state"]): React.ComponentProps<typeof StatusChip>["status"] {
  if (state === "Success") return "success";
  if (state === "Warning") return "warning";
  return "info";
}

export default function ProfilePage() {
  const { data: sampleUser } = useCurrentUser();
  const loading = useSimulatedLoading(700);

  const [notice, setNotice] = React.useState<string | null>(null);
  const [name, setName] = React.useState(sampleUser.name);
  const [email, setEmail] = React.useState(sampleUser.email);
  const [role, setRole] = React.useState(sampleUser.role);
  const [plan, setPlan] = React.useState<"Pro" | "Team">("Pro");

  const [query, setQuery] = React.useState("");

  const filteredActivities = React.useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return activityRows;
    return activityRows.filter((r) => r.action.toLowerCase().includes(q) || r.state.toLowerCase().includes(q));
  }, [query]);

  const columns = React.useMemo<TableColumn<ActivityRow>[]>(
    () => [
      {
        key: "action",
        header: "Activity",
        render: (row) => (
          <div className="space-y-1">
            <p className="font-medium text-foreground">{row.action}</p>
            <p className="text-xs text-muted-foreground">Simulated update</p>
          </div>
        ),
      },
      {
        key: "time",
        header: "Time",
        render: (row) => <span className="text-muted-foreground">{row.time}</span>,
      },
      {
        key: "state",
        header: "State",
        render: (row) => <StatusChip status={chipFromActivityState(row.state)}>{row.state}</StatusChip>,
      },
      {
        key: "id",
        header: "Actions",
        align: "right",
        render: (row) => (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="icon" type="button" aria-label="Open activity actions">
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-[16rem]">
              <ActionDialog
                title="View details"
                description={`Simulate viewing details for: ${row.action}`}
                cancelLabel="Close"
                confirmLabel="Ok"
                trigger={<DropdownMenuItem>View details</DropdownMenuItem>}
                onConfirm={() => setNotice(`Viewed: ${row.action}`)}
              />
            </DropdownMenuContent>
          </DropdownMenu>
        ),
      },
    ],
    []
  );

  const saveProfile = () => {
    setNotice("Profile saved (simulated). No backend connected.");
    window.setTimeout(() => setNotice(null), 2500);
  };

  return (
    <PageTransition>
      <div className="space-y-6">
        <div className="space-y-2">
          <h1 className="text-2xl font-semibold tracking-tight">Profile</h1>
          <p className="text-sm text-muted-foreground">Editable profile UI with dialogs and searchable activity table.</p>
        </div>

        {loading ? (
          <div className="space-y-3">
            <LoadingSkeleton lines={6} showAvatar />
            <LoadingSkeleton lines={6} />
            <LoadingSkeleton lines={6} />
          </div>
        ) : (
          <>
            {notice ? (
              <Alert className="glass-surface">
                <AlertTitle>Update complete</AlertTitle>
                <AlertDescription>{notice}</AlertDescription>
              </Alert>
            ) : null}

            <div className="grid grid-cols-1 gap-4 lg:grid-cols-[1.2fr_1fr]">
              <SectionCard
                title="Your identity"
                description="Update display info (local-only)."
                action={
                  <div className="flex items-center gap-2">
                    <Badge variant="glass">{plan} plan</Badge>
                    <ActionDialog
                      title="Save profile"
                      description="Simulate saving profile settings. (Fake)"
                      cancelLabel="Cancel"
                      confirmLabel="Save"
                      trigger={<Button type="button">Save</Button>}
                      onConfirm={saveProfile}
                    />
                  </div>
                }
              >
                <div className="flex items-start gap-4">
                  <Avatar className="h-14 w-14">
                    <AvatarImage src="/avatar.png" alt={name} />
                    <AvatarFallback name={name} fallback={sampleUser.initials} />
                  </Avatar>
                  <div className="flex-1 space-y-4">
                    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                      <div className="space-y-2">
                        <p className="text-sm font-medium">Display name</p>
                        <div className="relative">
                          <Edit3 className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                          <input
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            className="flex h-10 w-full rounded-md border border-input bg-background/60 pl-10 pr-3 text-sm text-foreground shadow-sm backdrop-blur-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                            aria-label="Display name"
                          />
                        </div>
                      </div>

                      <div className="space-y-2">
                        <p className="text-sm font-medium">Role</p>
                        <input
                          value={role}
                          onChange={(e) => setRole(e.target.value)}
                          className="flex h-10 w-full rounded-md border border-input bg-background/60 px-3 text-sm text-foreground shadow-sm backdrop-blur-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                          aria-label="Role"
                        />
                      </div>

                      <div className="space-y-2 sm:col-span-2">
                        <p className="text-sm font-medium">Email</p>
                        <input
                          value={email}
                          onChange={(e) => setEmail(e.target.value)}
                          className="flex h-10 w-full rounded-md border border-input bg-background/60 px-3 text-sm text-foreground shadow-sm backdrop-blur-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                          aria-label="Email"
                        />
                      </div>
                    </div>

                    <div className="rounded-xl border border-glass-border glass-surface p-4 shadow-sm">
                      <div className="flex items-start justify-between gap-3">
                        <div className="space-y-1">
                          <p className="text-sm font-medium">Subscription</p>
                          <p className="text-xs text-muted-foreground">Switch plan in UI only.</p>
                        </div>
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="outline" type="button">
                              {plan}
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            {(["Pro", "Team"] as const).map((p) => (
                              <DropdownMenuItem key={p} onClick={() => setPlan(p)}>
                                {p}
                              </DropdownMenuItem>
                            ))}
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </div>
                    </div>
                  </div>
                </div>
              </SectionCard>

              <div className="space-y-4">
                <div className="grid grid-cols-1 gap-4">
                  {[
                    {
                      title: "Tracked accounts",
                      value: "18",
                      change: "+4",
                      trend: "up" as const,
                      detail: "Active watch and follow sets.",
                    },
                    {
                      title: "Following back",
                      value: "7",
                      change: "+1",
                      trend: "neutral" as const,
                      detail: "Mutual followers pending follow-back.",
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
              </div>
            </div>

            <SectionCard
              title="Recent activity"
              description="Search simulated updates and open a dialog from the row actions menu."
              action={
                <div className="w-full max-w-[22rem]">
                  <SearchBar value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search activity..." />
                </div>
              }
            >
              <DataTable
                columns={columns}
                rows={filteredActivities}
                caption="Profile activity (fake)."
              />

              <p className="mt-2 text-xs text-muted-foreground">
                Showing {filteredActivities.length} of {activityRows.length}.
              </p>
            </SectionCard>
          </>
        )}
      </div>
    </PageTransition>
  );
}
