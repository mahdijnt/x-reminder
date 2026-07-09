import { env } from "@/config/env";

export const appConfig = {
  name: "X Reminder Dashboard",
  description: "Analytics and engagement dashboard for X reminder workflows.",
  url: process.env.NEXT_PUBLIC_APP_URL ?? "http://localhost:3000",
  featureFlags: {
    enableRealApi: !env.useMockApi,
    enableAnalyticsExport: false,
    enableAuth: false,
  },
} as const;
