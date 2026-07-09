"use client";

import { AlertTriangle } from "lucide-react";

import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/use-auth";

export function SessionExpiredBanner() {
  const { sessionExpired, dismissSessionExpired, logout } = useAuth();

  if (!sessionExpired) return null;

  return (
    <div className="fixed inset-x-0 top-0 z-toast px-4 pt-4">
      <div className="mx-auto flex max-w-3xl items-center justify-between gap-3 rounded-xl border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-sm text-foreground backdrop-blur-md">
        <div className="flex items-center gap-2">
          <AlertTriangle className="h-4 w-4 text-amber-300" />
          <span>Your session expired. Sign in again to continue.</span>
        </div>
        <div className="flex items-center gap-2">
          <Button size="sm" variant="outline" onClick={dismissSessionExpired}>
            Dismiss
          </Button>
          <Button
            size="sm"
            onClick={async () => {
              dismissSessionExpired();
              await logout();
            }}
          >
            Sign in
          </Button>
        </div>
      </div>
    </div>
  );
}
