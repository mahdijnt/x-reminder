"use client";

import { cn } from "@/lib/utils";

export interface AnimatedLinesProps {
  className?: string;
}

const lines = [
  { width: "32%", left: "6%", top: "18%", delay: "0s", duration: "14s" },
  { width: "26%", left: "54%", top: "24%", delay: "-3s", duration: "18s" },
  { width: "34%", left: "18%", top: "56%", delay: "-8s", duration: "16s" },
  { width: "24%", left: "64%", top: "68%", delay: "-5s", duration: "20s" },
];

export function AnimatedLines({ className }: AnimatedLinesProps) {
  return (
    <div
      aria-hidden="true"
      className={cn(
        "pointer-events-none absolute inset-0 overflow-hidden opacity-80",
        className
      )}
    >
      {lines.map((line, index) => (
        <span
          key={index}
          className="animated-light-line"
          style={{
            width: line.width,
            left: line.left,
            top: line.top,
            animationDelay: line.delay,
            animationDuration: line.duration,
          }}
        />
      ))}
    </div>
  );
}
