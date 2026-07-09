import { env } from "@/config/env";
import { ApiError, type ApiClientConfig, type ApiRequestOptions } from "@/lib/api/types";

const defaultConfig: ApiClientConfig = {
  baseUrl: env.apiBaseUrl,
  useMock: false,
  mockDelayMs: 0,
};

type ApiEnvelope<T> = {
  success?: boolean;
  message?: string;
  code?: string;
  data?: T;
};

function buildUrl(baseUrl: string, path: string, params?: ApiRequestOptions["params"]) {
  const url = new URL(path.startsWith("http") ? path : `${baseUrl.replace(/\/$/, "")}/${path.replace(/^\//, "")}`);
  if (params) {
    for (const [key, value] of Object.entries(params)) {
      if (value !== undefined) url.searchParams.set(key, String(value));
    }
  }
  return url.toString();
}

function unwrapResponse<T>(payload: T | ApiEnvelope<T>): T {
  if (payload && typeof payload === "object" && "data" in (payload as Record<string, unknown>)) {
    const envelope = payload as ApiEnvelope<T>;
    if (envelope.data !== undefined) return envelope.data;
  }
  return payload as T;
}

function appUserIdFromToken(token: string | null): string | null {
  if (!token) return null;
  try {
    const [, payload] = token.split(".");
    if (!payload) return null;
    const json = atob(payload.replace(/-/g, "+").replace(/_/g, "/"));
    const parsed = JSON.parse(json) as { sub?: string };
    return parsed.sub ?? null;
  } catch {
    return null;
  }
}

function getStoredAuthToken(): string | null {
  if (typeof window === "undefined") return null;
  const sessionToken = window.sessionStorage.getItem("xr_auth_token");
  const localToken = window.localStorage.getItem("xr_auth_token");
  return sessionToken || localToken;
}

function getRuntimeHeaders(existing?: HeadersInit): HeadersInit {
  if (typeof window === "undefined") return existing ?? {};

  const token = getStoredAuthToken();
  const appUserId = appUserIdFromToken(token) ?? "web-user";

  const headers: Record<string, string> = {
    "X-App-User-Id": appUserId,
  };
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  return {
    ...headers,
    ...existing,
  };
}

async function request<T>(
  method: string,
  path: string,
  body?: unknown,
  options?: ApiRequestOptions,
  config: ApiClientConfig = defaultConfig
): Promise<T> {
  const url = buildUrl(config.baseUrl, path, options?.params);
  const response = await fetch(url, {
    method,
    headers: {
      "Content-Type": "application/json",
      ...getRuntimeHeaders(options?.headers),
    },
    credentials: "include",
    body: body !== undefined ? JSON.stringify(body) : undefined,
    signal: options?.signal,
  });

  if (!response.ok) {
    let message = `Request failed with status ${response.status}`;
    try {
      const payload = (await response.json()) as { message?: string; detail?: string };
      if (payload?.message) message = payload.message;
      if (payload?.detail) message = payload.detail;
    } catch {
      // ignore parse errors
    }
    throw new ApiError({ message, status: response.status });
  }

  if (response.status === 204) return undefined as T;
  const json = (await response.json()) as T | ApiEnvelope<T>;
  return unwrapResponse(json);
}

export const apiClient = {
  get<T>(path: string, options?: ApiRequestOptions) {
    return request<T>("GET", path, undefined, options);
  },
  post<T>(path: string, body?: unknown, options?: ApiRequestOptions) {
    return request<T>("POST", path, body, options);
  },
  put<T>(path: string, body?: unknown, options?: ApiRequestOptions) {
    return request<T>("PUT", path, body, options);
  },
  delete<T>(path: string, options?: ApiRequestOptions) {
    return request<T>("DELETE", path, undefined, options);
  },
};
