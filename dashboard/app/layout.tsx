import type { ReactNode } from "react";

import "./globals.css";

import { DashboardAppShell } from "@/components/layout/dashboard-app-shell";
import { MotionProvider } from "@/components/motion/motion-provider";
import { AppProviders } from "@/providers/app-providers";
import { appConfig } from "@/config/app.config";

export const metadata = {
  title: appConfig.name,
  description: appConfig.description,
};

export default function RootLayout({
  children,
}: {
  children: ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-background text-foreground antialiased">
        <AppProviders>
          <MotionProvider>
            <DashboardAppShell>{children}</DashboardAppShell>
          </MotionProvider>
        </AppProviders>
      </body>
    </html>
  );
}
