"use client";

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
    <Card>
      <CardHeader>
        <CardDescription>{label}</CardDescription>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <Progress value={value} showLabel />
        {description ? <p className="text-sm text-muted-foreground">{description}</p> : null}
      </CardContent>
    </Card>
  );
}
