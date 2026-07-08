import type { ReactNode } from "react";

import "./globals.css";

import { DashboardAppShell } from "@/components/layout/dashboard-app-shell";

export const metadata = {
  title: "X Engagement Intelligence Manager",
  description: "Next.js dashboard UI (fake data only).",
};

export default function RootLayout({
  children,
}: {
  children: ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-background text-foreground antialiased">
        <DashboardAppShell>{children}</DashboardAppShell>
      </body>
    </html>
  );
}
