"use client";

import * as React from "react";
import { QueryClientProvider } from "@tanstack/react-query";
import { installMockApi } from "@/lib/api/mocks";
import { getQueryClient } from "@/lib/query-client";
import { ErrorBoundary } from "@/components/boundaries/error-boundary";
import { SessionExpiredBanner } from "@/components/auth/session-expired-banner";
import { Toaster } from "@/components/ui/toaster";
import { AuthProvider } from "@/providers/auth-provider";
import { NotificationProvider } from "@/providers/notification-provider";
import { ThemeProvider } from "@/providers/theme-provider";

let mockInstalled = false;
function ensureMockApi() { if (mockInstalled) return; installMockApi(); mockInstalled = true; }
function reportFrontendError(error: Error, info?: string) { const provider = process.env.NEXT_PUBLIC_SENTRY_DSN ? "sentry" : "none"; if (provider === "none") { console.error("frontend_error", { message: error.message, info }); return; } console.error("frontend_error_external", { provider, message: error.message, info }); }

export function AppProviders({ children }: { children: React.ReactNode }) {
  ensureMockApi();
  const [queryClient] = React.useState(() => getQueryClient());
  return <ErrorBoundary onError={reportFrontendError}><QueryClientProvider client={queryClient}><ThemeProvider><AuthProvider><NotificationProvider><SessionExpiredBanner />{children}<Toaster /></NotificationProvider></AuthProvider></ThemeProvider></QueryClientProvider></ErrorBoundary>;
}
