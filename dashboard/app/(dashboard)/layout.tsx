import type { ReactNode } from "react";

import { AuthGuard } from "@/components/auth/auth-guard";
import { DashboardAppShell } from "@/components/layout/dashboard-app-shell";
import { MotionProvider } from "@/components/motion/motion-provider";

export default function DashboardGroupLayout({ children }: { children: ReactNode }) {
  return (
    <AuthGuard>
      <MotionProvider>
        <DashboardAppShell>{children}</DashboardAppShell>
      </MotionProvider>
    </AuthGuard>
  );
}
