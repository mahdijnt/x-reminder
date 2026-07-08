import { registerMockHandler } from "@/lib/api/api-client";
import { ApiError } from "@/lib/api/types";
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

const routes: Record<string, () => unknown> = {
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
    return handler();
  });
}

