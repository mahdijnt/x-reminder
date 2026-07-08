import { useQuery } from "@tanstack/react-query";
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
