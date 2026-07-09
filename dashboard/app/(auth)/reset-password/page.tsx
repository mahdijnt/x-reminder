"use client";

import * as React from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";

import { AuthLayoutShell } from "@/components/auth/auth-layout-shell";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { AUTH_ROUTES } from "@/constants/auth";
import { authService } from "@/services/auth.service";

export default function ResetPasswordPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [token, setToken] = React.useState(searchParams.get("token") || "");
  const [password, setPassword] = React.useState("");
  const [error, setError] = React.useState<string | null>(null);
  const [message, setMessage] = React.useState<string | null>(null);
  const [pending, setPending] = React.useState(false);

  async function onSubmit(event: React.FormEvent) {
    event.preventDefault();
    setPending(true);
    setError(null);
    try {
      await authService.resetPassword({ token, password });
      setMessage("Password updated. You can sign in with your new password.");
      setTimeout(() => router.push(AUTH_ROUTES.login), 800);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to reset password");
    } finally {
      setPending(false);
    }
  }

  return (
    <AuthLayoutShell title="Reset password" subtitle="Enter your reset token and a new password.">
      <form className="space-y-4" onSubmit={onSubmit}>
        <div className="space-y-2">
          <label className="text-sm font-medium" htmlFor="token">Reset token</label>
          <Input id="token" value={token} onChange={(e) => setToken(e.target.value)} required />
        </div>
        <div className="space-y-2">
          <label className="text-sm font-medium" htmlFor="password">New password</label>
          <Input id="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
        </div>
        {error ? <p className="text-sm text-destructive">{error}</p> : null}
        {message ? <p className="text-sm text-muted-foreground">{message}</p> : null}
        <Button type="submit" className="w-full" disabled={pending}>{pending ? "Updating..." : "Update password"}</Button>
        <p className="text-center text-sm text-muted-foreground">
          <Link href={AUTH_ROUTES.login} className="text-primary hover:underline">Back to sign in</Link>
        </p>
      </form>
    </AuthLayoutShell>
  );
}
