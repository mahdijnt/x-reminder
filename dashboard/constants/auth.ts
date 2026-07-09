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
} as const;

export const PUBLIC_AUTH_PATHS = Object.values(AUTH_ROUTES);

export type MockAuthAccount = {
  id: string;
  email: string;
  password: string;
  name: string;
  role: AuthRole;
  initials: string;
};

export const MOCK_AUTH_ACCOUNTS: MockAuthAccount[] = [
  {
    id: "usr_admin",
    email: "admin@example.com",
    password: "admin123",
    name: "Ava Admin",
    role: "admin",
    initials: "AA",
  },
  {
    id: "usr_member",
    email: "user@example.com",
    password: "user123",
    name: "Uma User",
    role: "user",
    initials: "UU",
  },
];

export const MOCK_RESET_TOKEN = "mock-reset-token";
