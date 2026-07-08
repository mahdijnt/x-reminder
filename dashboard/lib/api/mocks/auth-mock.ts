import {
  MOCK_AUTH_ACCOUNTS,
  MOCK_RESET_TOKEN,
} from "@/constants/auth";
import { createMockJwt } from "@/lib/auth/token-manager";
import type {
  AuthSession,
  AuthUser,
  ForgotPasswordPayload,
  LoginCredentials,
  RegisterPayload,
  ResetPasswordPayload,
} from "@/types/auth";

const registeredUsers = [...MOCK_AUTH_ACCOUNTS];

function toAuthUser(account: (typeof MOCK_AUTH_ACCOUNTS)[number]): AuthUser {
  return {
    id: account.id,
    name: account.name,
    email: account.email,
    role: account.role,
    initials: account.initials,
  };
}

function buildSession(account: (typeof MOCK_AUTH_ACCOUNTS)[number], rememberMe = false): AuthSession {
  const accessToken = createMockJwt(account.id, account.role, rememberMe);
  const expiresAt = Date.now() + (rememberMe ? 1000 * 60 * 60 * 24 * 30 : 1000 * 60 * 60 * 8);
  return {
    accessToken,
    expiresAt,
    user: toAuthUser(account),
  };
}

export function mockAuthLogin(payload: LoginCredentials): AuthSession {
  const account = registeredUsers.find(
    (user) => user.email.toLowerCase() === payload.email.toLowerCase() && user.password === payload.password
  );
  if (!account) {
    throw new Error("Invalid email or password");
  }
  return buildSession(account, Boolean(payload.rememberMe));
}

export function mockAuthRegister(payload: RegisterPayload): AuthSession {
  const exists = registeredUsers.some((user) => user.email.toLowerCase() === payload.email.toLowerCase());
  if (exists) {
    throw new Error("An account with this email already exists");
  }
  const account = {
    id: `usr_${Date.now()}`,
    email: payload.email,
    password: payload.password,
    name: payload.name,
    role: "user" as const,
    initials: payload.name
      .split(" ")
      .map((part) => part[0])
      .join("")
      .slice(0, 2)
      .toUpperCase(),
  };
  registeredUsers.push(account);
  return buildSession(account, true);
}

export function mockAuthForgotPassword(payload: ForgotPasswordPayload) {
  const exists = registeredUsers.some((user) => user.email.toLowerCase() === payload.email.toLowerCase());
  if (!exists) {
    throw new Error("No account found for that email");
  }
  return { ok: true as const, token: MOCK_RESET_TOKEN };
}

export function mockAuthResetPassword(payload: ResetPasswordPayload) {
  if (payload.token !== MOCK_RESET_TOKEN) {
    throw new Error("Invalid or expired reset token");
  }
  return { ok: true as const };
}

export function mockAuthMe(token?: string): AuthUser {
  if (!token) throw new Error("Unauthorized");
  const userId = token.split(".")[1];
  if (!userId) throw new Error("Unauthorized");
  let decoded: { sub?: string } | null = null;
  try {
    decoded = JSON.parse(atob(userId.replace(/-/g, "+").replace(/_/g, "/")));
  } catch {
    throw new Error("Unauthorized");
  }
  const account = registeredUsers.find((user) => user.id === decoded?.sub);
  if (!account) throw new Error("Unauthorized");
  return toAuthUser(account);
}

export function mockAuthLogout() {
  return { ok: true as const };
}
