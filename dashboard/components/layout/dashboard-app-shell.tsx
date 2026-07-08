"use client";

import * as React from "react";
import { usePathname } from "next/navigation";

import { Dialog, DialogContent } from "@/components/ui/dialog";
import { Sidebar } from "@/components/layout/sidebar";
import { Navbar } from "@/components/layout/navbar";
import { TopNavigation } from "@/components/layout/top-navigation";
import { cn } from "@/lib/utils";
import {
  sampleNotifications,
  sampleSidebarItems,
  sampleTopNavItems,
  sampleUser,
  type NavigationItem,
} from "@/lib/mock-data";

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
      sampleSidebarItems.map((item) => ({
        ...item,
        active: getActive(item.href, pathname),
      })),
    [pathname]
  );

  const topNavItems: NavigationItem[] = React.useMemo(
    () =>
      sampleTopNavItems.map((item) => ({
        ...item,
        active: getActive(item.href, pathname),
      })),
    [pathname]
  );

  return (
    <div className="min-h-screen">
      <div className="mx-auto max-w-[1280px] space-y-4 p-4">
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-[20rem_1fr]">
          <div className="hidden lg:block">
            <Sidebar
              items={sidebarItems}
              collapsed={sidebarCollapsed}
              onToggleCollapse={() => setSidebarCollapsed((v) => !v)}
              footer={
                <div className="space-y-2 rounded-xl border border-glass-border bg-background/40 p-3">
                  <p className="text-xs font-medium text-foreground">Status</p>
                  <p className="text-xs text-muted-foreground">
                    UI ready with simulated loading and transitions.
                  </p>
                </div>
              }
            />
          </div>

          <div className="space-y-4">
            <Navbar
              title={pageTitle}
              subtitle={pageSubtitle}
              user={sampleUser}
              notifications={sampleNotifications}
              onMenuClick={() => setMobileOpen(true)}
              searchPlaceholder="Search within this page"
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
            "max-w-[90vw] overflow-hidden p-2",
            "bg-glass/20 backdrop-blur-xl shadow-glow"
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
