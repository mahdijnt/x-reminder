"use client";

import * as React from "react";

import { AnimatedCard } from "@/components/motion/animated-card";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { cn } from "@/lib/utils";

export interface SectionCardProps extends React.HTMLAttributes<HTMLDivElement> {
  title: string;
  description?: string;
  action?: React.ReactNode;
  contentClassName?: string;
}

export function SectionCard({
  title,
  description,
  action,
  children,
  className,
  contentClassName,
  ...props
}: SectionCardProps) {
  return (
    <AnimatedCard hover={false}>
      <Card className={cn("card-premium rounded-[1.5rem] border-white/10", className)} {...props}>
        <CardHeader className="flex flex-row items-start justify-between gap-4 space-y-0">
          <div className="space-y-1">
            <CardTitle>{title}</CardTitle>
            {description ? <CardDescription>{description}</CardDescription> : null}
          </div>
          {action}
        </CardHeader>
        <CardContent className={contentClassName}>{children}</CardContent>
      </Card>
    </AnimatedCard>
  );
}
