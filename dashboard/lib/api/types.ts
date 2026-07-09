export type ApiErrorShape = {
  message: string;
  code?: string;
  status?: number;
  details?: unknown;
};

export class ApiError extends Error {
  readonly code?: string;
  readonly status?: number;
  readonly details?: unknown;

  constructor(shape: ApiErrorShape) {
    super(shape.message);
    this.name = "ApiError";
    this.code = shape.code;
    this.status = shape.status;
    this.details = shape.details;
  }
}

export type ApiRequestOptions = {
  params?: Record<string, string | number | boolean | undefined>;
  headers?: Record<string, string>;
  signal?: AbortSignal;
};

export type ApiClientConfig = {
  baseUrl: string;
  useMock: boolean;
  mockDelayMs?: number;
};
