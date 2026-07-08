import { apiClient } from "@/lib/api/api-client";
import type {
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
};
