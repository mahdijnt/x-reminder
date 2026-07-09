import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

import { AUTH_COOKIE, AUTH_ROUTES, PUBLIC_AUTH_PATHS } from "@/constants/auth";

const AUTH_PATH_SET = new Set<string>(PUBLIC_AUTH_PATHS);

function isAuthPath(pathname: string) {
  return AUTH_PATH_SET.has(pathname);
}

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  if (pathname.startsWith("/api/auth")) {
    return NextResponse.next();
  }

  const hasSession = request.cookies.has(AUTH_COOKIE.name);

  if (isAuthPath(pathname)) {
    if (hasSession && (pathname === AUTH_ROUTES.login || pathname === AUTH_ROUTES.register)) {
      return NextResponse.redirect(new URL("/", request.url));
    }
    return NextResponse.next();
  }

  if (!hasSession) {
    const loginUrl = new URL(AUTH_ROUTES.login, request.url);
    if (pathname !== "/") {
      loginUrl.searchParams.set("redirect", pathname);
    }
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)"],
};
