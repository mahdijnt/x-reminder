import { apiClient } from "@/lib/api/api-client";
import type {
  ActiveAccountMetric,
  AnalyticsDashboardPayload,
  AnalyticsExport,
  AnalyticsFilters,
  AnalyticsKpis,
  AnalyticsSeriesPoint,
  AnalyticsTweetRow,
  BreadcrumbItem,
  ChartPoint,
  FollowTargetRow,
  FollowingRow,
  MutualFollowerRow,
  NavigationItem,
  NotificationItem,
  ProgressDatum,
  SampleRow,
  StatDatum,
  TargetAchievedRow,
  UserProfile,
  WatchListRow,
} from "@/types";

export type DashboardOverview = {
  stats: StatDatum[];
  progress: ProgressDatum[];
  lineChart: ChartPoint[];
  barChart: ChartPoint[];
  donutChart: ChartPoint[];
  tableRows: SampleRow[];
};

type ApiEnvelope<T> = {
  success: boolean;
  message: string;
  code: string;
  data: T;
};

function unwrapApiResponse<T>(payload: T | ApiEnvelope<T>): T {
  if (payload && typeof payload === "object" && "data" in (payload as Record<string, unknown>)) {
    return (payload as ApiEnvelope<T>).data;
  }
  return payload as T;
}

export type AnalyticsOverview = {
  stats: StatDatum[];
  lineChart: ChartPoint[];
  barChart: ChartPoint[];
  donutChart: ChartPoint[];
  topTweets: AnalyticsTweetRow[];
};

export const navigationService = {
  getSidebarItems: () => apiClient.get<NavigationItem[]>("navigation/sidebar"),
  getTopNavItems: () => apiClient.get<NavigationItem[]>("navigation/top-nav"),
  getBreadcrumbs: () => apiClient.get<BreadcrumbItem[]>("navigation/breadcrumbs"),
};

export const userService = {
  getCurrent: () => apiClient.get<UserProfile>("user/current"),
};

export const notificationsService = {
  list: () => apiClient.get<NotificationItem[]>("notifications"),
};

export const dashboardService = {
  getOverview: () => apiClient.get<DashboardOverview>("dashboard/overview"),
};

export const watchListsService = {
  list: () => apiClient.get<WatchListRow[]>("watch-lists"),
};

export const followingService = {
  list: () => apiClient.get<FollowingRow[]>("following"),
};

export const followTargetsService = {
  list: () => apiClient.get<FollowTargetRow[]>("follow-targets"),
};

export const mutualFollowersService = {
  list: () => apiClient.get<MutualFollowerRow[]>("mutual-followers"),
};

export const targetAchievedService = {
  list: () => apiClient.get<TargetAchievedRow[]>("target-achieved"),
};

export const analyticsService = {
  getOverview: () => apiClient.get<AnalyticsOverview>("analytics/overview"),
  async getSummary(filters: AnalyticsFilters = {}): Promise<AnalyticsKpis> {
    const response = await apiClient.get<ApiEnvelope<{ kpis: AnalyticsKpis }> | { kpis: AnalyticsKpis }>("analytics/summary", {
      params: filters,
    });
    return unwrapApiResponse(response).kpis;
  },
  async getFollowerGrowth(filters: AnalyticsFilters = {}): Promise<AnalyticsSeriesPoint[]> {
    const response = await apiClient.get<ApiEnvelope<{ series: AnalyticsSeriesPoint[] }> | { series: AnalyticsSeriesPoint[] }>(
      "analytics/follower-growth",
      { params: filters }
    );
    return unwrapApiResponse(response).series;
  },
  async getEngagementTimeline(filters: AnalyticsFilters = {}): Promise<AnalyticsSeriesPoint[]> {
    const response = await apiClient.get<ApiEnvelope<{ series: AnalyticsSeriesPoint[] }> | { series: AnalyticsSeriesPoint[] }>(
      "analytics/engagement-timeline",
      { params: filters }
    );
    return unwrapApiResponse(response).series;
  },
  async getMostActive(filters: AnalyticsFilters = {}): Promise<ActiveAccountMetric[]> {
    const response = await apiClient.get<ApiEnvelope<{ items: ActiveAccountMetric[] }> | { items: ActiveAccountMetric[] }>(
      "analytics/most-active",
      { params: filters }
    );
    return unwrapApiResponse(response).items;
  },
  async getMostValuable(filters: AnalyticsFilters = {}): Promise<import("@/types").ValuableAccountMetric[]> {
    const response = await apiClient.get<
      ApiEnvelope<{ items: import("@/types").ValuableAccountMetric[] }> | { items: import("@/types").ValuableAccountMetric[] }
    >("analytics/most-valuable", { params: filters });
    return unwrapApiResponse(response).items;
  },
  async getReport(scope: "daily" | "weekly" | "monthly", filters: AnalyticsFilters = {}): Promise<import("@/types").AnalyticsReport> {
    const response = await apiClient.get<ApiEnvelope<import("@/types").AnalyticsReport> | import("@/types").AnalyticsReport>(
      `analytics/reports/${scope}`,
      { params: filters }
    );
    return unwrapApiResponse(response);
  },
  async exportReport(
    reportType: string,
    format: "json" | "csv",
    filters: AnalyticsFilters = {}
  ): Promise<AnalyticsExport> {
    const response = await apiClient.get<ApiEnvelope<AnalyticsExport> | AnalyticsExport>("analytics/export", {
      params: { ...filters, report_type: reportType, format },
    });
    return unwrapApiResponse(response);
  },
};
export { authService } from "@/services/auth.service";
