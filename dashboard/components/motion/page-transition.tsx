"use client";

import * as React from "react";
import { AnimatePresence, m, useReducedMotion } from "framer-motion";
import { usePathname } from "next/navigation";

import { cn } from "@/lib/utils";

export function PageTransition({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
}) {
  const pathname = usePathname();
  const reducedMotion = useReducedMotion();

  return (
    <AnimatePresence mode="wait" initial={false}>
      <m.div
        key={pathname}
        className={cn("will-change-transform", className)}
        initial={reducedMotion ? { opacity: 0 } : { opacity: 0, y: 18, scale: 0.985 }}
        animate={reducedMotion ? { opacity: 1 } : { opacity: 1, y: 0, scale: 1 }}
        exit={reducedMotion ? { opacity: 0 } : { opacity: 0, y: -10, scale: 0.995 }}
        transition={{ duration: reducedMotion ? 0.16 : 0.42, ease: [0.22, 1, 0.36, 1] }}
      >
        {children}
      </m.div>
    </AnimatePresence>
  );
}
