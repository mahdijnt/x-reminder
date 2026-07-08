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
  const { data: user } = useCurrentUser();
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
    <div className="relative min-h-screen overflow-hidden">
      <AuroraBackground />
      <GradientMesh className="opacity-60" />
      <AnimatedLines className="mix-blend-screen" />

      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,rgba(8,12,28,0.15),transparent_28%),linear-gradient(180deg,rgba(7,10,20,0.12),rgba(7,10,20,0.4))]" />

      <div className="relative mx-auto max-w-[1280px] space-y-4 p-4 md:p-5 lg:p-6">
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-[minmax(16rem,19rem)_1fr] lg:gap-5">
          <m.div
            layout
            transition={{ type: "spring", stiffness: 220, damping: 24, mass: 0.8 }}
            className="hidden lg:block"
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

          <div className="space-y-4 lg:space-y-5">
            <Navbar
              title={pageTitle}
              subtitle={pageSubtitle}
              user={user!}
              notifications={notifications}
              onMenuClick={() => setMobileOpen(true)}
              searchPlaceholder="Search within this page"
              onMarkAllNotificationsRead={markAllReadInMenu}
            />

            <TopNavigation items={topNavItems} />

            <main className="pb-8" aria-label="Page content">
              {children}
            </main>
          </div>
        </div>
      </div>

      <Dialog open={mobileOpen} onOpenChange={setMobileOpen}>
        <DialogContent
          className={cn(
            "max-w-[90vw] overflow-hidden border-white/10 p-2",
            "bg-glass/20 shadow-glow backdrop-blur-2xl"
          )}
        >
          <div className="p-1">
            <Sidebar items={sidebarItems} collapsed={false} />
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
