"use client";

import * as React from "react";
import { usePathname } from "next/navigation";
import { m } from "framer-motion";

import { Dialog, DialogContent } from "@/components/ui/dialog";
import { Sidebar } from "@/components/layout/sidebar";
import { Navbar } from "@/components/layout/navbar";
import { TopNavigation } from "@/components/layout/top-navigation";
import { AuroraBackground } from "@/components/effects/aurora-background";
import { GradientMesh } from "@/components/effects/gradient-mesh";
import { AnimatedLines } from "@/components/effects/animated-lines";
import { cn } from "@/lib/utils";
import type { NavigationItem } from "@/types";
import {
  useCurrentUser,
  useNotificationsQuery,
  useSidebarNavigation,
  useTopNavigation,
} from "@/hooks/use-api-data";
import { useAuth } from "@/hooks/use-auth";
import { authUserToProfile } from "@/lib/auth/map-user";
import { useNotificationUiStore } from "@/stores/notification-store";

function getActive(href: string, pathname: string) {
  if (!href) return false;
  if (href === "/") return pathname === "/";
  return pathname === href || pathname.startsWith(`${href}/`);
}

export function DashboardAppShell({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = React.useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = React.useState(false);

  const { data: sidebarData } = useSidebarNavigation();
  const { data: topNavData } = useTopNavigation();
  const { user: authUser } = useAuth();
  const { data: apiUser } = useCurrentUser();
  const user = authUser ? authUserToProfile(authUser) : apiUser;
  const { data: notificationsQuery } = useNotificationsQuery();
  const menuItems = useNotificationUiStore((s) => s.menuItems);
  const markAllReadInMenu = useNotificationUiStore((s) => s.markAllReadInMenu);

  const notifications = menuItems ?? notificationsQuery ?? [];

  const pageTitle = React.useMemo(() => {
    if (!pathname) return "Dashboard";
    if (pathname === "/") return "Dashboard";
    const slug = pathname.replace(/\/$/, "").split("/").pop() ?? "dashboard";
    const label = slug
      .split("-")
      .filter(Boolean)
      .map((p) => p[0]?.toUpperCase() + p.slice(1))
      .join(" ");
    return label;
  }, [pathname]);

  const pageSubtitle = "Premium UI shell (fake data, no backend).";

  const sidebarItems: NavigationItem[] = React.useMemo(
    () =>
      (sidebarData ?? []).map((item) => ({
        ...item,
        active: getActive(item.href, pathname),
      })),
    [pathname, sidebarData]
  );

  const topNavItems: NavigationItem[] = React.useMemo(
    () =>
      (topNavData ?? []).map((item) => ({
        ...item,
        active: getActive(item.href, pathname),
      })),
    [pathname, topNavData]
  );

  return (
    <div className="relative isolate min-h-screen min-h-[100dvh] overflow-x-hidden">
      <AuroraBackground className="z-aurora" />
      <GradientMesh className="z-aurora opacity-60" />
      <AnimatedLines className="z-aurora mix-blend-screen" />

      <div className="pointer-events-none absolute inset-0 z-aurora bg-[radial-gradient(circle_at_top,rgba(8,12,28,0.15),transparent_28%),linear-gradient(180deg,rgba(7,10,20,0.12),rgba(7,10,20,0.4))]" />

      <div className="relative z-page-content mx-auto max-w-[1280px] space-y-4 px-[max(1rem,var(--safe-area-left))] pb-[max(2rem,var(--safe-area-bottom))] pt-[max(1rem,var(--safe-area-top))] md:px-5 md:pb-5 md:pt-5 lg:px-6 lg:pb-6 lg:pt-6">
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-[minmax(16rem,19rem)_1fr] lg:gap-5">
          <m.div
            layout
            transition={{ type: "spring", stiffness: 220, damping: 24, mass: 0.8 }}
            className="relative z-sidebar hidden lg:block"
          >
            <Sidebar
              items={sidebarItems}
              collapsed={sidebarCollapsed}
              onToggleCollapse={() => setSidebarCollapsed((v) => !v)}
              footer={
                <div className="glass-panel space-y-2 rounded-2xl p-3">
                  <p className="text-xs font-medium text-foreground">Status</p>
                  <p className="text-xs text-muted-foreground">
                    UI ready with simulated loading and transitions.
                  </p>
                </div>
              }
            />
          </m.div>

          <div className="min-w-0 space-y-4 lg:space-y-5">
            <Navbar
              title={pageTitle}
              subtitle={pageSubtitle}
              user={user ?? apiUser!}
              notifications={notifications}
              onMenuClick={() => setMobileOpen(true)}
              mobileNavOpen={mobileOpen}
              searchPlaceholder="Search within this page"
              onMarkAllNotificationsRead={markAllReadInMenu}
            />

            <TopNavigation items={topNavItems} />

            <main id="main-content" className="pb-8 outline-none" aria-label="Page content" tabIndex={-1}>
              {children}
            </main>
          </div>
        </div>
      </div>

      <Dialog open={mobileOpen} onOpenChange={setMobileOpen}>
        <DialogContent
          className={cn(
            "max-h-[min(92dvh,calc(100dvh-var(--safe-area-top)-var(--safe-area-bottom)-0.5rem))] w-[min(20rem,calc(100vw-var(--safe-area-left)-var(--safe-area-right)-1rem))] max-w-[90vw] overflow-hidden overflow-y-auto border-white/10 p-2",
            "bg-glass/20 shadow-glow backdrop-blur-2xl"
          )}
        >
          <div className="p-1">
            <Sidebar items={sidebarItems} collapsed={false} onNavigate={() => setMobileOpen(false)} className="min-h-0 max-h-none" />
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
