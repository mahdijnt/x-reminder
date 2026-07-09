import type * as React from "react";

export type NavigationItem = {
  title: string;
  href: string;
  badge?: string;
  active?: boolean;
};

export type BreadcrumbItem = {
  label: string;
  href?: string;
};

export type NotificationItem = {
  id: string;
  title: string;
  description: string;
  time: string;
  unread?: boolean;
  tone?: "default" | "success" | "warning" | "danger";
};

export type UserProfile = {
  name: string;
  email: string;
  role: string;
  initials: string;
  x_username?: string;
  bio?: string;
  avatar_url?: string;
  followers_count?: number;
  following_count?: number;
};

export type StatDatum = {
  title: string;
  value: string;
  change: string;
  trend: "up" | "down" | "neutral";
  detail: string;
};

export type ProgressDatum = {
  label: string;
  value: number;
  description: string;
};

export type TableColumn<T> = {
  key: keyof T | string;
  header: string;
  align?: "left" | "right" | "center";
  render?: (row: T, index: number) => React.ReactNode;
};

export type SampleRow = {
  id: string;
  name: string;
  status: "Active" | "Draft" | "Paused";
  owner: string;
  amount: string;
};

export type ChartPoint = {
  label: string;
  value: number;
};

export type WatchListRow = {
  id: string;
  name: string;
  handle: string;
  status: "Active" | "Draft" | "Paused";
  owner: string;
  signals: string;
  lastCheck: string;
};

export type FollowingRow = {
  id: string;
  name: string;
  handle: string;
  since: string;
  notificationState: "Enabled" | "Muted" | "Pending";
  engagement: string;
};

export type FollowTargetRow = {
  id: string;
  name: string;
  handle: string;
  matchScore: number;
  strategy: "Lookalike" | "Engagement" | "Keyword";
  status: "Qualified" | "Review" | "Scheduled";
};

export type MutualFollowerRow = {
  id: string;
  name: string;
  handle: string;
  mutualSince: string;
  lastMention: string;
  tier: "Gold" | "Standard";
};

export type TargetAchievedRow = {
  id: string;
  targetName: string;
  handle: string;
  achievedAt: string;
  metric: string;
  status: "Achieved" | "Archived";
};

export type AnalyticsTweetRow = {
  id: string;
  tweet: string;
  metric: string;
  impact: string;
  state: "High" | "Medium" | "Low";
};

export type AnalyticsGranularity = "daily" | "weekly" | "monthly";

export type AnalyticsFilters = {
  start_date?: string;
  end_date?: string;
  list_type?: string;
  account?: string;
  granularity?: AnalyticsGranularity;
};

export type AnalyticsKpis = {
  follow_back_rate: number;
  average_follow_back_time_hours: number;
  success_rate: number;
};

export type AnalyticsSeriesPoint = {
  label: string;
  value: number;
};

export type ActiveAccountMetric = {
  account_id: string;
  account: string;
  list_type: string;
  follows: number;
  follow_backs: number;
  engagements: number;
};

export type ValuableAccountMetric = {
  account_id: string;
  account: string;
  list_type: string;
  value_score: number;
  avg_follow_back_time_hours: number;
  engagement_score: number;
};

export type AnalyticsReport = {
  scope: "daily" | "weekly" | "monthly";
  period_label: string;
  kpis: AnalyticsKpis;
  follower_growth: AnalyticsSeriesPoint[];
  engagement_timeline: AnalyticsSeriesPoint[];
  most_active_accounts: ActiveAccountMetric[];
  most_valuable_accounts: ValuableAccountMetric[];
};

export type AnalyticsExport = {
  format: "json" | "csv";
  filename: string;
  content_type: string;
  content: string;
};

export type AnalyticsDashboardPayload = {
  kpis: AnalyticsKpis;
  followerGrowth: AnalyticsSeriesPoint[];
  engagementTimeline: AnalyticsSeriesPoint[];
  mostActive: ActiveAccountMetric[];
  mostValuable: ValuableAccountMetric[];
  reports: {
    daily: AnalyticsReport;
    weekly: AnalyticsReport;
    monthly: AnalyticsReport;
  };
};
