import { useQuery } from "@tanstack/react-query";
import type {
  AnalyticsDashboardPayload,
  AnalyticsFilters,
  BreadcrumbItem,
  FollowTargetRow,
  FollowingRow,
  MutualFollowerRow,
  NavigationItem,
  NotificationItem,
  TargetAchievedRow,
  UserProfile,
  WatchListRow,
} from "@/types";
import { queryKeys } from "@/constants/query-keys";
type DashboardOverview = { stats: import("@/types").StatDatum[]; progress: import("@/types").ProgressDatum[]; lineChart: import("@/types").ChartPoint[]; barChart: import("@/types").ChartPoint[]; donutChart: import("@/types").ChartPoint[]; tableRows: import("@/types").SampleRow[] };
type AnalyticsOverview = { stats: import("@/types").StatDatum[]; lineChart: import("@/types").ChartPoint[]; barChart: import("@/types").ChartPoint[]; donutChart: import("@/types").ChartPoint[]; topTweets: import("@/types").AnalyticsTweetRow[] };

import {
  analyticsService,
  dashboardService,
  followTargetsService,
  followingService,
  mutualFollowersService,
  navigationService,
  notificationsService,
  targetAchievedService,
  userService,
  watchListsService,
} from "@/services";

const EMPTY_USER: UserProfile = { name: "", email: "", role: "", initials: "" };
const EMPTY_DASHBOARD: DashboardOverview = { stats: [], progress: [], lineChart: [], barChart: [], donutChart: [], tableRows: [] };
const EMPTY_ANALYTICS_OVERVIEW: AnalyticsOverview = { stats: [], lineChart: [], barChart: [], donutChart: [], topTweets: [] };
const EMPTY_ANALYTICS_DASHBOARD: AnalyticsDashboardPayload = {
  kpis: { follow_back_rate: 0, average_follow_back_time_hours: 0, success_rate: 0 },
  followerGrowth: [],
  engagementTimeline: [],
  mostActive: [],
  mostValuable: [],
  reports: {
    daily: { scope: "daily", period_label: "", kpis: { follow_back_rate: 0, average_follow_back_time_hours: 0, success_rate: 0 }, follower_growth: [], engagement_timeline: [], most_active_accounts: [], most_valuable_accounts: [] },
    weekly: { scope: "weekly", period_label: "", kpis: { follow_back_rate: 0, average_follow_back_time_hours: 0, success_rate: 0 }, follower_growth: [], engagement_timeline: [], most_active_accounts: [], most_valuable_accounts: [] },
    monthly: { scope: "monthly", period_label: "", kpis: { follow_back_rate: 0, average_follow_back_time_hours: 0, success_rate: 0 }, follower_growth: [], engagement_timeline: [], most_active_accounts: [], most_valuable_accounts: [] },
  },
};

export function useSidebarNavigation() { return useQuery({ queryKey: queryKeys.navigation.sidebar, queryFn: () => navigationService.getSidebarItems(), initialData: [] as NavigationItem[] }); }
export function useTopNavigation() { return useQuery({ queryKey: queryKeys.navigation.topNav, queryFn: () => navigationService.getTopNavItems(), initialData: [] as NavigationItem[] }); }
export function useBreadcrumbs() { return useQuery({ queryKey: queryKeys.navigation.breadcrumbs, queryFn: () => navigationService.getBreadcrumbs(), initialData: [] as BreadcrumbItem[] }); }
export function useCurrentUser() { return useQuery({ queryKey: queryKeys.user.current, queryFn: () => userService.getCurrent(), initialData: EMPTY_USER }); }
export function useNotificationsQuery() { return useQuery({ queryKey: queryKeys.notifications.all, queryFn: () => notificationsService.list(), initialData: [] as NotificationItem[] }); }
export function useDashboardOverview() { return useQuery({ queryKey: queryKeys.dashboard.overview, queryFn: () => dashboardService.getOverview(), initialData: EMPTY_DASHBOARD }); }
export function useWatchLists() { return useQuery({ queryKey: queryKeys.watchLists.all, queryFn: () => watchListsService.list(), initialData: [] as WatchListRow[] }); }
export function useFollowing() { return useQuery({ queryKey: queryKeys.following.all, queryFn: () => followingService.list(), initialData: [] as FollowingRow[] }); }
export function useFollowTargets() { return useQuery({ queryKey: queryKeys.followTargets.all, queryFn: () => followTargetsService.list(), initialData: [] as FollowTargetRow[] }); }
export function useMutualFollowers() { return useQuery({ queryKey: queryKeys.mutualFollowers.all, queryFn: () => mutualFollowersService.list(), initialData: [] as MutualFollowerRow[] }); }
export function useTargetAchieved() { return useQuery({ queryKey: queryKeys.targetAchieved.all, queryFn: () => targetAchievedService.list(), initialData: [] as TargetAchievedRow[] }); }
export function useAnalyticsOverview() { return useQuery({ queryKey: queryKeys.analytics.overview, queryFn: () => analyticsService.getOverview(), initialData: EMPTY_ANALYTICS_OVERVIEW }); }

function toPercent(value: number): string { return `${(value * 100).toFixed(1)}%`; }

export function useAnalyticsDashboard(filters: AnalyticsFilters) {
  return useQuery({
    queryKey: queryKeys.analytics.dashboard(filters),
    queryFn: async (): Promise<AnalyticsDashboardPayload> => {
      const [kpis, followerGrowth, engagementTimeline, mostActive, mostValuable, daily, weekly, monthly] = await Promise.all([
        analyticsService.getSummary(filters),
        analyticsService.getFollowerGrowth(filters),
        analyticsService.getEngagementTimeline(filters),
        analyticsService.getMostActive(filters),
        analyticsService.getMostValuable(filters),
        analyticsService.getReport("daily", { ...filters, granularity: "daily" }),
        analyticsService.getReport("weekly", { ...filters, granularity: "weekly" }),
        analyticsService.getReport("monthly", { ...filters, granularity: "monthly" }),
      ]);
      return { kpis, followerGrowth, engagementTimeline, mostActive, mostValuable, reports: { daily, weekly, monthly } };
    },
    initialData: EMPTY_ANALYTICS_DASHBOARD,
  });
}

export function mapKpisToStats(kpis: { follow_back_rate: number; average_follow_back_time_hours: number; success_rate: number }) {
  return [
    { title: "Follow Back Rate", value: toPercent(kpis.follow_back_rate), change: "+2.3%", trend: "up" as const, detail: "Followers following back" },
    { title: "Avg Follow Back Time", value: `${kpis.average_follow_back_time_hours.toFixed(1)}h`, change: "-1.1h", trend: "up" as const, detail: "Average delay to follow back" },
    { title: "Success Rate", value: toPercent(kpis.success_rate), change: "+1.8%", trend: "up" as const, detail: "Campaign success ratio" },
  ];
}
