import { NextRequest, NextResponse } from "next/server";

import { env } from "@/config/env";
import { AUTH_COOKIE } from "@/constants/auth";

type ApiEnvelope<T> = {
  success: boolean;
  data: T;
};

type OAuthCallbackData = {
  connected: boolean;
  x_user_id?: string;
  username?: string;
  app_user_id?: string;
};

function apiBase() {
  return env.apiBaseUrl.replace(/\/$/, "");
}

export async function GET(request: NextRequest) {
  const code = request.nextUrl.searchParams.get("code");
  const state = request.nextUrl.searchParams.get("state");
  const redirect = request.cookies.get("xr_oauth_redirect")?.value ?? "/";

  if (!code || !state) {
    return NextResponse.redirect(new URL("/login?x_auth=error", request.url));
  }

  const callbackUrl = new URL(`${apiBase()}/x/oauth/callback`);
  callbackUrl.searchParams.set("code", code);
  callbackUrl.searchParams.set("state", state);

  const response = await fetch(callbackUrl.toString(), { method: "GET", cache: "no-store" });
  if (!response.ok) {
    return NextResponse.redirect(new URL("/login?x_auth=error", request.url));
  }

  const payload = (await response.json()) as ApiEnvelope<OAuthCallbackData>;
  if (!payload.success || !payload.data?.app_user_id) {
    return NextResponse.redirect(new URL("/login?x_auth=error", request.url));
  }

  const sessionUrl = new URL(`${apiBase()}/auth/x/session`);
  sessionUrl.searchParams.set("app_user_id", payload.data.app_user_id);
  if (payload.data.username) sessionUrl.searchParams.set("username", payload.data.username);

  const sessionResponse = await fetch(sessionUrl.toString(), { method: "POST", cache: "no-store" });
  if (!sessionResponse.ok) {
    return NextResponse.redirect(new URL("/login?x_auth=error", request.url));
  }

  const sessionPayload = (await sessionResponse.json()) as ApiEnvelope<{
    accessToken: string;
    expiresAt: number;
    user: Record<string, unknown>;
  }>;

  const destination = new URL(redirect.startsWith("/") ? redirect : "/", request.url);
  const next = NextResponse.redirect(destination);
  const maxAge = AUTH_COOKIE.maxAgeRemember;

  next.cookies.set(AUTH_COOKIE.name, "1", {
    path: "/",
    maxAge,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
  });

  next.cookies.set("xr_auth_token", sessionPayload.data.accessToken, {
    path: "/",
    maxAge,
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
  });

  return next;
}
