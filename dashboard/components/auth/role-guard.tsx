"use client";

import * as React from "react";
import { useRouter } from "next/navigation";

import { AUTH_ROUTES } from "@/constants/auth";
import { useAuth } from "@/hooks/use-auth";

export function RoleGuard({
  allow,
  children,
}: {
  allow: "admin" | "user" | Array<"admin" | "user">;
  children: React.ReactNode;
}) {
  const router = useRouter();
  const { status, hasRole } = useAuth();

  React.useEffect(() => {
    if (status !== "authenticated") return;
    if (!hasRole(allow)) {
      router.replace(AUTH_ROUTES.unauthorized);
    }
  }, [allow, hasRole, router, status]);

  if (status === "loading") return null;
  if (!hasRole(allow)) return null;
  return <>{children}</>;
}
