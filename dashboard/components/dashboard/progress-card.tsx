"use client";

import { AnimatedCard } from "@/components/motion/animated-card";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";

export interface ProgressCardProps {
  title: string;
  value: number;
  description?: string;
  label?: string;
}

export function ProgressCard({
  title,
  value,
  description,
  label = "Completion",
}: ProgressCardProps) {
  return (
    <AnimatedCard>
      <Card className="card-premium rounded-[1.5rem] border-white/10">
        <CardHeader>
          <CardDescription>{label}</CardDescription>
          <CardTitle>{title}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Progress value={value} showLabel />
          {description ? <p className="text-sm text-muted-foreground">{description}</p> : null}
        </CardContent>
      </Card>
    </AnimatedCard>
  );
}
