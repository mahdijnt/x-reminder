import type { AuthUser } from "@/types/auth";
import type { UserProfile } from "@/types";

export function authUserToProfile(user: AuthUser): UserProfile {
  return {
    name: user.name,
    email: user.email,
    role: user.role,
    initials: user.initials,
  };
}
