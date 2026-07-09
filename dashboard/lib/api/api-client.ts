import { env } from "@/config/env";
import { ApiError, type ApiClientConfig, type ApiRequestOptions } from "@/lib/api/types";

export type MockHandler = (path: string, options?: ApiRequestOptions & { method?: string; body?: unknown }) => Promise<unknown>;

let mockHandler: MockHandler | null = null;

export function registerMockHandler(handler: MockHandler) {
  mockHandler = handler;
}

const defaultConfig: ApiClientConfig = {
  baseUrl: env.apiBaseUrl,
  useMock: env.useMockApi,
  mockDelayMs: 0,
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

async function delay(ms: number) {
  if (ms <= 0) return;
  await new Promise((resolve) => setTimeout(resolve, ms));
}

async function request<T>(
  method: string,
  path: string,
  body?: unknown,
  options?: ApiRequestOptions,
  config: ApiClientConfig = defaultConfig
): Promise<T> {
  if (config.useMock) {
    if (!mockHandler) {
      throw new ApiError({ message: "Mock handler not registered", code: "MOCK_NOT_CONFIGURED" });
    }
    await delay(config.mockDelayMs ?? 0);
    try {
      return (await mockHandler(path, { ...options, method, body })) as T;
    } catch (err) {
      if (err instanceof ApiError) throw err;
      throw new ApiError({ message: err instanceof Error ? err.message : "Mock request failed" });
    }
  }

  const url = buildUrl(config.baseUrl, path, options?.params);
  const response = await fetch(url, {
    method,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    body: body !== undefined ? JSON.stringify(body) : undefined,
    signal: options?.signal,
  });

  if (!response.ok) {
    let message = `Request failed with status ${response.status}`;
    try {
      const payload = (await response.json()) as { message?: string };
      if (payload?.message) message = payload.message;
    } catch {
      // ignore parse errors
    }
    throw new ApiError({ message, status: response.status });
  }

  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
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
