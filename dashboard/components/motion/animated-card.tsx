"use client";

import * as React from "react";
import { m, useReducedMotion, type HTMLMotionProps } from "framer-motion";

import { cn } from "@/lib/utils";

type AnimatedCardProps = HTMLMotionProps<"div"> & {
  delay?: number;
  hover?: boolean;
};

export function AnimatedCard({
  children,
  className,
  delay = 0,
  hover = true,
  ...props
}: AnimatedCardProps) {
  const reducedMotion = useReducedMotion();

  return (
    <m.div
      initial={reducedMotion ? { opacity: 0 } : { opacity: 0, y: 22, scale: 0.985 }}
      animate={reducedMotion ? { opacity: 1 } : { opacity: 1, y: 0, scale: 1 }}
      whileHover={
        hover && !reducedMotion
          ? { y: -6, scale: 1.01, transition: { duration: 0.22, ease: "easeOut" } }
          : undefined
      }
      transition={{ duration: reducedMotion ? 0.16 : 0.42, delay, ease: [0.22, 1, 0.36, 1] }}
      className={cn("transform-gpu will-change-transform", className)}
      {...props}
    >
      {children}
    </m.div>
  );
}
