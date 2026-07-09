"use client";

import Link from "next/link";

import { AuthLayoutShell } from "@/components/auth/auth-layout-shell";
import { Button } from "@/components/ui/button";
import { AUTH_ROUTES } from "@/constants/auth";
import { routes } from "@/constants/routes";

export default function UnauthorizedPage() {
  return (
    <AuthLayoutShell title="Unauthorized" subtitle="You do not have permission to view this page.">
      <div className="space-y-4">
        <p className="text-sm text-muted-foreground">
          This route is protected by role checks. Switch to an admin mock account or return to the dashboard.
        </p>
        <div className="flex flex-col gap-2 sm:flex-row">
          <Button asChild className="flex-1">
            <Link href={routes.home}>Go to dashboard</Link>
          </Button>
          <Button asChild variant="outline" className="flex-1">
            <Link href={AUTH_ROUTES.login}>Sign in</Link>
          </Button>
        </div>
      </div>
    </AuthLayoutShell>
  );
}
