"use client";

import { useRouter } from "next/navigation";
import { CreditCard, LogOut, Settings, Sparkles } from "lucide-react";

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { routes } from "@/constants/routes";
import { useAuth } from "@/hooks/use-auth";
import type { UserProfile } from "@/types";

export interface UserMenuAction {
  label: string;
  onSelect?: () => void;
  href?: string;
}

export interface UserMenuProps {
  user: UserProfile;
  imageSrc?: string;
  actions?: UserMenuAction[];
}

const defaultActions: UserMenuAction[] = [
  { label: "Profile", href: routes.profile },
  { label: "Billing" },
  { label: "Preferences", href: routes.settings },
  { label: "Sign out" },
];

const actionIcons = [Sparkles, CreditCard, Settings, LogOut];

export function UserMenu({ user, imageSrc, actions = defaultActions }: UserMenuProps) {
  const router = useRouter();
  const { logout } = useAuth();

  return (
    <DropdownMenu>
      <DropdownMenuTrigger className="rounded-full">
        <Avatar className="h-10 w-10 cursor-pointer">
          {imageSrc ? <AvatarImage src={imageSrc} alt={user.name} /> : null}
          <AvatarFallback name={user.name} fallback={user.initials} />
        </Avatar>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-64">
        <DropdownMenuLabel>
          <div className="space-y-1">
            <p className="text-sm font-medium text-foreground">{user.name}</p>
            <p className="text-xs text-muted-foreground">{user.email}</p>
            <p className="text-xs text-muted-foreground">{user.role}</p>
          </div>
        </DropdownMenuLabel>
        <DropdownMenuSeparator />
        {actions.map((action, index) => {
          const Icon = actionIcons[index] ?? Sparkles;
          const isSignOut = action.label === "Sign out";
          return (
            <DropdownMenuItem
              key={action.label}
              onClick={() => {
                if (isSignOut) {
                  void logout();
                  return;
                }
                if (action.href) {
                  router.push(action.href);
                  return;
                }
                action.onSelect?.();
              }}
            >
              <Icon className="h-4 w-4 text-muted-foreground" />
              {action.label}
            </DropdownMenuItem>
          );
        })}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
