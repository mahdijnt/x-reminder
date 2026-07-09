"use client";

import * as React from "react";
import Link from "next/link";

import { AuthLayoutShell } from "@/components/auth/auth-layout-shell";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { AUTH_ROUTES } from "@/constants/auth";
import { authService } from "@/services/auth.service";

export default function ForgotPasswordPage() {
  const [email, setEmail] = React.useState("");
  const [message, setMessage] = React.useState<string | null>(null);
  const [error, setError] = React.useState<string | null>(null);
  const [pending, setPending] = React.useState(false);

  async function onSubmit(event: React.FormEvent) {
    event.preventDefault();
    setPending(true);
    setError(null);
    setMessage(null);
    try {
      const response = await authService.forgotPassword({ email });
      const token = (response as { token?: string }).token;
      setMessage(token ? `Reset token generated: ${token}` : "Reset instructions generated. Check your inbox.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to process request");
    } finally {
      setPending(false);
    }
  }

  return (
    <AuthLayoutShell title="Forgot password" subtitle="We will generate reset instructions for your account.">
      <form className="space-y-4" onSubmit={onSubmit}>
        <div className="space-y-2">
          <label className="text-sm font-medium" htmlFor="email">Email</label>
          <Input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        </div>
        {error ? <p className="text-sm text-destructive">{error}</p> : null}
        {message ? <p className="text-sm text-muted-foreground">{message}</p> : null}
        <Button type="submit" className="w-full" disabled={pending}>{pending ? "Sending..." : "Send reset link"}</Button>
        <p className="text-center text-sm text-muted-foreground">
          <Link href={AUTH_ROUTES.login} className="text-primary hover:underline">Back to sign in</Link>
        </p>
      </form>
    </AuthLayoutShell>
  );
}
