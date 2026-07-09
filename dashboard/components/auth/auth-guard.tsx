"use client";

import * as React from "react";
import { useRouter } from "next/navigation";

import { AUTH_ROUTES } from "@/constants/auth";
import { useAuth } from "@/hooks/use-auth";

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { status, isAuthenticated } = useAuth();

  React.useEffect(() => {
    if (status === "loading") return;
    if (!isAuthenticated) {
      router.replace(`${AUTH_ROUTES.login}?redirect=${encodeURIComponent(window.location.pathname)}`);
    }
  }, [isAuthenticated, router, status]);

  if (status === "loading") {
    return (
      <div className="flex min-h-[40vh] items-center justify-center">
        <p className="text-sm text-muted-foreground">Loading session…</p>
      </div>
    );
  }

  if (!isAuthenticated) return null;

  return <>{children}</>;
}


