export type AuthRole = "user" | "admin";

export type AuthUser = {
  id: string;
  name: string;
  email: string;
  role: AuthRole;
  initials: string;
  x_user_id?: string;
  x_username?: string;
  display_name?: string;
  bio?: string;
  avatar_url?: string;
  followers_count?: number;
  following_count?: number;
  verified?: boolean;
  created_at?: string;
};

export type AuthSession = {
  accessToken: string;
  expiresAt: number;
  user: AuthUser;
};

export type LoginCredentials = {
  email: string;
  password: string;
  rememberMe?: boolean;
};

export type RegisterPayload = {
  name: string;
  email: string;
  password: string;
};

export type ForgotPasswordPayload = {
  email: string;
};

export type ResetPasswordPayload = {
  token: string;
  password: string;
};

export type AuthApiResponse<T> = {
  data: T;
  message?: string;
};
