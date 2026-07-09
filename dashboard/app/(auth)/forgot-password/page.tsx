"use client";

import * as React from "react";
import Link from "next/link";

import { AuthLayoutShell } from "@/components/auth/auth-layout-shell";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { MOCK_RESET_TOKEN } from "@/constants/auth";
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
      await authService.forgotPassword({ email });
      setMessage(`Reset link generated. Use token ${MOCK_RESET_TOKEN} on the reset page.`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to process request");
    } finally {
      setPending(false);
    }
  }

  return (
    <AuthLayoutShell title="Forgot password" subtitle="We will send a mock reset token for this demo environment.">
      <form className="space-y-4" onSubmit={onSubmit}>
        <div className="space-y-2">
          <label className="text-sm font-medium" htmlFor="email">Email</label>
          <Input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        </div>
        {error ? <p className="text-sm text-destructive">{error}</p> : null}
        {message ? <p className="text-sm text-muted-foreground">{message}</p> : null}
        <Button type="submit" className="w-full" disabled={pending}>{pending ? "Sending…" : "Send reset link"}</Button>
        <p className="text-center text-sm text-muted-foreground">
          <Link href={AUTH_ROUTES.login} className="text-primary hover:underline">Back to sign in</Link>
        </p>
      </form>
    </AuthLayoutShell>
  );
}
