import { NextRequest, NextResponse } from "next/server";

import { env } from "@/config/env";

function apiBase() {
  return env.apiBaseUrl.replace(/\/$/, "");
}

export async function GET(request: NextRequest) {
  const redirect = request.nextUrl.searchParams.get("redirect") ?? "/";
  const appUserId = request.nextUrl.searchParams.get("app_user_id");
  const params = new URLSearchParams();
  if (appUserId) params.set("app_user_id", appUserId);
  if (redirect) params.set("redirect", redirect);

  const backendUrl = `${apiBase()}/auth/x/login${params.toString() ? `?${params}` : ""}`;
  return NextResponse.redirect(backendUrl);
}
