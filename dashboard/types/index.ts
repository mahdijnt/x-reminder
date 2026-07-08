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