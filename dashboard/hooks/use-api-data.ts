import { useQuery } from "@tanstack/react-query";
import type { AnalyticsDashboardPayload, AnalyticsFilters } from "@/types";
import { queryKeys } from "@/constants/query-keys";
import {
  analyticsTopTweetRows,
  followTargetRows,
  followingRows,
  mutualFollowerRows,
  sampleBarChartData,
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

const dashboardOverviewInitial = {
  stats: sampleStats,
  progress: sampleProgressItems,
  lineChart: sampleLineChartData,
  barChart: sampleBarChartData,
  donutChart: sampleDonutChartData,
  tableRows: sampleTableRows,
};

const analyticsOverviewInitial = {
  stats: sampleStats,
  lineChart: sampleLineChartData,
  barChart: sampleBarChartData,
  donutChart: sampleDonutChartData,
  topTweets: analyticsTopTweetRows,
};

export function useSidebarNavigation() {
  return useQuery({
    queryKey: queryKeys.navigation.sidebar,
    queryFn: () => navigationService.getSidebarItems(),
    initialData: sampleSidebarItems,
  });
}

export function useTopNavigation() {
  return useQuery({
    queryKey: queryKeys.navigation.topNav,
    queryFn: () => navigationService.getTopNavItems(),
    initialData: sampleTopNavItems,
  });
}

export function useBreadcrumbs() {
  return useQuery({
    queryKey: queryKeys.navigation.breadcrumbs,
    queryFn: () => navigationService.getBreadcrumbs(),
  });
}

export function useCurrentUser() {
  return useQuery({
    queryKey: queryKeys.user.current,
    queryFn: () => userService.getCurrent(),
    initialData: sampleUser,
  });
}

export function useNotificationsQuery() {
  return useQuery({
    queryKey: queryKeys.notifications.all,
    queryFn: () => notificationsService.list(),
    initialData: sampleNotifications.map((n) => ({ ...n })),
  });
}

export function useDashboardOverview() {
  return useQuery({
    queryKey: queryKeys.dashboard.overview,
    queryFn: () => dashboardService.getOverview(),
    initialData: dashboardOverviewInitial,
  });
}

export function useWatchLists() {
  return useQuery({
    queryKey: queryKeys.watchLists.all,
    queryFn: () => watchListsService.list(),
    initialData: watchListRows,
  });
}

export function useFollowing() {
  return useQuery({
    queryKey: queryKeys.following.all,
    queryFn: () => followingService.list(),
    initialData: followingRows,
  });
}

export function useFollowTargets() {
  return useQuery({
    queryKey: queryKeys.followTargets.all,
    queryFn: () => followTargetsService.list(),
    initialData: followTargetRows,
  });
}

export function useMutualFollowers() {
  return useQuery({
    queryKey: queryKeys.mutualFollowers.all,
    queryFn: () => mutualFollowersService.list(),
    initialData: mutualFollowerRows,
  });
}

export function useTargetAchieved() {
  return useQuery({
    queryKey: queryKeys.targetAchieved.all,
    queryFn: () => targetAchievedService.list(),
    initialData: targetAchievedRows,
  });
}

export function useAnalyticsOverview() {
  return useQuery({
    queryKey: queryKeys.analytics.overview,
    queryFn: () => analyticsService.getOverview(),
    initialData: analyticsOverviewInitial,
  });
}


function toPercent(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

function fallbackAnalyticsPayload(): AnalyticsDashboardPayload {
  return {
    kpis: {
      follow_back_rate: 0.58,
      average_follow_back_time_hours: 22,
      success_rate: 0.61,
    },
    followerGrowth: sampleLineChartData,
    engagementTimeline: sampleBarChartData,
    mostActive: watchListRows.slice(0, 5).map((item, i) => ({
      account_id: `fallback-${i}`,
      account: item.handle.replace("@", ""),
      list_type: "following",
      follows: 20 + i * 5,
      follow_backs: 12 + i * 4,
      engagements: 40 + i * 12,
    })),
    mostValuable: watchListRows.slice(0, 5).map((item, i) => ({
      account_id: `fallback-${i}`,
      account: item.handle.replace("@", ""),
      list_type: "following",
      value_score: 30 + i * 7,
      avg_follow_back_time_hours: 10 + i * 2,
      engagement_score: 1.2 + i * 0.25,
    })),
    reports: {
      daily: {
        scope: "daily",
        period_label: "Daily report",
        kpis: { follow_back_rate: 0.58, average_follow_back_time_hours: 22, success_rate: 0.61 },
        follower_growth: sampleLineChartData,
        engagement_timeline: sampleBarChartData,
        most_active_accounts: [],
        most_valuable_accounts: [],
      },
      weekly: {
        scope: "weekly",
        period_label: "Weekly report",
        kpis: { follow_back_rate: 0.58, average_follow_back_time_hours: 22, success_rate: 0.61 },
        follower_growth: sampleLineChartData,
        engagement_timeline: sampleBarChartData,
        most_active_accounts: [],
        most_valuable_accounts: [],
      },
      monthly: {
        scope: "monthly",
        period_label: "Monthly report",
        kpis: { follow_back_rate: 0.58, average_follow_back_time_hours: 22, success_rate: 0.61 },
        follower_growth: sampleLineChartData,
        engagement_timeline: sampleBarChartData,
        most_active_accounts: [],
        most_valuable_accounts: [],
      },
    },
  };
}

export function useAnalyticsDashboard(filters: AnalyticsFilters) {
  return useQuery({
    queryKey: queryKeys.analytics.dashboard(filters),
    queryFn: async (): Promise<AnalyticsDashboardPayload> => {
      try {
        const [kpis, followerGrowth, engagementTimeline, mostActive, mostValuable, daily, weekly, monthly] =
          await Promise.all([
            analyticsService.getSummary(filters),
            analyticsService.getFollowerGrowth(filters),
            analyticsService.getEngagementTimeline(filters),
            analyticsService.getMostActive(filters),
            analyticsService.getMostValuable(filters),
            analyticsService.getReport("daily", { ...filters, granularity: "daily" }),
            analyticsService.getReport("weekly", { ...filters, granularity: "weekly" }),
            analyticsService.getReport("monthly", { ...filters, granularity: "monthly" }),
          ]);

        return {
          kpis,
          followerGrowth,
          engagementTimeline,
          mostActive,
          mostValuable,
          reports: { daily, weekly, monthly },
        };
      } catch {
        return fallbackAnalyticsPayload();
      }
    },
    initialData: fallbackAnalyticsPayload(),
  });
}

export function mapKpisToStats(kpis: { follow_back_rate: number; average_follow_back_time_hours: number; success_rate: number }) {
  return [
    {
      title: "Follow Back Rate",
      value: toPercent(kpis.follow_back_rate),
      change: "+2.3%",
      trend: "up" as const,
      detail: "Followers following back",
    },
    {
      title: "Avg Follow Back Time",
      value: `${kpis.average_follow_back_time_hours.toFixed(1)}h`,
      change: "-1.1h",
      trend: "up" as const,
      detail: "Average delay to follow back",
    },
    {
      title: "Success Rate",
      value: toPercent(kpis.success_rate),
      change: "+1.8%",
      trend: "up" as const,
      detail: "Campaign success ratio",
    },
  ];
}
