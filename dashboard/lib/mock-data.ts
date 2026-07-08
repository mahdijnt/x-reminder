import * as React from "react";

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

export const sampleSidebarItems: NavigationItem[] = [
  { title: "Dashboard", href: "/", active: true },
  { title: "Watch Lists", href: "/watch-lists", badge: "New" },
  { title: "Following", href: "/following" },
  { title: "Follow Targets", href: "/follow-targets" },
  { title: "Mutual Followers", href: "/mutual-followers" },
  { title: "Target Achieved", href: "/target-achieved" },
  { title: "Analytics", href: "/analytics" },
  { title: "Settings", href: "/settings" },
  { title: "Profile", href: "/profile" },
  { title: "Notifications", href: "/notifications" },
];

export const sampleTopNavItems: NavigationItem[] = [
  { title: "Dashboard", href: "/", active: true },
  { title: "Watch Lists", href: "/watch-lists" },
  { title: "Following", href: "/following" },
  { title: "Follow Targets", href: "/follow-targets" },
  { title: "Mutual", href: "/mutual-followers" },
  { title: "Achieved", href: "/target-achieved" },
  { title: "Analytics", href: "/analytics" },
  { title: "Settings", href: "/settings" },
  { title: "Profile", href: "/profile" },
  { title: "Alerts", href: "/notifications" },
];

export const sampleBreadcrumbs: BreadcrumbItem[] = [
  { label: "Workspace", href: "#" },
  { label: "Insights", href: "#" },
  { label: "Overview" },
];

export const sampleNotifications: NotificationItem[] = [
  {
    id: "1",
    title: "Scheduled digest ready",
    description: "A fresh weekly summary is available to review.",
    time: "2m ago",
    unread: true,
    tone: "default",
  },
  {
    id: "2",
    title: "Goal reached",
    description: "One of your tracked benchmarks crossed its target threshold.",
    time: "18m ago",
    tone: "success",
  },
  {
    id: "3",
    title: "Attention needed",
    description: "A monitored segment is trending lower than the trailing average.",
    time: "1h ago",
    tone: "warning",
  },
  {
    id: "4",
    title: "New mutual found",
    description: "Two accounts began following each other. Consider following back.",
    time: "3h ago",
    unread: true,
    tone: "default",
  },
];

export const sampleUser: UserProfile = {
  name: "Ava Collins",
  email: "ava@example.com",
  role: "Product Lead",
  initials: "AC",
};

export const sampleStats: StatDatum[] = [
  {
    title: "Qualified signals",
    value: "12.4K",
    change: "+14.2%",
    trend: "up",
    detail: "Compared with the previous period.",
  },
  {
    title: "Response velocity",
    value: "2.8h",
    change: "-6.1%",
    trend: "down",
    detail: "Median time to acknowledge tracked events.",
  },
  {
    title: "Retention health",
    value: "91%",
    change: "+1.9%",
    trend: "up",
    detail: "Stable across the last three reporting windows.",
  },
];

export const sampleProgressItems: ProgressDatum[] = [
  { label: "Roadmap completion", value: 68, description: "12 of 18 planned tasks are finished." },
  { label: "Dataset coverage", value: 84, description: "Most benchmark groups have fresh sample inputs." },
  { label: "Review readiness", value: 52, description: "Visual QA is halfway complete for the current set." },
];

export const sampleTableRows: SampleRow[] = [
  { id: "row-1", name: "North Star Campaign", status: "Active", owner: "Ava Collins", amount: "$24,300" },
  { id: "row-2", name: "Creator Pulse", status: "Draft", owner: "Marcus Lee", amount: "$8,120" },
  { id: "row-3", name: "Partner Watch", status: "Paused", owner: "Nina Shah", amount: "$5,970" },
];

export const sampleLineChartData: ChartPoint[] = [
  { label: "Mon", value: 22 },
  { label: "Tue", value: 34 },
  { label: "Wed", value: 30 },
  { label: "Thu", value: 48 },
  { label: "Fri", value: 44 },
  { label: "Sat", value: 52 },
  { label: "Sun", value: 46 },
];

export const sampleBarChartData: ChartPoint[] = [
  { label: "Q1", value: 28 },
  { label: "Q2", value: 44 },
  { label: "Q3", value: 36 },
  { label: "Q4", value: 58 },
];

export const sampleDonutChartData: ChartPoint[] = [
  { label: "Organic", value: 46 },
  { label: "Partner", value: 28 },
  { label: "Paid", value: 16 },
  { label: "Other", value: 10 },
];

export const watchListRows: WatchListRow[] = [
  {
    id: "wl-1",
    name: "North Star Campaign",
    handle: "@northstar",
    status: "Active",
    owner: "Ava Collins",
    signals: "12.4K signals",
    lastCheck: "2m ago",
  },
  {
    id: "wl-2",
    name: "Creator Pulse",
    handle: "@creatorpulse",
    status: "Draft",
    owner: "Marcus Lee",
    signals: "4.8K signals",
    lastCheck: "38m ago",
  },
  {
    id: "wl-3",
    name: "Partner Watch",
    handle: "@partnerwatch",
    status: "Paused",
    owner: "Nina Shah",
    signals: "1.2K signals",
    lastCheck: "3h ago",
  },
  {
    id: "wl-4",
    name: "Hyperlocal Labs",
    handle: "@hyperlocal",
    status: "Active",
    owner: "Ava Collins",
    signals: "7.1K signals",
    lastCheck: "11m ago",
  },
  {
    id: "wl-5",
    name: "Signal Garden",
    handle: "@signalgarden",
    status: "Draft",
    owner: "Marcus Lee",
    signals: "2.9K signals",
    lastCheck: "1h ago",
  },
  {
    id: "wl-6",
    name: "Aurora Community",
    handle: "@auroracommunity",
    status: "Active",
    owner: "Nina Shah",
    signals: "5.6K signals",
    lastCheck: "24m ago",
  },
];

export const followingRows: FollowingRow[] = [
  {
    id: "fg-1",
    name: "Creator Pulse",
    handle: "@creatorpulse",
    since: "May 14",
    notificationState: "Enabled",
    engagement: "Rising",
  },
  {
    id: "fg-2",
    name: "North Star Campaign",
    handle: "@northstar",
    since: "Jun 02",
    notificationState: "Muted",
    engagement: "Stable",
  },
  {
    id: "fg-3",
    name: "Hyperlocal Labs",
    handle: "@hyperlocal",
    since: "Apr 28",
    notificationState: "Enabled",
    engagement: "Accelerating",
  },
  {
    id: "fg-4",
    name: "Signal Garden",
    handle: "@signalgarden",
    since: "May 30",
    notificationState: "Pending",
    engagement: "Warm",
  },
  {
    id: "fg-5",
    name: "Partner Watch",
    handle: "@partnerwatch",
    since: "Mar 21",
    notificationState: "Muted",
    engagement: "Low",
  },
  {
    id: "fg-6",
    name: "Aurora Community",
    handle: "@auroracommunity",
    since: "Jun 18",
    notificationState: "Enabled",
    engagement: "High",
  },
];

export const followTargetRows: FollowTargetRow[] = [
  {
    id: "ft-1",
    name: "Lattice Makers",
    handle: "@latticemakers",
    matchScore: 92,
    strategy: "Lookalike",
    status: "Qualified",
  },
  {
    id: "ft-2",
    name: "Metric Atlas",
    handle: "@metricatlas",
    matchScore: 78,
    strategy: "Engagement",
    status: "Review",
  },
  {
    id: "ft-3",
    name: "Thread Compass",
    handle: "@threadcompass",
    matchScore: 65,
    strategy: "Keyword",
    status: "Scheduled",
  },
  {
    id: "ft-4",
    name: "Prism Collective",
    handle: "@prismcollective",
    matchScore: 86,
    strategy: "Lookalike",
    status: "Qualified",
  },
  {
    id: "ft-5",
    name: "Pulse Orchard",
    handle: "@pulseorchard",
    matchScore: 71,
    strategy: "Engagement",
    status: "Review",
  },
  {
    id: "ft-6",
    name: "Echo Harbor",
    handle: "@echoharbor",
    matchScore: 59,
    strategy: "Keyword",
    status: "Scheduled",
  },
];

export const mutualFollowerRows: MutualFollowerRow[] = [
  {
    id: "mf-1",
    name: "Prism Collective",
    handle: "@prismcollective",
    mutualSince: "Jun 09",
    lastMention: "14m ago",
    tier: "Gold",
  },
  {
    id: "mf-2",
    name: "Lattice Makers",
    handle: "@latticemakers",
    mutualSince: "May 27",
    lastMention: "2h ago",
    tier: "Standard",
  },
  {
    id: "mf-3",
    name: "Thread Compass",
    handle: "@threadcompass",
    mutualSince: "Jun 21",
    lastMention: "46m ago",
    tier: "Standard",
  },
  {
    id: "mf-4",
    name: "Pulse Orchard",
    handle: "@pulseorchard",
    mutualSince: "May 19",
    lastMention: "9m ago",
    tier: "Gold",
  },
  {
    id: "mf-5",
    name: "Metric Atlas",
    handle: "@metricatlas",
    mutualSince: "Jun 02",
    lastMention: "1h ago",
    tier: "Standard",
  },
  {
    id: "mf-6",
    name: "Echo Harbor",
    handle: "@echoharbor",
    mutualSince: "Jun 25",
    lastMention: "23m ago",
    tier: "Gold",
  },
];

export const targetAchievedRows: TargetAchievedRow[] = [
  {
    id: "ta-1",
    targetName: "Increase qualified signals",
    handle: "@northstar",
    achievedAt: "Jun 30",
    metric: "+14.2%",
    status: "Achieved",
  },
  {
    id: "ta-2",
    targetName: "Accelerate response velocity",
    handle: "@hyperlocal",
    achievedAt: "Jun 21",
    metric: "-6.1%",
    status: "Achieved",
  },
  {
    id: "ta-3",
    targetName: "Improve retention health",
    handle: "@auroracommunity",
    achievedAt: "Jun 18",
    metric: "+1.9%",
    status: "Achieved",
  },
  {
    id: "ta-4",
    targetName: "Stabilize partner engagement",
    handle: "@partnerwatch",
    achievedAt: "May 29",
    metric: "+3.4%",
    status: "Archived",
  },
  {
    id: "ta-5",
    targetName: "Boost roadmap readiness",
    handle: "@signalgarden",
    achievedAt: "May 12",
    metric: "52% -> 68%",
    status: "Archived",
  },
];

export const analyticsTopTweetRows: AnalyticsTweetRow[] = [
  {
    id: "tw-1",
    tweet: "Roadmap signals are converging fast.",
    metric: "+28%",
    impact: "High reach",
    state: "High",
  },
  {
    id: "tw-2",
    tweet: "Engagement loops improve when response latency drops.",
    metric: "-6%",
    impact: "Strong retention",
    state: "Medium",
  },
  {
    id: "tw-3",
    tweet: "Partner signals are stabilizing week over week.",
    metric: "+12%",
    impact: "Steady momentum",
    state: "Medium",
  },
  {
    id: "tw-4",
    tweet: "New targets scheduled for next sprint.",
    metric: "+7%",
    impact: "Early wins",
    state: "Low",
  },
  {
    id: "tw-5",
    tweet: "Organic discovery improved across cohorts.",
    metric: "+19%",
    impact: "Quality growth",
    state: "High",
  },
  {
    id: "tw-6",
    tweet: "Keyword strategies show cleaner intent signals.",
    metric: "+9%",
    impact: "Better leads",
    state: "Medium",
  },
  {
    id: "tw-7",
    tweet: "Lookalike segments are overshooting thresholds.",
    metric: "+23%",
    impact: "Top cohort",
    state: "High",
  },
  {
    id: "tw-8",
    tweet: "Paid cohorts remain volatile.",
    metric: "-2%",
    impact: "Needs QA",
    state: "Low",
  },
];
