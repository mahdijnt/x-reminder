import { registerMockHandler } from "@/lib/api/api-client";
import { ApiError } from "@/lib/api/types";
import {
  mockAuthForgotPassword,
  mockAuthLogin,
  mockAuthLogout,
  mockAuthMe,
  mockAuthRegister,
  mockAuthResetPassword,
} from "@/lib/api/mocks/auth-mock";
import {
  analyticsTopTweetRows,
  followTargetRows,
  followingRows,
  mutualFollowerRows,
  sampleBarChartData,
  sampleBreadcrumbs,
  sampleDonutChartData,
  sampleLineChartData,
  sampleNotifications,
  sampleProgressItems,
  sampleSidebarItems,
  sampleStats,
  sampleTableRows,
  sampleTopNavItems,
  sampleUser,
  targetAchievedRows,
  watchListRows,
} from "@/lib/mock-data";
import type {
  ForgotPasswordPayload,
  LoginCredentials,
  RegisterPayload,
  ResetPasswordPayload,
} from "@/types/auth";

const routes: Record<string, (body?: unknown, headers?: HeadersInit) => unknown> = {
  "GET navigation/sidebar": () => sampleSidebarItems,
  "GET navigation/top-nav": () => sampleTopNavItems,
  "GET navigation/breadcrumbs": () => sampleBreadcrumbs,
  "GET user/current": () => sampleUser,
  "GET notifications": () => sampleNotifications.map((n) => ({ ...n })),
  "GET dashboard/overview": () => ({
    stats: sampleStats,
    progress: sampleProgressItems,
    lineChart: sampleLineChartData,
    barChart: sampleBarChartData,
    donutChart: sampleDonutChartData,
    tableRows: sampleTableRows,
  }),
  "GET watch-lists": () => watchListRows,
  "GET following": () => followingRows,
  "GET follow-targets": () => followTargetRows,
  "GET mutual-followers": () => mutualFollowerRows,
  "GET target-achieved": () => targetAchievedRows,
  "GET analytics/overview": () => ({
    stats: sampleStats,
    lineChart: sampleLineChartData,
    barChart: sampleBarChartData,
    donutChart: sampleDonutChartData,
    topTweets: analyticsTopTweetRows,
  }),
  "POST auth/login": (body) => mockAuthLogin(body as LoginCredentials),
  "POST auth/register": (body) => mockAuthRegister(body as RegisterPayload),
  "POST auth/forgot-password": (body) => mockAuthForgotPassword(body as ForgotPasswordPayload),
  "POST auth/reset-password": (body) => mockAuthResetPassword(body as ResetPasswordPayload),
  "POST auth/logout": () => mockAuthLogout(),
  "GET auth/me": (_body, headers) => {
    const authHeader =
      typeof headers === "object" && headers && "Authorization" in headers
        ? String((headers as Record<string, string>).Authorization)
        : "";
    const token = authHeader.replace(/^Bearer\s+/i, "");
    return mockAuthMe(token);
  },
};

export function installMockApi() {
  registerMockHandler(async (path, options) => {
    const method = (options?.method ?? "GET").toUpperCase();
    const key = `${method} ${path.replace(/^\//, "")}`;
    const normalizedKey = key.replace(/\/+/g, "/");
    const handler = routes[normalizedKey];
    if (!handler) {
      throw new ApiError({ message: `No mock route for ${normalizedKey}`, code: "NOT_FOUND", status: 404 });
    }
    const body = options?.body;
    return handler(body, options?.headers);
  });
}
