/**
 * Client-safe environment configuration.
 */
export const env = {
  apiBaseUrl: process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:3001/api",
  useMockApi: process.env.NEXT_PUBLIC_USE_MOCK_API !== "false",
  appEnv: process.env.NEXT_PUBLIC_APP_ENV ?? "development",
} as const;

export type AppEnv = (typeof env)["appEnv"];
