import type { AuthRole } from "@/types/auth";

export const AUTH_STORAGE_KEYS = {
  token: "xr_auth_token",
  session: "xr_auth_session",
  remember: "xr_auth_remember",
} as const;

export const AUTH_COOKIE = {
  name: "xr_session",
  maxAgeSession: 60 * 60 * 8,
  maxAgeRemember: 60 * 60 * 24 * 30,
} as const;

export const AUTH_ROUTES = {
  login: "/login",
  register: "/register",
  forgotPassword: "/forgot-password",
  resetPassword: "/reset-password",
  unauthorized: "/unauthorized",
  xLogin: "/api/auth/x/login",
  xCallback: "/api/auth/x/callback",
} as const;

export const PUBLIC_AUTH_PATHS = Object.values(AUTH_ROUTES);

export type SeedAuthAccount = {
  id: string;
  email: string;
  password: string;
  name: string;
  role: AuthRole;
  initials: string;
};
