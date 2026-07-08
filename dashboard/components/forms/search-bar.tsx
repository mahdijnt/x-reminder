"use client";

import * as React from "react";
import { Search } from "lucide-react";

import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";

export interface SearchBarProps extends React.InputHTMLAttributes<HTMLInputElement> {
  containerClassName?: string;
}

export const SearchBar = React.forwardRef<HTMLInputElement, SearchBarProps>(
  ({ className, containerClassName, placeholder = "Search...", ...props }, ref) => (
    <div
      className={cn(
        "relative flex w-full items-center rounded-xl border border-input bg-background/60 shadow-sm backdrop-blur-sm",
        containerClassName
      )}
    >
      <Search className="pointer-events-none absolute left-3 h-4 w-4 text-muted-foreground" />
      <Input ref={ref} className={cn("border-0 bg-transparent pl-9 shadow-none", className)} placeholder={placeholder} {...props} />
    </div>
  )
);
SearchBar.displayName = "SearchBar";
