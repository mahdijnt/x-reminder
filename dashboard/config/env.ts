/**
 * Client-safe environment configuration.
 */
const readEnv = (key: string, fallback: string) => process.env[key] ?? fallback;

export const env = {
  apiBaseUrl: readEnv("NEXT_PUBLIC_API_BASE_URL", "http://localhost:8000/api/v1"),
  useMockApi: readEnv("NEXT_PUBLIC_USE_MOCK_API", "true") !== "false",
  appEnv: readEnv("NEXT_PUBLIC_APP_ENV", "development"),
} as const;

export type AppEnv = (typeof env)["appEnv"];
