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

export const sampleSidebarItems: NavigationItem[] = [
  { title: "Overview", href: "#", active: true },
  { title: "Analytics", href: "#" },
  { title: "Reports", href: "#", badge: "New" },
  { title: "Automations", href: "#" },
  { title: "Settings", href: "#" },
];

export const sampleTopNavItems: NavigationItem[] = [
  { title: "Summary", href: "#", active: true },
  { title: "Performance", href: "#" },
  { title: "Audience", href: "#" },
  { title: "Exports", href: "#" },
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
