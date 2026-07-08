"use client";

import * as React from "react";
import { LazyMotion, MotionConfig, domAnimation, useReducedMotion } from "framer-motion";

export function MotionProvider({ children }: { children: React.ReactNode }) {
  const reducedMotion = useReducedMotion();

  return (
    <LazyMotion features={domAnimation} strict>
      <MotionConfig reducedMotion={reducedMotion ? "always" : "user"}>
        {children}
      </MotionConfig>
    </LazyMotion>
  );
}
