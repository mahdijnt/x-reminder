export const queryKeys = {
  navigation: {
    all: ["navigation"] as const,
    sidebar: ["navigation", "sidebar"] as const,
    topNav: ["navigation", "topNav"] as const,
    breadcrumbs: ["navigation", "breadcrumbs"] as const,
  },
  user: { current: ["user", "current"] as const },
  notifications: { all: ["notifications"] as const },
  dashboard: { overview: ["dashboard", "overview"] as const },
  watchLists: { all: ["watchLists"] as const },
  following: { all: ["following"] as const },
  followTargets: { all: ["followTargets"] as const },
  mutualFollowers: { all: ["mutualFollowers"] as const },
  targetAchieved: { all: ["targetAchieved"] as const },
  analytics: {
    overview: ["analytics", "overview"] as const,
    dashboard: (filters: unknown) => ["analytics", "dashboard", filters] as const,
  },
} as const;
