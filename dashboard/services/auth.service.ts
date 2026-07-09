import { apiClient } from "@/lib/api/api-client";
import type { ApiRequestOptions } from "@/lib/api/types";
import type {
  AuthSession,
  AuthUser,
  ForgotPasswordPayload,
  LoginCredentials,
  RegisterPayload,
  ResetPasswordPayload,
} from "@/types/auth";

export const authService = {
  login(credentials: LoginCredentials) {
    return apiClient.post<AuthSession>("auth/login", credentials);
  },
  register(payload: RegisterPayload) {
    return apiClient.post<AuthSession>("auth/register", payload);
  },
  forgotPassword(payload: ForgotPasswordPayload) {
    return apiClient.post<{ ok: true }>("auth/forgot-password", payload);
  },
  resetPassword(payload: ResetPasswordPayload) {
    return apiClient.post<{ ok: true }>("auth/reset-password", payload);
  },
  me(options?: ApiRequestOptions) {
    return apiClient.get<AuthUser>("auth/me", options);
  },
  logout() {
    return apiClient.post<{ ok: true }>("auth/logout");
  },
};
