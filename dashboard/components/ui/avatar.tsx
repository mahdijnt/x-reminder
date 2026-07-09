"use client";

import Image, { type ImageProps } from "next/image";
import * as React from "react";

import { cn } from "@/lib/utils";

function getInitials(name?: string, fallback?: string) {
  if (fallback) return fallback.slice(0, 2).toUpperCase();
  if (!name) return "UI";

  const initials = name
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0])
    .join("");

  return initials.toUpperCase() || "UI";
}

const Avatar = React.forwardRef<
  HTMLSpanElement,
  React.HTMLAttributes<HTMLSpanElement>
>(({ className, ...props }, ref) => (
  <span
    ref={ref}
    className={cn(
      "relative flex h-10 w-10 shrink-0 overflow-hidden rounded-full border border-glass-border bg-secondary/40 text-foreground shadow-sm",
      className
    )}
    {...props}
  />
));
Avatar.displayName = "Avatar";

type AvatarImageProps = Omit<ImageProps, "alt"> & {
  alt?: string;
  className?: string;
};

function AvatarImage({ className, alt = "Avatar", sizes = "40px", ...props }: AvatarImageProps) {
  return (
    <Image
      alt={alt}
      sizes={sizes}
      className={cn("aspect-square h-full w-full object-cover", className)}
      {...props}
    />
  );
}

export interface AvatarFallbackProps
  extends React.HTMLAttributes<HTMLSpanElement> {
  name?: string;
  fallback?: string;
}

const AvatarFallback = React.forwardRef<HTMLSpanElement, AvatarFallbackProps>(
  ({ className, children, name, fallback, ...props }, ref) => (
    <span
      ref={ref}
      className={cn(
        "flex h-full w-full items-center justify-center bg-gradient-to-br from-primary/30 to-accent/20 text-xs font-semibold uppercase text-foreground",
        className
      )}
      {...props}
    >
      {children ?? getInitials(name, fallback)}
    </span>
  )
);
AvatarFallback.displayName = "AvatarFallback";

export { Avatar, AvatarFallback, AvatarImage };
