import { env } from "@/config/env";

export const appConfig = {
  name: "X Engagement Intelligence Manager",
  description: "Next.js dashboard UI (fake data only).",
  featureFlags: {
    enableRealApi: !env.useMockApi,
    enableAnalyticsExport: false,
    enableAuth: false,
  },
} as const;
