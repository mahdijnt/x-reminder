"use client";

import * as React from "react";

import { AUTH_ROUTES } from "@/constants/auth";
import {
  clearStoredToken,
  getStoredToken,
  isTokenExpired,
  setStoredToken,
} from "@/lib/auth/token-manager";
import { authService } from "@/services/auth.service";
import type { AuthSession, AuthUser, LoginCredentials, RegisterPayload } from "@/types/auth";

type AuthStatus = "loading" | "authenticated" | "unauthenticated";

type AuthContextValue = {
  status: AuthStatus;
  user: AuthUser | null;
  session: AuthSession | null;
  isAuthenticated: boolean;
  sessionExpired: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (payload: RegisterPayload) => Promise<void>;
  logout: () => Promise<void>;
  refreshSession: () => Promise<void>;
  dismissSessionExpired: () => void;
  hasRole: (role: AuthUser["role"] | AuthUser["role"][]) => boolean;
};

const AuthContext = React.createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [status, setStatus] = React.useState<AuthStatus>("loading");
  const [user, setUser] = React.useState<AuthUser | null>(null);
  const [session, setSession] = React.useState<AuthSession | null>(null);
  const [sessionExpired, setSessionExpired] = React.useState(false);

  const applySession = React.useCallback((next: AuthSession | null, rememberMe = false) => {
    if (!next) {
      clearStoredToken();
      setSession(null);
      setUser(null);
      setStatus("unauthenticated");
      return;
    }
    setStoredToken(next.accessToken, rememberMe);
    setSession(next);
    setUser(next.user);
    setStatus("authenticated");
    setSessionExpired(false);
  }, []);

  const refreshSession = React.useCallback(async () => {
    const token = getStoredToken();
    if (!token || isTokenExpired(token)) {
      clearStoredToken();
      setSession(null);
      setUser(null);
      setStatus("unauthenticated");
      if (token) setSessionExpired(true);
      return;
    }

    try {
      const me = await authService.me({
        headers: { Authorization: `Bearer ${token}` },
      });
      setUser(me);
      setSession({ accessToken: token, expiresAt: Date.now() + 1000 * 60 * 60, user: me });
      setStatus("authenticated");
    } catch {
      clearStoredToken();
      setSession(null);
      setUser(null);
      setStatus("unauthenticated");
      setSessionExpired(true);
    }
  }, []);

  React.useEffect(() => {
    void refreshSession();
  }, [refreshSession]);

  const login = React.useCallback(
    async (credentials: LoginCredentials) => {
      const next = await authService.login(credentials);
      applySession(next, Boolean(credentials.rememberMe));
    },
    [applySession]
  );

  const register = React.useCallback(
    async (payload: RegisterPayload) => {
      const next = await authService.register(payload);
      applySession(next, true);
    },
    [applySession]
  );

  const logout = React.useCallback(async () => {
    try {
      await authService.logout();
    } catch {
      // ignore logout failures
    }
    applySession(null);
    if (typeof window !== "undefined") {
      window.location.href = AUTH_ROUTES.login;
    }
  }, [applySession]);

  const hasRole = React.useCallback(
    (role: AuthUser["role"] | AuthUser["role"][]) => {
      if (!user) return false;
      const roles = Array.isArray(role) ? role : [role];
      return roles.includes(user.role);
    },
    [user]
  );

  const value = React.useMemo<AuthContextValue>(
    () => ({
      status,
      user,
      session,
      isAuthenticated: status === "authenticated" && Boolean(user),
      sessionExpired,
      login,
      register,
      logout,
      refreshSession,
      dismissSessionExpired: () => setSessionExpired(false),
      hasRole,
    }),
    [hasRole, login, logout, refreshSession, register, session, sessionExpired, status, user]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuthContext() {
  const ctx = React.useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuthContext must be used within AuthProvider");
  }
  return ctx;
}

