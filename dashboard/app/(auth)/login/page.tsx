"use client";

import * as React from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";

import { AuthLayoutShell } from "@/components/auth/auth-layout-shell";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { AUTH_ROUTES } from "@/constants/auth";
import { useAuth } from "@/hooks/use-auth";

export default function LoginPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { login, isAuthenticated, status } = useAuth();
  const [email, setEmail] = React.useState("user@example.com");
  const [password, setPassword] = React.useState("user123");
  const [rememberMe, setRememberMe] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);
  const [pending, setPending] = React.useState(false);

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

  return (
    <AuthLayoutShell title="Welcome back" subtitle="Sign in to access your dashboard workspace.">
      <form className="space-y-4" onSubmit={onSubmit}>
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
        <p className="rounded-lg border border-white/10 bg-white/5 p-3 text-xs text-muted-foreground">
          Demo: user@example.com / user123 or admin@example.com / admin123
        </p>
      </form>
    </AuthLayoutShell>
  );
}
