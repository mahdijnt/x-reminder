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

  "GET analytics/summary": () => ({
    success: true,
    data: {
      kpis: {
        follow_back_rate: 0.58,
        average_follow_back_time_hours: 21.7,
        success_rate: 0.63,
      },
    },
  }),
  "GET analytics/follower-growth": () => ({ success: true, data: { series: sampleLineChartData } }),
  "GET analytics/engagement-timeline": () => ({ success: true, data: { series: sampleBarChartData } }),
  "GET analytics/most-active": () => ({
    success: true,
    data: {
      items: watchListRows.slice(0, 5).map((item, i) => ({
        account_id: `mock-${i}`,
        account: item.handle.replace("@", ""),
        list_type: "following",
        follows: 20 + i * 4,
        follow_backs: 13 + i * 3,
        engagements: 42 + i * 11,
      })),
    },
  }),
  "GET analytics/most-valuable": () => ({
    success: true,
    data: {
      items: watchListRows.slice(0, 5).map((item, i) => ({
        account_id: `mock-${i}`,
        account: item.handle.replace("@", ""),
        list_type: "following",
        value_score: 44 + i * 8,
        avg_follow_back_time_hours: 8 + i * 2,
        engagement_score: 1.4 + i * 0.2,
      })),
    },
  }),
  "GET analytics/reports/daily": () => ({
    success: true,
    data: {
      scope: "daily",
      period_label: "Daily report",
      kpis: { follow_back_rate: 0.58, average_follow_back_time_hours: 21.7, success_rate: 0.63 },
      follower_growth: sampleLineChartData,
      engagement_timeline: sampleBarChartData,
      most_active_accounts: [],
      most_valuable_accounts: [],
    },
  }),
  "GET analytics/reports/weekly": () => ({
    success: true,
    data: {
      scope: "weekly",
      period_label: "Weekly report",
      kpis: { follow_back_rate: 0.56, average_follow_back_time_hours: 23.1, success_rate: 0.61 },
      follower_growth: sampleLineChartData,
      engagement_timeline: sampleBarChartData,
      most_active_accounts: [],
      most_valuable_accounts: [],
    },
  }),
  "GET analytics/reports/monthly": () => ({
    success: true,
    data: {
      scope: "monthly",
      period_label: "Monthly report",
      kpis: { follow_back_rate: 0.54, average_follow_back_time_hours: 24.8, success_rate: 0.6 },
      follower_growth: sampleLineChartData,
      engagement_timeline: sampleBarChartData,
      most_active_accounts: [],
      most_valuable_accounts: [],
    },
  }),
  "GET analytics/export": () => ({
    success: true,
    data: {
      format: "json",
      filename: "analytics-summary.json",
      content_type: "application/json",
      content: JSON.stringify({ message: "mock export" }, null, 2),
    },
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
