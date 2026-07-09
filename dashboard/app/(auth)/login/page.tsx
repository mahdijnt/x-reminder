"use client";

import * as React from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";

import { AuthLayoutShell } from "@/components/auth/auth-layout-shell";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { AUTH_ROUTES } from "@/constants/auth";
import { useAuth } from "@/hooks/use-auth";
import { setStoredToken } from "@/lib/auth/token-manager";

export default function LoginPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { login, isAuthenticated, status, refreshSession } = useAuth();
  const [email, setEmail] = React.useState("");
  const [password, setPassword] = React.useState("");
  const [rememberMe, setRememberMe] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);
  const [pending, setPending] = React.useState(false);

  React.useEffect(() => {
    const xAuth = searchParams.get("x_auth");
    if (xAuth === "success") {
      const cookieToken = document.cookie
        .split(";")
        .map((part) => part.trim())
        .find((part) => part.startsWith("xr_auth_token="))
        ?.split("=")[1];
      if (cookieToken) {
        setStoredToken(decodeURIComponent(cookieToken), true);
      }
      void refreshSession().then(() => {
        router.replace(searchParams.get("redirect") || "/");
      });
      return;
    }
    if (xAuth === "error") {
      setError("X authorization failed. Please try again.");
    }
  }, [refreshSession, router, searchParams]);

  React.useEffect(() => {
    if (status === "authenticated" && isAuthenticated) {
      router.replace(searchParams.get("redirect") || "/");
    }
  }, [isAuthenticated, router, searchParams, status]);

  async function onSubmit(event: React.FormEvent) {
    event.preventDefault();
    setPending(true);
    setError(null);
    try {
      await login({ email, password, rememberMe });
      router.replace(searchParams.get("redirect") || "/");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to sign in");
    } finally {
      setPending(false);
    }
  }

  function continueWithX() {
    const redirect = searchParams.get("redirect") || "/";
    const url = new URL(AUTH_ROUTES.xLogin, window.location.origin);
    url.searchParams.set("redirect", redirect);
    window.location.href = url.toString();
  }

  return (
    <AuthLayoutShell title="Welcome back" subtitle="Sign in to access your dashboard workspace.">
      <div className="space-y-4">
        <Button type="button" variant="outline" className="w-full" onClick={continueWithX}>
          Continue with X
        </Button>
        <div className="relative text-center text-xs text-muted-foreground">
          <span className="bg-background px-2">or sign in with email</span>
        </div>
      </div>
      <form className="mt-4 space-y-4" onSubmit={onSubmit}>
        <div className="space-y-2">
          <label className="text-sm font-medium" htmlFor="email">Email</label>
          <Input id="email" type="email" autoComplete="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        </div>
        <div className="space-y-2">
          <label className="text-sm font-medium" htmlFor="password">Password</label>
          <Input id="password" type="password" autoComplete="current-password" value={password} onChange={(e) => setPassword(e.target.value)} required />
        </div>
        <div className="flex items-center justify-between gap-3 text-sm">
          <label className="inline-flex items-center gap-2 text-muted-foreground">
            <input type="checkbox" checked={rememberMe} onChange={(e) => setRememberMe(e.target.checked)} className="rounded border-input" />
            Remember me
          </label>
          <Link href={AUTH_ROUTES.forgotPassword} className="text-primary hover:underline">Forgot password?</Link>
        </div>
        {error ? <p className="text-sm text-destructive">{error}</p> : null}
        <Button type="submit" className="w-full" disabled={pending}>{pending ? "Signing in…" : "Sign in"}</Button>
        <p className="text-center text-sm text-muted-foreground">
          No account? <Link href={AUTH_ROUTES.register} className="text-primary hover:underline">Create one</Link>
        </p>
      </form>
    </AuthLayoutShell>
  );
}
