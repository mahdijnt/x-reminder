"use client";

import * as React from "react";
import { RotateCcw } from "lucide-react";

import { ActionDialog } from "@/components/feedback/action-dialog";
import { LoadingSkeleton } from "@/components/feedback/loading-skeleton";
import { SectionCard } from "@/components/dashboard/section-card";
import { useSimulatedLoading } from "@/app/_components/use-simulated-loading";
import { PageTransition } from "@/components/motion/page-transition";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";

export default function SettingsPage() {
  const loading = useSimulatedLoading(650);

  const [notice, setNotice] = React.useState<string | null>(null);

  const [notificationsEnabled, setNotificationsEnabled] = React.useState(true);
  const [dailyDigest, setDailyDigest] = React.useState(false);
  const [digestFrequency, setDigestFrequency] = React.useState<"Daily" | "Weekly" | "Monthly">("Weekly");
  const [exportFormat, setExportFormat] = React.useState<"CSV" | "JSON">("CSV");

  const saveChanges = () => {
    setNotice("Saved (simulated). No backend connected.");
    window.setTimeout(() => setNotice(null), 2500);
  };

  return (
    <PageTransition>
      <div className="space-y-6">
        <div className="space-y-2">
          <h1 className="text-2xl font-semibold tracking-tight">Settings</h1>
          <p className="text-sm text-muted-foreground">Responsive preferences UI with simulated save/reset dialogs.</p>
        </div>

        {loading ? (
          <div className="space-y-3">
            <LoadingSkeleton lines={6} />
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

            <SectionCard
              title="Workspace preferences"
              description="All controls are local-only; actions update the UI."
              action={
                <div className="flex items-center gap-2">
                  <Badge variant="glass">Fake settings</Badge>
                  <ActionDialog
                    title="Save changes"
                    description="Simulate saving your preferences. (No backend)"
                    cancelLabel="Cancel"
                    confirmLabel="Save"
                    trigger={<Button type="button">Save changes</Button>}
                    onConfirm={saveChanges}
                  />
                </div>
              }
            >
              <Tabs defaultValue="preferences" className="w-full">
                <TabsList className="w-full justify-start overflow-x-auto">
                  <TabsTrigger value="preferences">Preferences</TabsTrigger>
                  <TabsTrigger value="notifications">Notifications</TabsTrigger>
                  <TabsTrigger value="data">Data & Access</TabsTrigger>
                </TabsList>

                <TabsContent value="preferences">
                  <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                    <label className="flex items-start gap-3 rounded-xl border border-glass-border glass-surface p-4 shadow-sm">
                      <input
                        type="checkbox"
                        checked={notificationsEnabled}
                        onChange={(e) => setNotificationsEnabled(e.target.checked)}
                        className="mt-1 h-4 w-4 rounded border-input bg-background/60"
                      />
                      <span className="space-y-1">
                        <span className="font-medium text-foreground">Enable in-app notifications</span>
                        <span className="block text-sm text-muted-foreground">Show alerts for important status changes.</span>
                      </span>
                    </label>

                    <label className="flex items-start gap-3 rounded-xl border border-glass-border glass-surface p-4 shadow-sm">
                      <input
                        type="checkbox"
                        checked={dailyDigest}
                        onChange={(e) => setDailyDigest(e.target.checked)}
                        className="mt-1 h-4 w-4 rounded border-input bg-background/60"
                      />
                      <span className="space-y-1">
                        <span className="font-medium text-foreground">Daily digest mode</span>
                        <span className="block text-sm text-muted-foreground">Override weekly digest for one day.</span>
                      </span>
                    </label>

                    <div className="rounded-xl border border-glass-border glass-surface p-4 shadow-sm">
                      <p className="text-sm font-medium">Digest frequency</p>
                      <p className="mt-1 text-xs text-muted-foreground">Pure UI dropdown.</p>
                      <div className="mt-3">
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="outline" type="button" className="w-full justify-between">
                              <span>{digestFrequency}</span>
                              <span className="text-muted-foreground">Change</span>
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end" className="w-full">
                            {(["Daily", "Weekly", "Monthly"] as const).map((v) => (
                              <DropdownMenuItem key={v} onClick={() => setDigestFrequency(v)}>
                                {v}
                              </DropdownMenuItem>
                            ))}
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </div>
                    </div>

                    <div className="rounded-xl border border-glass-border glass-surface p-4 shadow-sm">
                      <p className="text-sm font-medium">Default export format</p>
                      <p className="mt-1 text-xs text-muted-foreground">Controls which data format the UI “exports”.</p>
                      <div className="mt-3">
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="outline" type="button" className="w-full justify-between">
                              <span>{exportFormat}</span>
                              <span className="text-muted-foreground">Change</span>
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end" className="w-full">
                            {(["CSV", "JSON"] as const).map((v) => (
                              <DropdownMenuItem key={v} onClick={() => setExportFormat(v)}>
                                {v}
                              </DropdownMenuItem>
                            ))}
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </div>
                    </div>
                  </div>
                </TabsContent>

                <TabsContent value="notifications">
                  <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                    <div className="rounded-xl border border-glass-border glass-surface p-4 shadow-sm">
                      <p className="text-sm font-medium">Priority rules</p>
                      <p className="mt-1 text-xs text-muted-foreground">Simulated checkboxes.</p>
                      <div className="mt-3 space-y-3">
                        {[
                          { label: "Goal reached", key: "goal" },
                          { label: "Attention needed", key: "attention" },
                          { label: "New mutual found", key: "mutual" },
                        ].map((item) => (
                          <label key={item.key} className="flex items-center justify-between rounded-lg bg-background/30 px-3 py-2">
                            <span className="text-sm text-foreground">{item.label}</span>
                            <input
                              type="checkbox"
                              defaultChecked
                              className="h-4 w-4 rounded border-input bg-background/60"
                              onChange={() => setNotice("Updated notification rule (simulated).")}
                            />
                          </label>
                        ))}
                      </div>
                    </div>

                    <div className="rounded-xl border border-glass-border glass-surface p-4 shadow-sm">
                      <p className="text-sm font-medium">Support contact</p>
                      <p className="mt-1 text-xs text-muted-foreground">No backend, but UI validates locally.</p>
                      <div className="mt-3 space-y-3">
                        <Input defaultValue="support@x-engagement.example" aria-label="Support email" />
                        <Button variant="outline" type="button" className="w-full" onClick={() => setNotice("Copied support email (simulated).")}
                        >
                          Copy email
                        </Button>
                      </div>
                    </div>
                  </div>
                </TabsContent>

                <TabsContent value="data">
                  <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                    <div className="rounded-xl border border-glass-border glass-surface p-4 shadow-sm">
                      <p className="text-sm font-medium">Data retention</p>
                      <p className="mt-1 text-xs text-muted-foreground">Choose how long demo records persist in UI.</p>
                      <div className="mt-3">
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="outline" type="button" className="w-full justify-between">
                              <span>30 days</span>
                              <span className="text-muted-foreground">Change</span>
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end" className="w-full">
                            {(["7 days", "30 days", "90 days"] as const).map((v) => (
                              <DropdownMenuItem key={v} onClick={() => setNotice(`Set retention: ${v} (simulated).`)}>
                                {v}
                              </DropdownMenuItem>
                            ))}
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </div>
                    </div>

                    <div className="rounded-xl border border-glass-border glass-surface p-4 shadow-sm">
                      <p className="text-sm font-medium">Danger zone</p>
                      <p className="mt-1 text-xs text-muted-foreground">Reset demo data and UI state.</p>
                      <div className="mt-3">
                        <ActionDialog
                          title="Reset demo data"
                          description="Simulate resetting all UI demo state. (No backend)"
                          cancelLabel="Cancel"
                          confirmLabel="Reset"
                          trigger={
                            <Button variant="destructive" type="button" className="w-full">
                              <RotateCcw className="mr-2 h-4 w-4" />
                              Reset demo data
                            </Button>
                          }
                          onConfirm={() => setNotice("Demo data reset (simulated).")}
                        />
                      </div>
                    </div>
                  </div>
                </TabsContent>
              </Tabs>
            </SectionCard>
          </>
        )}
      </div>
    </PageTransition>
  );
}
