import { AUTH_COOKIE, AUTH_STORAGE_KEYS } from "@/constants/auth";

function isBrowser() {
  return typeof window !== "undefined";
}

export function setSessionCookie(rememberMe: boolean) {
  if (!isBrowser()) return;
  const maxAge = rememberMe ? AUTH_COOKIE.maxAgeRemember : AUTH_COOKIE.maxAgeSession;
  document.cookie = `${AUTH_COOKIE.name}=1; path=/; max-age=${maxAge}; SameSite=Lax`;
}

export function clearSessionCookie() {
  if (!isBrowser()) return;
  document.cookie = `${AUTH_COOKIE.name}=; path=/; max-age=0; SameSite=Lax`;
}

export function hasSessionCookie() {
  if (!isBrowser()) return false;
  return document.cookie.split(";").some((part) => part.trim().startsWith(`${AUTH_COOKIE.name}=`));
}

export function getStoredToken(): string | null {
  if (!isBrowser()) return null;
  const remember = localStorage.getItem(AUTH_STORAGE_KEYS.remember) === "true";
  const storage = remember ? localStorage : sessionStorage;
  return storage.getItem(AUTH_STORAGE_KEYS.token);
}

export function setStoredToken(token: string, rememberMe: boolean) {
  if (!isBrowser()) return;
  localStorage.setItem(AUTH_STORAGE_KEYS.remember, rememberMe ? "true" : "false");
  const storage = rememberMe ? localStorage : sessionStorage;
  const other = rememberMe ? sessionStorage : localStorage;
  storage.setItem(AUTH_STORAGE_KEYS.token, token);
  other.removeItem(AUTH_STORAGE_KEYS.token);
  setSessionCookie(rememberMe);
}

export function clearStoredToken() {
  if (!isBrowser()) return;
  localStorage.removeItem(AUTH_STORAGE_KEYS.token);
  sessionStorage.removeItem(AUTH_STORAGE_KEYS.token);
  localStorage.removeItem(AUTH_STORAGE_KEYS.remember);
  clearSessionCookie();
}

export function decodeJwtPayload(token: string): { sub: string; exp: number; role: string } | null {
  try {
    const [, payload] = token.split(".");
    if (!payload) return null;
    const json = atob(payload.replace(/-/g, "+").replace(/_/g, "/"));
    return JSON.parse(json) as { sub: string; exp: number; role: string };
  } catch {
    return null;
  }
}

export function isTokenExpired(token: string) {
  const decoded = decodeJwtPayload(token);
  if (!decoded?.exp) return true;
  return decoded.exp * 1000 <= Date.now();
}
